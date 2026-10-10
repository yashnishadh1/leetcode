class Solution:
    def checkIfPrerequisite(self, numCourses: int, prerequisites: list[list[int]], queries: list[list[int]]) -> list[bool]:
        # is_pre[u][v] will be True if u is a prerequisite of v
        is_pre = [[False] * numCourses for _ in range(numCourses)]
        
        for u, v in prerequisites:
            is_pre[u][v] = True
            
        # Floyd-Warshall for Transitive Closure
        for k in range(numCourses):
            for i in range(numCourses):
                for j in range(numCourses):
                    if is_pre[i][k] and is_pre[k][j]:
                        is_pre[i][j] = True
                        
        return [is_pre[u][v] for u, v in queries]
