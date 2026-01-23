
import pytest
from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from view_logs import tail_file

def test_tail_file_none():
    with pytest.raises(TypeError):
        tail_file(None)

def test_tail_file_empty_string():
    with pytest.raises(TypeError):
        tail_file("")

def test_tail_file_huge_number():
    with pytest.raises(TypeError):
        tail_file(1000000)

def test_tail_file_negative_number():
    with pytest.raises(TypeError):
        tail_file(-1000000)

def test_tail_file_invalid_path():
    with pytest.raises(FileNotFoundError):
        tail_file(Path("/invalid/path"))

def test_tail_file_valid_path():
    # Create a temporary file
    temp_file = Path("temp.log")
    temp_file.write_text("Test log file")
    
    # Test with a valid path
    tail_file(temp_file)
    
    # Remove the temporary file
    temp_file.unlink()

def test_tail_file_follow_true():
    # Create a temporary file
    temp_file = Path("temp.log")
    temp_file.write_text("Test log file")
    
    # Test with follow=True
    with pytest.raises(KeyboardInterrupt):
        tail_file(temp_file, follow=True)
    
    # Remove the temporary file
    temp_file.unlink()

def test_tail_file_level_filter():
    # Create a temporary file
    temp_file = Path("temp.log")
    temp_file.write_text("INFO Test log file")
    
    # Test with level filter
    tail_file(temp_file, level_filter="INFO")
    
    # Remove the temporary file
    temp_file.unlink()
