from easyborg.util import deep_merge


def test_shallow_merge():
    base = {"a": 1, "b": 2}
    override = {"b": 3, "c": 4}
    result = deep_merge(base, override)

    assert result == {"a": 1, "b": 3, "c": 4}


def test_nested_merge():
    base = {"repos": {"main": {"path": "/old"}}}
    override = {"repos": {"main": {"path": "/new"}}}
    result = deep_merge(base, override)

    assert result == {"repos": {"main": {"path": "/new"}}}


def test_nested_addition():
    base = {"repos": {"main": {"path": "/old"}}}
    override = {"repos": {"office": {"path": "/office"}}}
    result = deep_merge(base, override)

    assert result == {
        "repos": {
            "main": {"path": "/old"},
            "office": {"path": "/office"},
        }
    }


def test_deep_merge_multiple_levels():
    base = {
        "a": {"b": {"c": 1, "d": 2}},
    }
    override = {
        "a": {"b": {"c": 99}},
    }
    result = deep_merge(base, override)

    assert result == {
        "a": {"b": {"c": 99, "d": 2}},
    }


def test_non_dict_override_replaces_entire_value():
    base = {"a": {"b": 1}}
    override = {"a": 10}
    result = deep_merge(base, override)

    assert result == {"a": 10}


def test_list_is_replaced_not_merged():
    base = {"groups": ["home", "work"]}
    override = {"groups": ["work"]}
    result = deep_merge(base, override)

    assert result == {"groups": ["work"]}
