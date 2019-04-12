import pytest
from calculator import simple_plus


class TestSimplePlus:
    def __init__(self):
        self.issue_key = 'IAM-20'

    def should_calculate_plus_correctly():
        assert simple_plus(1, 2) == 3
        assert simple_plus(27, 4) == 31

    def should_throw_error_when_input_strings():
        with pytest.raises(TypeError):
            simple_plus('string', 'string')
