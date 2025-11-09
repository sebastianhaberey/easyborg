# tests/helpers/fakes.py


class FakeFzf:
    """
    Simple fzf replacement for tests: returns pre-defined responses
    in the order they will be requested.

    Each response should either be:
      - a single value    -> returned as a single-item list
      - a list of values  -> returned as-is
    """

    def __init__(self, responses):
        self._responses = iter(responses)

    def select_items(self, *_args, **_kwargs):
        result = next(self._responses)
        return result if isinstance(result, list) else [result]

    def select_strings(self, *_args, **_kwargs):
        result = next(self._responses)
        return result if isinstance(result, list) else [result]
