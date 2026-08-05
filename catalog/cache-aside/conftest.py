"""Make the Part's implementation importable to its contract tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "impl" / "python"))
