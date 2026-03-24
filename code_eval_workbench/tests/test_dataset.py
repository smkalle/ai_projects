"""Tests for dataset.py."""
from dataset import DATASET, get_dataset, get_categories, get_difficulties


class TestGetDataset:
    def test_returns_all_when_no_filters(self):
        result = get_dataset()
        assert len(result) == len(DATASET)

    def test_filters_by_single_category(self):
        result = get_dataset(categories=['arithmetic'])
        assert all(item['category'] == 'arithmetic' for item in result)

    def test_filters_by_multiple_categories(self):
        result = get_dataset(categories=['arithmetic', 'logic'])
        assert all(item['category'] in ('arithmetic', 'logic') for item in result)

    def test_filters_by_single_difficulty(self):
        result = get_dataset(difficulties=['easy'])
        assert all(item['difficulty'] == 'easy' for item in result)

    def test_filters_by_multiple_difficulties(self):
        result = get_dataset(difficulties=['easy', 'medium'])
        assert all(item['difficulty'] in ('easy', 'medium') for item in result)

    def test_combines_category_and_difficulty_filters(self):
        result = get_dataset(categories=['arithmetic'], difficulties=['easy'])
        assert all(
            item['category'] == 'arithmetic' and item['difficulty'] == 'easy'
            for item in result
        )

    def test_returns_empty_list_for_no_matches(self):
        result = get_dataset(categories=['nonexistent-category'])
        assert result == []

    def test_returns_correct_count(self):
        assert len(get_dataset(categories=['arithmetic'])) == 2
        assert len(get_dataset(difficulties=['easy'])) == 6
        assert len(get_dataset(difficulties=['medium'])) == 4


class TestGetCategories:
    def test_returns_sorted_unique_categories(self):
        cats = get_categories()
        assert cats == sorted(set(cats))

    def test_contains_expected_categories(self):
        cats = get_categories()
        assert 'arithmetic' in cats
        assert 'logic' in cats
        assert 'recursion' in cats


class TestGetDifficulties:
    def test_returns_sorted_unique_difficulties(self):
        diffs = get_difficulties()
        assert diffs == sorted(set(diffs))

    def test_contains_expected_difficulties(self):
        diffs = get_difficulties()
        assert 'easy' in diffs
        assert 'medium' in diffs


class TestDatasetEntries:
    def test_all_entries_have_required_fields(self):
        for item in DATASET:
            assert 'id' in item
            assert 'category' in item
            assert 'difficulty' in item
            assert 'input' in item
            assert 'buggy_code' in item['input']
            assert 'bug_description' in item['input']
            assert 'reference_output' in item
            assert 'test_code' in item

    def test_all_ids_are_unique(self):
        ids = [item['id'] for item in DATASET]
        assert len(ids) == len(set(ids))

    def test_all_entries_have_valid_categories_and_difficulties(self):
        valid_cats = {'arithmetic', 'off-by-one', 'type-error', 'logic', 'python-gotcha',
                       'string-handling', 'recursion', 'error-handling', 'list-comprehension'}
        valid_diffs = {'easy', 'medium', 'hard'}
        for item in DATASET:
            assert item['category'] in valid_cats, f"Unknown category: {item['category']}"
            assert item['difficulty'] in valid_diffs, f"Unknown difficulty: {item['difficulty']}"
