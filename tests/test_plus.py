import pytest
from app import simple_plus


@pytest.mark.IAM_30
def test_simple_plus():
    assert simple_plus(1, 2) == 3
    assert simple_plus(27, 4) == 31


@pytest.mark.IAM_31
def test_simple_plus_using_string():
    with pytest.raises(TypeError):
        simple_plus('string', 'string')
