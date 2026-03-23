"""
Curated bug-fix dataset for the Code Eval Workbench.

Each example has:
  - id, category, difficulty
  - input: buggy_code + bug_description
  - reference_output: the correct fixed code
  - test_code: pytest-style assertions to validate the fix programmatically
"""
import json
import os

from dotenv import load_dotenv

load_dotenv()


# ─── Curated Dataset (10 examples) ───────────────────────────────────────────

DATASET: list[dict] = [
    # ── 1. Arithmetic operator ───────────────────────────────────────────────
    {
        "id": "bug_001",
        "category": "arithmetic",
        "difficulty": "easy",
        "input": {
            "buggy_code": (
                "def add(a, b):\n"
                "    return a - b"
            ),
            "bug_description": (
                "The function should add two numbers but it subtracts instead."
            ),
        },
        "reference_output": (
            "def add(a, b):\n"
            "    return a + b  # Fixed: changed '-' to '+'"
        ),
        "test_code": (
            "def test_add():\n"
            "    assert add(2, 3) == 5\n"
            "    assert add(-1, 1) == 0\n"
            "    assert add(0, 0) == 0\n"
            "    assert add(100, 200) == 300\n"
        ),
    },

    # ── 2. Off-by-one in range ───────────────────────────────────────────────
    {
        "id": "bug_002",
        "category": "off-by-one",
        "difficulty": "easy",
        "input": {
            "buggy_code": (
                "def sum_list(lst):\n"
                "    total = 0\n"
                "    for i in range(len(lst) - 1):  # misses last element\n"
                "        total += lst[i]\n"
                "    return total"
            ),
            "bug_description": (
                "The function misses the last element because the range is one too short."
            ),
        },
        "reference_output": (
            "def sum_list(lst):\n"
            "    total = 0\n"
            "    for i in range(len(lst)):  # Fixed: removed '- 1'\n"
            "        total += lst[i]\n"
            "    return total"
        ),
        "test_code": (
            "def test_sum_list():\n"
            "    assert sum_list([1, 2, 3, 4, 5]) == 15\n"
            "    assert sum_list([10]) == 10\n"
            "    assert sum_list([]) == 0\n"
            "    assert sum_list([-1, -2, -3]) == -6\n"
        ),
    },

    # ── 3. Type coercion ─────────────────────────────────────────────────────
    {
        "id": "bug_003",
        "category": "type-error",
        "difficulty": "easy",
        "input": {
            "buggy_code": (
                "def greet(name, age):\n"
                '    return "Hello, " + name + "! You are " + age + " years old."'
            ),
            "bug_description": (
                "The function throws a TypeError because 'age' is an int "
                "and cannot be concatenated with strings using '+'."
            ),
        },
        "reference_output": (
            "def greet(name, age):\n"
            '    return "Hello, " + name + "! You are " + str(age) + " years old."'
            "  # Fixed: wrapped age with str()"
        ),
        "test_code": (
            "def test_greet():\n"
            '    assert greet("Alice", 30) == "Hello, Alice! You are 30 years old."\n'
            '    assert greet("Bob", 0) == "Hello, Bob! You are 0 years old."\n'
            '    assert "25" in greet("Carol", 25)\n'
        ),
    },

    # ── 4. Boolean logic ─────────────────────────────────────────────────────
    {
        "id": "bug_004",
        "category": "logic",
        "difficulty": "medium",
        "input": {
            "buggy_code": (
                "def is_valid_age(age):\n"
                "    # Should return True if age is between 0 and 120 inclusive\n"
                "    return age >= 0 and age <= 120\n"
                "\n"
                "def is_invalid_age(age):\n"
                "    # Should return True if age is outside 0-120\n"
                "    return age < 0 and age > 120  # bug: should be 'or'"
            ),
            "bug_description": (
                "is_invalid_age uses 'and' but it's logically impossible for a number "
                "to be both < 0 AND > 120 simultaneously. It should use 'or'."
            ),
        },
        "reference_output": (
            "def is_valid_age(age):\n"
            "    return age >= 0 and age <= 120\n"
            "\n"
            "def is_invalid_age(age):\n"
            "    return age < 0 or age > 120  # Fixed: changed 'and' to 'or'"
        ),
        "test_code": (
            "def test_is_invalid_age():\n"
            "    assert is_invalid_age(-1) == True\n"
            "    assert is_invalid_age(121) == True\n"
            "    assert is_invalid_age(0) == False\n"
            "    assert is_invalid_age(50) == False\n"
            "    assert is_invalid_age(120) == False\n"
        ),
    },

    # ── 5. Mutable default argument ──────────────────────────────────────────
    {
        "id": "bug_005",
        "category": "python-gotcha",
        "difficulty": "medium",
        "input": {
            "buggy_code": (
                "def append_to(elem, to=[]):\n"
                "    to.append(elem)\n"
                "    return to"
            ),
            "bug_description": (
                "The default argument 'to=[]' is mutable and shared across all calls. "
                "Each call without an explicit 'to' argument will modify the same list, "
                "causing unexpected accumulation of values."
            ),
        },
        "reference_output": (
            "def append_to(elem, to=None):\n"
            "    if to is None:  # Fixed: use None as sentinel, create new list each call\n"
            "        to = []\n"
            "    to.append(elem)\n"
            "    return to"
        ),
        "test_code": (
            "def test_append_to():\n"
            "    result1 = append_to(1)\n"
            "    result2 = append_to(2)\n"
            "    assert result1 == [1], f'Expected [1] but got {result1}'\n"
            "    assert result2 == [2], f'Expected [2] but got {result2}'\n"
            "    # Explicit list should work normally\n"
            "    lst = [10, 20]\n"
            "    assert append_to(30, lst) == [10, 20, 30]\n"
        ),
    },

    # ── 6. Integer division ──────────────────────────────────────────────────
    {
        "id": "bug_006",
        "category": "arithmetic",
        "difficulty": "easy",
        "input": {
            "buggy_code": (
                "def average(numbers):\n"
                "    return sum(numbers) / len(numbers)\n"
                "\n"
                "def median_index(lst):\n"
                "    # Should return the integer index of the middle element\n"
                "    return len(lst) / 2  # bug: returns float, not int"
            ),
            "bug_description": (
                "median_index returns a float (e.g., 2.5) instead of an integer index "
                "because Python 3 uses true division with '/'. Use '//' for integer division."
            ),
        },
        "reference_output": (
            "def average(numbers):\n"
            "    return sum(numbers) / len(numbers)\n"
            "\n"
            "def median_index(lst):\n"
            "    return len(lst) // 2  # Fixed: use integer division"
        ),
        "test_code": (
            "def test_median_index():\n"
            "    assert median_index([1, 2, 3, 4, 5]) == 2\n"
            "    assert median_index([1, 2, 3, 4]) == 2\n"
            "    assert median_index([42]) == 0\n"
            "    assert isinstance(median_index([1, 2, 3]), int)\n"
        ),
    },

    # ── 7. Wrong string method ───────────────────────────────────────────────
    {
        "id": "bug_007",
        "category": "string-handling",
        "difficulty": "easy",
        "input": {
            "buggy_code": (
                "def clean_input(text):\n"
                "    # Remove leading/trailing whitespace and convert to lowercase\n"
                "    return text.split().lower()  # bug: .split() returns a list"
            ),
            "bug_description": (
                ".split() returns a list of words, not a string with whitespace removed. "
                "It should be .strip() to remove leading/trailing whitespace."
            ),
        },
        "reference_output": (
            "def clean_input(text):\n"
            "    return text.strip().lower()  # Fixed: changed .split() to .strip()"
        ),
        "test_code": (
            "def test_clean_input():\n"
            '    assert clean_input("  Hello World  ") == "hello world"\n'
            '    assert clean_input("Python") == "python"\n'
            '    assert clean_input("  SPACES  ") == "spaces"\n'
            '    assert isinstance(clean_input("test"), str)\n'
        ),
    },

    # ── 8. Missing recursion base case ───────────────────────────────────────
    {
        "id": "bug_008",
        "category": "recursion",
        "difficulty": "medium",
        "input": {
            "buggy_code": (
                "def factorial(n):\n"
                "    # Missing base case — will recurse infinitely\n"
                "    return n * factorial(n - 1)"
            ),
            "bug_description": (
                "The factorial function is missing a base case. When n reaches 0 "
                "it will recurse infinitely causing a RecursionError. "
                "Add 'if n == 0: return 1' as the base case."
            ),
        },
        "reference_output": (
            "def factorial(n):\n"
            "    if n == 0:  # Fixed: base case\n"
            "        return 1\n"
            "    return n * factorial(n - 1)"
        ),
        "test_code": (
            "def test_factorial():\n"
            "    assert factorial(0) == 1\n"
            "    assert factorial(1) == 1\n"
            "    assert factorial(5) == 120\n"
            "    assert factorial(10) == 3628800\n"
        ),
    },

    # ── 9. Missing dict key handling ─────────────────────────────────────────
    {
        "id": "bug_009",
        "category": "error-handling",
        "difficulty": "medium",
        "input": {
            "buggy_code": (
                "def get_user_email(users, user_id):\n"
                "    # Returns email or None if user not found\n"
                "    return users[user_id]['email']  # bug: raises KeyError if not found"
            ),
            "bug_description": (
                "Accessing users[user_id] raises KeyError if user_id doesn't exist. "
                "Should use .get() with a default value to handle missing keys gracefully."
            ),
        },
        "reference_output": (
            "def get_user_email(users, user_id):\n"
            "    user = users.get(user_id)  # Fixed: use .get() to avoid KeyError\n"
            "    if user is None:\n"
            "        return None\n"
            "    return user.get('email')"
        ),
        "test_code": (
            "def test_get_user_email():\n"
            "    users = {\n"
            "        1: {'email': 'alice@example.com', 'name': 'Alice'},\n"
            "        2: {'name': 'Bob'},  # no email\n"
            "    }\n"
            "    assert get_user_email(users, 1) == 'alice@example.com'\n"
            "    assert get_user_email(users, 999) is None  # missing user\n"
            "    assert get_user_email(users, 2) is None   # user with no email\n"
        ),
    },

    # ── 10. Wrong list comprehension condition ────────────────────────────────
    {
        "id": "bug_010",
        "category": "list-comprehension",
        "difficulty": "medium",
        "input": {
            "buggy_code": (
                "def get_even_squares(n):\n"
                "    # Return squares of even numbers from 0 to n-1\n"
                "    return [x**2 for x in range(n) if x % 2 == 1]  # bug: filters odds, not evens"
            ),
            "bug_description": (
                "The condition 'x % 2 == 1' filters for odd numbers, "
                "but the function should return squares of EVEN numbers. "
                "Change the condition to 'x % 2 == 0'."
            ),
        },
        "reference_output": (
            "def get_even_squares(n):\n"
            "    return [x**2 for x in range(n) if x % 2 == 0]  # Fixed: == 1 to == 0"
        ),
        "test_code": (
            "def test_get_even_squares():\n"
            "    assert get_even_squares(6) == [0, 4, 16]\n"
            "    assert get_even_squares(1) == [0]\n"
            "    assert get_even_squares(0) == []\n"
            "    assert get_even_squares(10) == [0, 4, 16, 36, 64]\n"
        ),
    },
]


