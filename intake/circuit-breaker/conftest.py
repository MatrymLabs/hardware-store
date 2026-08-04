"""Make the Part's implementation importable to its contract tests (the tests import the
canonical module name; store_check runs pytest with this directory as cwd)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "impl" / "python"))
