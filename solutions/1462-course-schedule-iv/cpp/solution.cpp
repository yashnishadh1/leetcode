class Solution {
public:
    vector<bool> checkIfPrerequisite(int numCourses, vector<vector<int>>& prerequisites, vector<vector<int>>& queries) {
        vector<vector<bool>> isPre(numCourses, vector<bool>(numCourses, false));
        
        for (const auto& edge : prerequisites) {
            isPre[edge[0]][edge[1]] = true;
        }
        
        // Floyd-Warshall for Transitive Closure
        for (int k = 0; k < numCourses; ++k) {
            for (int i = 0; i < numCourses; ++i) {
                for (int j = 0; j < numCourses; ++j) {
                    if (isPre[i][k] && isPre[k][j]) {
                        isPre[i][j] = true;
                    }
                }
            }
        }
        
        vector<bool> ans;
        ans.reserve(queries.size());
        for (const auto& q : queries) {
            ans.push_back(isPre[q[0]][q[1]]);
        }
        return ans;
    }
};