# ─── Dataset Helpers ─────────────────────────────────────────────────────────

def get_dataset(
    categories: list[str] | None = None,
    difficulties: list[str] | None = None,
) -> list[dict]:
    """Return a filtered subset of the dataset."""
    items = DATASET
    if categories:
        items = [d for d in items if d["category"] in categories]
    if difficulties:
        items = [d for d in items if d["difficulty"] in difficulties]
    return items


def get_categories() -> list[str]:
    return sorted({d["category"] for d in DATASET})


def get_difficulties() -> list[str]:
    return sorted({d["difficulty"] for d in DATASET})


# ─── Claude-powered Dataset Generator ────────────────────────────────────────

def generate_examples(
    n: int = 3,
    category: str = "any",
    difficulty: str = "medium",
) -> list[dict]:
    """Use Claude to synthesize n new bug-fix examples in dataset format."""
    import anthropic

    client = anthropic.Anthropic()

    # Build a few-shot prompt with 2 existing examples
    few_shot = json.dumps(DATASET[:2], indent=2)

    category_hint = f"category: '{category}'" if category != "any" else "any category you find interesting"

    prompt = f"""You are building a code evaluation dataset.

Generate {n} new Python bug-fix examples. Each example must follow EXACTLY this JSON structure
(matching the schema below):

```json
[
  {{
    "id": "bug_XXX",
    "category": "<category>",
    "difficulty": "easy|medium|hard",
    "input": {{
      "buggy_code": "<python code with ONE clear bug>",
      "bug_description": "<clear 1-2 sentence description of the bug>"
    }},
    "reference_output": "<the fixed code with a comment marking the fix>",
    "test_code": "<pytest-style test function(s) that PASS with the fixed code>"
  }}
]
```

Requirements:
- {category_hint}
- Difficulty: {difficulty}
- Each bug must be realistic and educational
- test_code must ONLY test the fixed behavior (no imports needed — the fixed function is prepended)
- The test_code pytest functions must call the function defined in buggy_code/reference_output
- Make bugs distinct from these existing examples: {[d['id'] for d in DATASET]}

Here are 2 examples of the exact format to follow:
{few_shot}

Return ONLY a valid JSON array. No explanation, no markdown fences."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    )

    text = next(b.text for b in response.content if b.type == "text")

    # Strip any accidental markdown fences
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        new_examples = json.loads(text)
        # Basic validation
        validated = []
        for ex in new_examples:
            if all(k in ex for k in ("id", "category", "difficulty", "input", "reference_output", "test_code")):
                validated.append(ex)
        return validated
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude returned invalid JSON: {e}\n\nRaw output:\n{text}") from e


import re  # noqa: E402 (used in generate_examples above)
