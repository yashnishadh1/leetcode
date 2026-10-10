class Solution {
    public List<Boolean> checkIfPrerequisite(int numCourses, int[][] prerequisites, int[][] queries) {
        boolean[][] isPre = new boolean[numCourses][numCourses];
        
        for (int[] edge : prerequisites) {
            isPre[edge[0]][edge[1]] = true;
        }
        
        // Floyd-Warshall for Transitive Closure
        for (int k = 0; k < numCourses; k++) {
            for (int i = 0; i < numCourses; i++) {
                for (int j = 0; j < numCourses; j++) {
                    if (isPre[i][k] && isPre[k][j]) {
                        isPre[i][j] = true;
                    }
                }
            }
        }
        
        List<Boolean> ans = new ArrayList<>(queries.length);
        for (int[] q : queries) {
            ans.add(isPre[q[0]][q[1]]);
        }
        return ans;
    }
}
