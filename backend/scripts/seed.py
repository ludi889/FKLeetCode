import asyncio

from sqlalchemy import select

from app.models.problem import Problem
from app.db.session import AsyncSessionLocal

SEED_PROBLEMS = [
    {
        "title": "Two Sum",
        "statement": (
            "Given an array of integers nums and an integer target, return indices "
            "of the two numbers such that they add up to target. Each input has "
            "exactly one solution, and you may not use the same element twice."
        ),
        "constraints": {
            "array_length": {"min": 2, "max": 10_000},
            "value_range": {"min": -1_000_000_000, "max": 1_000_000_000},
            "exactly_one_solution": True,
        },
        "reference_solution": (
            "def two_sum(nums: list[int], target: int) -> list[int]:\n"
            "    seen = {}\n"
            "    for i, num in enumerate(nums):\n"
            "        complement = target - num\n"
            "        if complement in seen:\n"
            "            return [seen[complement], i]\n"
            "        seen[num] = i\n"
            "    raise ValueError('No solution found')\n"
        ),
        "test_cases": {
            "cases": [
                {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
                {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
                {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1]},
            ]
        },
        "difficulty": "easy",
        "tags": {"topics": ["arrays", "hash-map"]},
    },
    {
        "title": "Valid Parentheses",
        "statement": (
            "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', "
            "determine if the input string is valid. An input string is valid if open brackets "
            "are closed by the same type of brackets, and in the correct order."
        ),
        "constraints": {
            "string_length": {"min": 1, "max": 10_000},
            "characters": ["(", ")", "{", "}", "[", "]"]
        },
        "reference_solution": (
            "def is_valid(s: str) -> bool:\n"
            "    stack = []\n"
            "    mapping = {')': '(', '}': '{', ']': '['}\n"
            "    for char in s:\n"
            "        if char in mapping:\n"
            "            top_element = stack.pop() if stack else '#'\n"
            "            if mapping[char] != top_element:\n"
            "                return False\n"
            "        else:\n"
            "            stack.append(char)\n"
            "    return not stack\n"
        ),
        "test_cases": {
            "cases": [
                {"input": {"s": "()"}, "expected": True},
                {"input": {"s": "()[]{}"}, "expected": True},
                {"input": {"s": "(]"}, "expected": False},
                {"input": {"s": "([)]"}, "expected": False},
                {"input": {"s": "{[]}"}, "expected": True}
            ]
        },
        "difficulty": "easy",
        "tags": {"topics": ["string", "stack"]},
    },
    {
        "title": "Best Time to Buy and Sell Stock",
        "statement": (
            "You are given an array prices where prices[i] is the price of a given stock "
            "on the ith day. You want to maximize your profit by choosing a single day to "
            "buy one stock and choosing a different day in the future to sell that stock. "
            "Return the maximum profit you can achieve. If you cannot achieve any profit, return 0."
        ),
        "constraints": {
            "array_length": {"min": 1, "max": 100_000},
            "price_value": {"min": 0, "max": 10_000}
        },
        "reference_solution": (
            "def max_profit(prices: list[int]) -> int:\n"
            "    min_price = float('inf')\n"
            "    max_profit = 0\n"
            "    for price in prices:\n"
            "        if price < min_price:\n"
            "            min_price = price\n"
            "        elif price - min_price > max_profit:\n"
            "            max_profit = price - min_price\n"
            "    return max_profit\n"
        ),
        "test_cases": {
            "cases": [
                {"input": {"prices": [7, 1, 5, 3, 6, 4]}, "expected": 5},
                {"input": {"prices": [7, 6, 4, 3, 1]}, "expected": 0},
                {"input": {"prices": [2, 4, 1]}, "expected": 2}
            ]
        },
        "difficulty": "easy",
        "tags": {"topics": ["array", "dynamic-programming"]},
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "statement": (
            "Given a string s, find the length of the longest substring without repeating characters."
        ),
        "constraints": {
            "string_length": {"min": 0, "max": 50_000},
            "characters": "English letters, digits, symbols and spaces"
        },
        "reference_solution": (
            "def length_of_longest_substring(s: str) -> int:\n"
            "    char_map = {}\n"
            "    left = 0\n"
            "    max_length = 0\n"
            "    for right, char in enumerate(s):\n"
            "        if char in char_map and char_map[char] >= left:\n"
            "            left = char_map[char] + 1\n"
            "        char_map[char] = right\n"
            "        max_length = max(max_length, right - left + 1)\n"
            "    return max_length\n"
        ),
        "test_cases": {
            "cases": [
                {"input": {"s": "abcabcbb"}, "expected": 3},
                {"input": {"s": "bbbbb"}, "expected": 1},
                {"input": {"s": "pwwkew"}, "expected": 3},
                {"input": {"s": ""}, "expected": 0}
            ]
        },
        "difficulty": "medium",
        "tags": {"topics": ["hash-table", "string", "sliding-window"]},
    },
    {
        "title": "Product of Array Except Self",
        "statement": (
            "Given an integer array nums, return an array answer such that answer[i] is equal to "
            "the product of all the elements of nums except nums[i]. You must write an algorithm "
            "that runs in O(n) time and without using the division operation."
        ),
        "constraints": {
            "array_length": {"min": 2, "max": 100_000},
            "value_range": {"min": -30, "max": 30},
            "guaranteed_fit": "The product of any prefix or suffix fits in a 32-bit integer."
        },
        "reference_solution": (
            "def product_except_self(nums: list[int]) -> list[int]:\n"
            "    length = len(nums)\n"
            "    answer = [1] * length\n"
            "    left_product = 1\n"
            "    for i in range(length):\n"
            "        answer[i] = left_product\n"
            "        left_product *= nums[i]\n"
            "    right_product = 1\n"
            "    for i in range(length - 1, -1, -1):\n"
            "        answer[i] *= right_product\n"
            "        right_product *= nums[i]\n"
            "    return answer\n"
        ),
        "test_cases": {
            "cases": [
                {"input": {"nums": [1, 2, 3, 4]}, "expected": [24, 12, 8, 6]},
                {"input": {"nums": [-1, 1, 0, -3, 3]}, "expected": [0, 0, 9, 0, 0]}
            ]
        },
        "difficulty": "medium",
        "tags": {"topics": ["array", "prefix-sum"]},
    },
    {
        "title": "Merge Intervals",
        "statement": (
            "Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping "
            "intervals, and return an array of the non-overlapping intervals that cover all the "
            "intervals in the input."
        ),
        "constraints": {
            "array_length": {"min": 1, "max": 10_000},
            "interval_values": {"min": 0, "max": 10_000}
        },
        "reference_solution": (
            "def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:\n"
            "    intervals.sort(key=lambda x: x[0])\n"
            "    merged = []\n"
            "    for interval in intervals:\n"
            "        if not merged or merged[-1][1] < interval[0]:\n"
            "            merged.append(interval)\n"
            "        else:\n"
            "            merged[-1][1] = max(merged[-1][1], interval[1])\n"
            "    return merged\n"
        ),
        "test_cases": {
            "cases": [
                {"input": {"intervals": [[1, 3], [2, 6], [8, 10], [15, 18]]}, "expected": [[1, 6], [8, 10], [15, 18]]},
                {"input": {"intervals": [[1, 4], [4, 5]]}, "expected": [[1, 5]]},
                {"input": {"intervals": [[1, 4], [2, 3]]}, "expected": [[1, 4]]}
            ]
        },
        "difficulty": "medium",
        "tags": {"topics": ["array", "sorting"]},
    }
]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        for data in SEED_PROBLEMS:
            existing = await session.execute(
                select(Problem).where(Problem.title == data["title"])
            )
            if existing.scalar_one_or_none():
                print(f"Skipping '{data['title']}' — already exists.")
                continue

            session.add(Problem(**data))
            print(f"Inserting '{data['title']}'.")

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())