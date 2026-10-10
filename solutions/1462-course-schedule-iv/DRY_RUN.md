# Dry run and test cases

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

## Suggested tests

- Input: `numCourses = 2, prerequisites = [[1,0]], queries = [[0,1],[1,0]]` -> Expected: `[false,true]` (1 is a prerequisite of 0, but 0 is not a prerequisite of 1.)
- Input: `numCourses = 3, prerequisites = [[0,1],[1,2]], queries = [[0,2],[2,0]]` -> Expected: `[true,false]` (Path 0 -> 1 -> 2 exists, so 0 is indirect prerequisite of 2. Reverse is not true.)

**Important:** These test ideas are generated, not executed. Confirm expected values against the statement.
