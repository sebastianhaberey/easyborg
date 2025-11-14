from pathlib import Path

from easyborg.util import remove_redundant_paths


def test_keeps_original_order():
    paths = [
        Path("data/text"),
        Path("data/images"),
    ]
    assert remove_redundant_paths(paths) == [
        Path("data/text"),
        Path("data/images"),
    ]


def test_keeps_order_when_subpaths_removed():
    paths = [
        Path("data/text"),
        Path("data/images"),
        Path("data/text/file1.txt"),
        Path("data/images/cat.png"),
    ]
    assert remove_redundant_paths(paths) == [
        Path("data/text"),
        Path("data/images"),
    ]


def test_keeps_order_even_with_mixed_input_order():
    paths = [
        Path("data/images/cat.png"),
        Path("data/text"),
        Path("data/images"),  # parent appears AFTER child
        Path("data/text/file.txt"),
    ]
    assert remove_redundant_paths(paths) == [
        Path("data/text"),
        Path("data/images"),
    ]


def test_deep_children_removed_but_parent_order_kept():
    paths = [
        Path("a/b/c/d"),
        Path("x/y/z"),
        Path("a/b"),
        Path("x/y/z/1.txt"),
        Path("a/b/c"),
    ]
    assert remove_redundant_paths(paths) == [
        Path("x/y/z"),
        Path("a/b"),
    ]


def test_duplicates_do_not_change_order():
    paths = [
        Path("data/text"),
        Path("data/text"),
        Path("data/text/file.txt"),
    ]
    assert remove_redundant_paths(paths) == [Path("data/text")]
