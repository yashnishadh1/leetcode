import datetime as dt
import json
import shutil
from collections import Counter

import pytest

import automation as a
import mark_revision as mr


@pytest.fixture(autouse=True)
def _no_real_toolchain(monkeypatch):
    monkeypatch.setenv("COMPILE_CHECK", "0")


def make_problem(slug, difficulty="Easy", qid="1", title=None):
    return {"titleSlug": slug, "difficulty": difficulty, "frontendQuestionId": qid, "title": title or slug}


def test_python_validation():
    assert a.validate_code("python", "class Solution:\n    def f(self): return 1") == []
    assert any("syntax" in i for i in a.validate_code("python", "class Solution:\n  def f(:"))
    assert a.validate_code("python", "") == ["Missing source code"]
    assert a.validate_code("python", "```py\nx\n```") == ["Markdown fences found; expected raw source"]


def test_brace_fallback_when_compile_disabled():
    assert a.validate_code("java", "class Solution { }") == []
    assert a.validate_code("cpp", "class Solution {") == ["Unbalanced braces"]
    assert a.brace_check("class Solution {") == ["Unbalanced braces"]


@pytest.mark.skipif(shutil.which("g++") is None, reason="g++ missing")
def test_cpp_compile_check(monkeypatch):
    monkeypatch.setenv("COMPILE_CHECK", "1")
    good = "class Solution {\npublic:\n    int f(vector<int>& v) { return v.size(); }\n};"
    bad = "class Solution {\npublic:\n    int f() { return undefined_name; }\n};"
    assert a.validate_code("cpp", good) == []
    assert any("Compile error" in i for i in a.validate_code("cpp", bad))


@pytest.mark.skipif(shutil.which("g++") is None, reason="g++ missing")
def test_cpp_listnode_stub(monkeypatch):
    monkeypatch.setenv("COMPILE_CHECK", "1")
    code = "class Solution {\npublic:\n    ListNode* f(ListNode* h) { return h; }\n};"
    assert a.validate_code("cpp", code) == []


def test_bullets_formatting():
    text = a.bullets([{"question": "Q1", "answer": "A1"}, {"input": "[1]", "expected": "1", "why": "single"}])
    assert "**Q:** Q1" in text and "**A:** A1" in text
    assert "Input: `[1]` -> Expected: `1` (single)" in text
    assert a.bullets([]) == "- Not provided\n"


def test_update_progress_schedule():
    progress = {"schema_version": 1, "problems": []}
    day = dt.date(2026, 1, 1)
    a.update_progress(progress, {"title": "Pow(x, n)", "titleSlug": "powx-n", "questionFrontendId": "50", "difficulty": "Medium"}, day)
    a.update_progress(progress, {"title": "Pow(x, n)", "titleSlug": "powx-n", "questionFrontendId": "50"}, day)  # duplicate ignored
    (entry,) = progress["problems"]
    assert entry["revision_dates"] == ["2026-01-02", "2026-01-04", "2026-01-08", "2026-01-15", "2026-01-31"]
    assert entry["my_attempt"] == "solutions/50-powx-n/MY_ATTEMPT.md"


def test_queue_due_upcoming_and_stats(tmp_path, monkeypatch):
    monkeypatch.setattr(a, "REVISION_FILE", tmp_path / "queue.md")
    progress = {"schema_version": 1, "problems": []}
    a.update_progress(progress, {"title": "Two Sum", "titleSlug": "two-sum", "questionFrontendId": "1", "difficulty": "Easy"}, dt.date(2026, 1, 1))
    a.write_revision_queue(progress, dt.date(2026, 1, 5))
    text = (tmp_path / "queue.md").read_text()
    due_part = text.split("## Upcoming")[0]
    assert "Two Sum" in due_part and "due 2026-01-02" in due_part and "due 2026-01-04" in due_part
    assert "2026-01-08" in text.split("## Upcoming")[1]
    assert "Problems tracked: 1 (Easy 1)" in text
    assert "Revisions done: 0 / 5" in text


