
import sys
import os

# Add 'src' to python path so 'side' package is resolvable
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.append(src_dir)

# Import the mcp object from the runner
# The imports inside runner.py (e.g. 'from .core') will resolve because 
# we are loading it as part of the 'side' package structure.
try:
    from side.forensic_audit.runner import mcp
except ImportError as e:
    print(f"Failed to import mcp: {e}")
    raise
