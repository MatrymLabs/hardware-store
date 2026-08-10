"""Make the Part's implementation importable to its contract tests, and supply it as a fixture.

The contract suite imports NOTHING concrete. It receives the implementation through `loader`, so
the same tests run unchanged against a second adapter, in this or any language, by pointing this
fixture at it. That is what makes them CONTRACT tests rather than unit tests with a nice name.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent / "contract"))
sys.path.insert(0, str(Path(__file__).parent / "impl" / "python"))


@pytest.fixture
def loader():
    """The implementation under contract. Swap this to test another adapter."""
    import typed_settings_impl

    return typed_settings_impl
