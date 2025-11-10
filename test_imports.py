import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    import PyPDF2
    print(f"PyPDF2 imported successfully")
    print(f"PyPDF2 version: {PyPDF2.__version__}")
except ImportError as e:
    print(f"Failed to import PyPDF2: {e}")

try:
    import tkinter
    print("tkinter imported successfully")
except ImportError as e:
    print(f"Failed to import tkinter: {e}")

try:
    from utils import call_llm
    print("utils.call_llm imported successfully")
except ImportError as e:
    print(f"Failed to import utils.call_llm: {e}")

print("All imports test completed.")