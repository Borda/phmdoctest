#### doc/test_setup.py
```python
"""pytest file built from doc/setup.md"""
import pytest

from phmdoctest.fixture import managenamespace
from phmdoctest.functions import _phm_compare_exact


@pytest.fixture(scope="module")
def _phm_setup_teardown(managenamespace):
    # setup code line 9.
    import math

    mylist = [1, 2, 3]
    a, b = 10, 11

    def doubler(x):
        return x * 2

    managenamespace(operation="update", additions=locals())
    yield
    # teardown code line 58.
    mylist.clear()
    assert not mylist, "mylist was not emptied"

    managenamespace(operation="clear")


pytestmark = pytest.mark.usefixtures("_phm_setup_teardown")


def test_code_20_output_27(capsys):
    print("math.pi=", round(math.pi, 3))
    print(mylist)
    print(a, b)
    print("doubler(16)=", doubler(16))

    _phm_expected_str = """\
math.pi= 3.142
[1, 2, 3]
10 11
doubler(16)= 32
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)


def test_code_37_output_42(capsys):
    mylist.append(4)
    print(mylist)

    _phm_expected_str = """\
[1, 2, 3, 4]
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)


def test_code_47_output_51(capsys):
    print(mylist == [1, 2, 3, 4])

    _phm_expected_str = """\
True
"""
    _phm_compare_exact(a=_phm_expected_str, b=capsys.readouterr().out)
```
This page is created from a Markdown file that contains the contents
of a python source file in a syntax highlighted fenced code block.
It is included in the documentation as an example python file.
