# 1462. Course Schedule IV

- **Difficulty:** Medium
- **Problem:** https://leetcode.com/problems/course-schedule-iv/
- **Topics:** Depth-First Search, Breadth-First Search, Graph Theory, Topological Sort
- **Generated:** 2026-10-10

## 1. Problem ko simple Hinglish mein samjho

Humein `numCourses` courses diye gaye hain aur unke beech direct prerequisites `prerequisites` list me hain: `[a, b]` ka matlab course `a` lene ke baad hi course `b` le sakte hain. Direct ke alawa indirect prerequisites bhi valid hain (transitive dependency: agar a -> b aur b -> c, toh a course c ka bhi prerequisite hai). Humein multiple `queries` di gayi hain `[u, v]`, aur har query ke liye batana hai ki kya `u` course `v` ka prerequisite hai ya nahi (true/false).

## 2. Input aur output

Input:
- `numCourses` (integer): Total courses (0 se numCourses - 1 tak).
- `prerequisites` (2D array): Direct edges jisme `[a, b]` represent karta hai directed edge a -> b.
- `queries` (2D array): `[u, v]` jisme poocha gaya hai ki kya u se v tak path exist karta hai.
Output:
- Boolean array `answer` of size equal to `queries.length`.
Constraints:
- `2 <= numCourses <= 100` (n kaafi chhota hai, isliye O(n^3) easily chal jayega).
- Graph DAG hai (koi cycle nahi hai).
- Queries up to 10^4 hain (query time O(1) hona chahiye optimal speed ke liye).

## 3. Example walkthrough

Example 1:
- numCourses = 2, prerequisites = [[1,0]], queries = [[0,1],[1,0]]
- Edge: 1 -> 0.
- Query 1: [0, 1] -> Kya 0 se 1 pahunch sakte hain? Nahi, edge 1 se 0 hai. Output: false.
- Query 2: [1, 0] -> Kya 1 se 0 pahunch sakte hain? Haan, direct edge hai. Output: true.
- Final Result: [false, true].

Example 3:
- numCourses = 3, prerequisites = [[1,2],[1,0],[2,0]], queries = [[1,0],[1,2]]
- Edges: 1 -> 2, 1 -> 0, 2 -> 0.
- Query 1: [1, 0] -> 1 se 0 direct edge bhi hai (aur 1 -> 2 -> 0 indirect bhi). Output: true.
- Query 2: [1, 2] -> Direct edge hai. Output: true.
- Final Result: [true, true].

## 4. Brute-force approach

Naive approach yeh hai ki har ek query `[u, v]` ke liye graph me BFS ya DFS run karein to check ki kya `u` se `v` reachable hai. Har query me BFS/DFS ka time O(V + E) hoga. Total time: O(Q * (V + E)). Jahan Q = 10^4 aur V + E around ~5000 ho sakta hai, total operations ~5 * 10^7 ho sakte hain jo TLE de sakta hai ya slow hoga. Repeated queries par redundant graph traversal hota hai.

## 5. Optimized approach

Kyunki `numCourses` (V) sirf 100 tak hai, hum Precomputation kar sakte hain:
1. Transitive Closure (Floyd-Warshall Algorithm):
   - Ek 2D boolean table `isPre[n][n]` banate hain, initialised to false.
   - Sabhi direct prerequisites `[u, v]` ke liye `isPre[u][v] = true` mark karte hain.
   - Fir intermediate node `k` par iterate karke Floyd-Warshall lagate hain:
     Agar `isPre[i][k]` true hai aur `isPre[k][j]` true hai, toh `isPre[i][j] = true` hoga (i -> k -> j path exist karta hai).
   - Yeh precomputation O(V^3) me complete ho jata hai (100^3 = 10^6 operations, jo kuch milliseconds me ho jayega).
2. Answering Queries:
   - Har query `[u, v]` ke liye direct `isPre[u][v]` lookup karenge O(1) time me!
   - Q queries ka total time sirf O(Q) hoga.

## 6. Dry run

numCourses = 3, prerequisites = [[1,2], [2,0]], queries = [[1,0], [0,1]]
Matrix initial state:
isPre[1][2] = true, isPre[2][0] = true; baki sab false.
Floyd-Warshall loop:
- Jab k = 2, i = 1, j = 0:
  Check: isPre[1][2] (true) AND isPre[2][0] (true) == true.
  Toh isPre[1][0] ban gaya true!
Query answering:
- [1, 0]: isPre[1][0] is true -> return true.
- [0, 1]: isPre[0][1] is false -> return false.
Result: [true, false].

## 7. Complexity

- **Time:** Precomputation Time: O(V^3) jahan V = numCourses (at most 100^3 = 10^6). Queries Answering Time: O(Q) jahan Q = queries.length. Overall Time Complexity: O(V^3 + Q), jo constraints ke hisaab se extremely fast hai.
- **Space:** O(V^2) 2D boolean array / matrix store karne ke liye (100 x 100 space negligible hai).

## 8. Common mistakes

- Floyd-Warshall ke 3 nested loops me intermediate node `k` ka loop innermost rakh dena; yaad rahe `k` outermost loop hona chahiye.
- Har query ke liye bar-bar DFS/BFS run karna, jisse overall time limit exceed hone ka risk rehta hai.
- Directed edge ki direction reverse samajh lena: `prerequisites = [a, b]` ka matlab `a -> b` hota hai (a prerequisite hai b ka), na ki b -> a.

## 9. Self-check quiz

- **Q:** Floyd-Warshall algorithm me intermediate node `k` ka loop outermost kyu rakha jata hai?
  **A:** Kyunki dynamic programming subproblem yeh define karti hai ki paths me intermediate nodes sirf {0, 1, ..., k} set se choose ho sakte hain, isliye k ko systematically 0 se V-1 expand karna zaroori hai.
- **Q:** Agar numCourses = 2000 hota aur V^3 TLE deta, toh kaunsa alternative approach use karte?
  **A:** Topological sort (Kahn's algorithm) ke sath bitset ya ancestor sets maintain karke O(V * (V + E) / 64) time me solve kar sakte the.

## 10. Assumptions and caveats

Floyd-Warshall transitive closure approach is chosen because V <= 100 makes V^3 <= 10^6 operations, which executes in a few milliseconds and gives O(1) query time.

## Validation

Static checks only. No code was executed and no LeetCode judge result was obtained.