def test_selection_skips_seen_and_is_deterministic(monkeypatch):
    pool = [make_problem(f"p{i}", d) for i, d in enumerate(["Easy", "Medium", "Hard"] * 5)]
    progress = {"problems": [{"slug": "p0"}, {"slug": "p1"}]}
    monkeypatch.setattr(a, "existing_slugs", lambda prog: {p["slug"] for p in prog["problems"]})
    first = a.select_new_questions(list(pool), progress, 3)
    second = a.select_new_questions(list(reversed(pool)), progress, 3)
    assert [q["titleSlug"] for q in first] == [q["titleSlug"] for q in second]
    assert not {"p0", "p1"} & {q["titleSlug"] for q in first}
    assert len({q["titleSlug"] for q in first}) == 3


def test_selection_raises_when_exhausted(monkeypatch):
    monkeypatch.setattr(a, "existing_slugs", lambda prog: {"p0"})
    with pytest.raises(RuntimeError, match="unseen"):
        a.select_new_questions([make_problem("p0")], {"problems": []}, 1)


def test_weights_parse_and_bias(monkeypatch):
    monkeypatch.setenv("DIFFICULTY_WEIGHTS", "Easy:0,Medium:0,Hard:1")
    assert a.parse_weights() == {"Easy": 0.0, "Medium": 0.0, "Hard": 1.0}
    monkeypatch.setenv("DIFFICULTY_WEIGHTS", "garbage")
    assert a.parse_weights() == a.DEFAULT_WEIGHTS
    monkeypatch.setenv("DIFFICULTY_WEIGHTS", "Easy:0,Medium:0,Hard:1")
    monkeypatch.setattr(a, "existing_slugs", lambda prog: set())
    pool = [make_problem(f"e{i}", "Easy") for i in range(5)] + [make_problem(f"h{i}", "Hard") for i in range(5)]
    picked = a.select_new_questions(pool, {"problems": []}, 3)
    assert Counter(q["difficulty"] for q in picked) == {"Hard": 3}


def test_mark_revision(tmp_path, monkeypatch):
    progress = {"schema_version": 1, "problems": []}
    a.update_progress(progress, {"title": "Two Sum", "titleSlug": "two-sum", "questionFrontendId": "1"}, dt.date(2026, 1, 1))
    assert mr.mark(progress, "1", "3") == 1
    assert progress["problems"][0]["revision_status"]["3"] == "done"
    assert mr.mark(progress, "1", "all") == 4
    with pytest.raises(ValueError):
        mr.mark(progress, "999", "all")
    with pytest.raises(ValueError):
        mr.mark(progress, "1", "5")


def test_repair_replaces_bad_code(monkeypatch):
    pack = {"solutions": {"python": "class Solution:\n  def f(:"}}
    monkeypatch.setattr(a, "gemini_json", lambda prompt: {"solutions": {"python": "class Solution:\n    def f(self): return 1"}})
    a.repair_solutions({"title": "T", "content": "x"}, pack, ["python"])
    assert a.validate_code("python", pack["solutions"]["python"]) == []


def test_repair_survives_api_failure(monkeypatch):
    pack = {"solutions": {"python": "class Solution:\n  def f(:"}}

    def boom(prompt):
        raise RuntimeError("api down")

    monkeypatch.setattr(a, "gemini_json", boom)
    a.repair_solutions({"title": "T", "content": "x"}, pack, ["python"])  # must not raise
    assert "def f(:" in pack["solutions"]["python"]


def test_progress_json_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(a, "PROGRESS_DIR", tmp_path)
    monkeypatch.setattr(a, "PROGRESS_FILE", tmp_path / "progress.json")
    assert a.load_progress() == {"schema_version": 1, "problems": []}
    (tmp_path / "progress.json").write_text("{broken")
    with pytest.raises(RuntimeError):
        a.load_progress()
    (tmp_path / "progress.json").write_text(json.dumps({"schema_version": 1, "problems": []}))
    assert a.load_progress()["problems"] == []
