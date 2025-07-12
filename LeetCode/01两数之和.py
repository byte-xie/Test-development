"""
https://leetcode.cn/problems/two-sum/
"""

from typing import List


class Solution:
    # 暴力枚举
    def twoSum1(self, nums: List[int], target: int) -> List[int]:
        n = len(nums)
        for i in range(n):
            for j in range(i + 1, n):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []

    # 哈希表
    def twoSum2(self, nums: List[int], target: int) -> List[int]:
        hashtable = dict()
        for i, num in enumerate(nums):
            if target - num in hashtable:
                return [hashtable[target - num], i]
            hashtable[nums[i]] = i
        return []

    # 双指针 + 索引排序
    def twoSum3(self, nums: List[int], target: int) -> List[int]:
        # 创建一个带索引的数组
        index_nums = [(num, i) for i, num in enumerate(nums)]
        index_nums.sort(key=lambda x: x[0])  # 按值排序
        left, right = 0, len(nums) - 1
        while left < right:
            current_sum = index_nums[left][0] + index_nums[right][0]
            if current_sum == target:
                return [index_nums[left][1], index_nums[right][1]]
            elif current_sum < target:
                left += 1
            else:
                right -= 1
        return []

    # 二分搜索
    def twoSum4(self, nums: List[int], target: int) -> List[int]:
        indexed_nums = [(num, i) for i, num in enumerate(nums)]
        indexed_nums.sort(key=lambda x: x[0])

        for i in range(len(indexed_nums)):
            complement = target - indexed_nums[i][0]
            # 在右侧子数组二分查找
            lo, hi = i + 1, len(nums) - 1
            while lo <= hi:
                mid = (lo + hi) // 2
                if indexed_nums[mid][0] == complement:
                    return [indexed_nums[i][1], indexed_nums[mid][1]]
                elif indexed_nums[mid][0] < complement:
                    lo = mid + 1
                else:
                    hi = mid - 1
        return []


if __name__ == '__main__':
    # 示例用例
    nums = [2, 7, 11, 15]
    target = 9
    sol = Solution()
    result1 = sol.twoSum1(nums, target)
    print(result1)

    result2 = sol.twoSum2(nums, target)
    print(result2)

    result3 = sol.twoSum3(nums, target)
    print(result3)

    result4 = sol.twoSum4(nums, target)
    print(result4)
