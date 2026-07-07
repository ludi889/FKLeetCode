import asyncio

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.base import Problem, Session
from sqlalchemy.ext.asyncio import AsyncSession

async def seed_database(async_session: AsyncSession):
    async with async_session as session:
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

SEED_PROBLEMS = [
    {
        "title": "Two Sum",
        "statement": (
            "Given an array of integers nums and an integer target, return indices "
            "of the two numbers such that they add up to target. Each input has "
            "exactly one solution, and you may not use the same element twice."
        ),
        "signature": {
            "name": "two_sum",
            "args": [
                {"name": "nums", "type": "list[int]"},
                {"name": "target", "type": "int"}
            ],
            "returns": "list[int]"
        },
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
        "variants": [
            {
                "validated": True,
                "scenario_context": "You are a logistics coordinator loading a cargo plane with specific weight limits.",
                "stage_1_mvp": "You are given a list of container weights (`nums`) and the exact remaining weight capacity of the plane (`target`). To maintain balance, you must select exactly two containers that, when combined, perfectly match the remaining capacity. Return their indices.",
                "stage_2_curveball": "The containers are no longer sitting in a warehouse; they are arriving one by one on a high-speed conveyor belt. You don't know all the weights in advance. How do you process this stream efficiently to find a match as early as possible?",
                "stage_3_system": "We now have 10,000 planes being loaded simultaneously across 50 global airports. Design the API and backend architecture to track available container weights and flight capacities in real-time.",
                "technical_rubric": {
                    "time_complexity": "Expected O(N) using a Hash Map.",
                    "space_complexity": "Expected O(N) to store seen elements.",
                    "edge_cases": "Must handle negative weights (if not explicitly clarified) and duplicate values correctly."
                },
                "system_rubric": {
                    "caching": "Should mention Redis or Memcached for fast lookup of container manifests.",
                    "scaling": "Should discuss database sharding by airport or region.",
                    "concurrency": "How do they handle race conditions if two planes try to claim the same container?"
                },
                "communication_rubric": {
                    "clarifying_questions": "Did they ask if weights could be zero or negative? Did they ask about data types?",
                    "testing": "Did they dry-run their algorithm with a small test case before executing?"
                }
            },
            {
                "validated": False,  # Keeps your test logic for filtering valid variants intact
                "scenario_context": "As an alchemist, you are brewing a potion using vials of mana.",
                "stage_1_mvp": "You have a shelf of vials with varying mana levels (`nums`). To complete the spell, you need exactly two vials whose mana levels sum to the `target` energy required. Return the positions of these two vials.",
                "stage_2_curveball": "Certain mana types react explosively. How do you filter out incompatible pairs?",
                "stage_3_system": "Design a marketplace for alchemists to trade vials globally.",
                "technical_rubric": {},
                "system_rubric": {},
                "communication_rubric": {}
            }
        ]
    },
    {
        "title": "Valid Parentheses",
        "statement": (
            "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', "
            "determine if the input string is valid. An input string is valid if open brackets "
            "are closed by the same type of brackets, and in the correct order."
        ),
        "signature": {
            "name": "is_valid",
            "args": [{"name": "s", "type": "str"}],
            "returns": "bool"
        },
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
            ]
        },
        "difficulty": "easy",
        "tags": {"topics": ["string", "stack"]},
        "variants": [
            {
                "validated": True,
                "scenario_context": "You are a code inspector reviewing XML-like routing paths on a legacy server.",
                "stage_1_mvp": "The paths are represented by different node openers and closers: '(', ')', '{', '}', '[', ']'. Determine if the network path is fully resolved (i.e., every opened node is closed by its matching counterpart in the correct chronological order).",
                "stage_2_curveball": "Instead of just returning True/False, the system now requires you to return the exact index of the character where the routing path first became invalid. How does your logic change?",
                "stage_3_system": "These routing logs are massive (100GB+ per file). We need a service that validates them nightly. How do you build a pipeline to process files that don't fit into RAM?",
                "technical_rubric": {
                    "data_structure": "Must use a Stack (List/Array).",
                    "time_complexity": "Expected O(N).",
                    "edge_cases": "Must handle strings that are all opening brackets, all closing brackets, or start with a closing bracket."
                },
                "system_rubric": {
                    "file_io": "Should discuss streaming file readers (e.g., Python generators, chunking).",
                    "distributed_processing": "Can chunks be processed in parallel? (Trick question: state depends on previous chunks, requires discussion of boundary passing)."
                },
                "communication_rubric": {
                    "clarifying_questions": "Did they ask about empty strings?",
                    "adaptability": "Did they quickly adapt the stack to store tuples of (char, index) for the curveball?"
                }
            }
        ]
    },
    {
        "title": "Best Time to Buy and Sell Stock",
        "statement": (
            "You are given an array prices where prices[i] is the price of a given stock "
            "on the ith day. You want to maximize your profit by choosing a single day to "
            "buy one stock and choosing a different day in the future to sell that stock."
        ),
        "signature": {
            "name": "max_profit",
            "args": [{"name": "prices", "type": "list[int]"}],
            "returns": "int"
        },
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
                {"input": {"prices": [7, 6, 4, 3, 1]}, "expected": 0}
            ]
        },
        "difficulty": "easy",
        "tags": {"topics": ["array", "dynamic-programming"]},
        "variants": [
            {
                "validated": True,
                "scenario_context": "You are a space merchant trading dilithium crystals across different star systems.",
                "stage_1_mvp": "You have a chronological forecast of market values (`prices`). Due to cargo restrictions, you can only buy a crystal once and sell it once at a later date. Find the maximum profit you can achieve.",
                "stage_2_curveball": "The Intergalactic Federation just introduced a flat tax rate per transaction. How do you modify your algorithm to subtract this fee from the final profit, and does it change when you buy/sell?",
                "stage_3_system": "Instead of a daily forecast, crystal prices are streaming via sub-space telemetry at 100,000 updates per second. How do you architect a backend to ingest, store, and query this real-time financial data?",
                "technical_rubric": {
                    "time_complexity": "Expected O(N) using a single pass, tracking min_price.",
                    "space_complexity": "Expected O(1).",
                    "edge_cases": "Array in strictly descending order (must return 0, not a negative loss)."
                },
                "system_rubric": {
                    "streaming": "Should mention Kafka, RabbitMQ, or AWS Kinesis for ingestion.",
                    "storage": "Should discuss Time-Series Databases (TSDB) like InfluxDB or TimescaleDB."
                },
                "communication_rubric": {
                    "testing": "Did they walk through the strictly descending case manually before running?"
                }
            }
        ]
    },
    {
        "title": "Product of Array Except Self",
        "statement": (
            "Given an integer array nums, return an array answer such that answer[i] is equal to "
            "the product of all the elements of nums except nums[i]. You must write an algorithm "
            "that runs in O(n) time and without using the division operation."
        ),
        "signature": {
            "name": "product_except_self",
            "args": [{"name": "nums", "type": "list[int]"}],
            "returns": "list[int]"
        },
        "constraints": {
            "array_length": {"min": 2, "max": 100_000},
            "value_range": {"min": -30, "max": 30}
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
        "variants": [
            {
                "validated": True,
                "scenario_context": "You are managing a network grid of satellite relays.",
                "stage_1_mvp": "The transmission strength at a given node is equal to the combined amplification power of all *other* nodes in the network. Given an array of individual satellite powers (`nums`), return the transmission strength for each satellite. The floating point processor is broken, so you cannot use division.",
                "stage_2_curveball": "Occasionally, a satellite goes entirely offline (power = 0). Your current logic might output 0 for the entire grid. How do you gracefully handle grids containing one zero, or multiple zeros?",
                "stage_3_system": "The satellites are distributed globally, and their power levels fluctuate constantly. Designing a centralized master server creates too much latency. How do you architect a decentralized system where nodes share their state updates?",
                "technical_rubric": {
                    "time_complexity": "Expected O(N) using left/right prefix arrays.",
                    "space_complexity": "Expected O(1) auxiliary space (excluding the output array).",
                    "edge_cases": "Must cleanly handle one zero (only that index has non-zero value) and multiple zeros (all indices are zero)."
                },
                "system_rubric": {
                    "consistency": "Should discuss CAP theorem, specifically Eventual Consistency vs Strong Consistency.",
                    "gossip_protocol": "Bonus points for mentioning Gossip Protocols for node-to-node state replication."
                },
                "communication_rubric": {
                    "clarifying_questions": "Did they proactively ask about zeros or negative power levels before starting Stage 1?"
                }
            }
        ]
    }
]
async def seed() -> None:
    await seed_database(AsyncSessionLocal())


if __name__ == "__main__":
    asyncio.run(seed())