# conftest.py

import pytest
import sys
from IPython.testing.globalipapp import start_ipython
from IPython.core.interactiveshell import InteractiveShell

# Adjust this path based on your project structure.
# It should be the directory CONTAINING your extension module (e.g., 'poly.py' or 'poly/' directory).
EXTENSION_PARENT_DIR = '/path/to/your/extension/parent/dir'


@pytest.fixture(scope="session", autouse=True)
def setup_path():
    """Adds the 'src' directory to the Python path."""
    # Using Path for reliable path construction
    from pathlib import Path
    root_dir = Path(__file__).parent.parent  # Navigate up to the project root
    src_dir = root_dir / "src"

    # Insert the 'src' directory at the beginning of sys.path
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
        # This line ensures that Python can find the 'poly' package inside 'src'
        print(f"[SETUP] Added {src_dir} to sys.path.")

@pytest.fixture(scope="session")
def ipython_session():
    """Initializes and returns an IPython session for the entire test run."""

    # 1. Add the extension's path to sys.path
    if EXTENSION_PARENT_DIR not in sys.path:
        sys.path.insert(0, EXTENSION_PARENT_DIR)

    # 2. Start an IPython session programmatically
    # start_ipython() ensures a clean, isolated shell instance.
    return start_ipython()


@pytest.fixture(scope="function")
def ip_shell(ipython_session):
    """Provides the InteractiveShell instance for each test function."""
    # Ensure the shell is clean for each test (though the instance is the same)
    ipython_session.reset()
    return ipython_session