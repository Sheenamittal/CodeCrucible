# core/validator.py
from rich.console import Console

console = Console()

def run_tests(repo_path: str) -> tuple[bool, str]:
    """
    This validation step is now disabled to support a unified, LLM-first
    analysis for all languages without environment conflicts.
    """
    console.log("[yellow]Test validation is disabled to ensure multi-language compatibility.[/yellow]")
    return (True, "Skipped test validation.")




# import subprocess
# import os
# import sys
# from rich.console import Console

# console = Console()

# def is_python_project(repo_path: str) -> bool:
#     """Check if a repository seems to be a Python project."""
#     # Look for key Python files at the root level
#     for file in ["pyproject.toml", "requirements.txt", "tox.ini", "setup.py"]:
#         if os.path.exists(os.path.join(repo_path, file)):
#             return True
    
#     # As a fallback, check for a high number of .py files
#     py_files = sum(1 for root, _, files in os.walk(repo_path) for f in files if f.endswith('.py'))
#     return py_files > 20 # Arbitrary threshold for what constitutes a "Python project"

# def run_tests(repo_path: str) -> tuple[bool, str]:
#     """
#     Installs dependencies and runs the test suite, but only for Python projects.
#     """
#     # --- NEW: Check if this is a Python project before doing anything ---
#     if not is_python_project(repo_path):
#         console.log("[yellow]Non-Python project detected. Skipping test validation.[/yellow]")
#         return (True, "Skipped validation for non-Python project.")
#     # --- END NEW BLOCK ---

#     try:
#         # Strategy 1: Use 'tox' if available
#         if os.path.exists(os.path.join(repo_path, "tox.ini")):
#             # ... (rest of the tox logic is the same) ...
#             console.log("Found 'tox.ini', running tests with a specific tox environment...")
#             py_version_env = f"py{sys.version_info.major}{sys.version_info.minor}"
#             tox_command = ["tox", "-e", py_version_env]
#             result = subprocess.run(tox_command, cwd=repo_path, capture_output=True, text=True, timeout=1200)
#             if result.returncode == 0:
#                 return (True, "All tests passed successfully using the primary tox environment.")
#             else:
#                 return (False, f"Tox execution failed for '{py_version_env}':\n{result.stdout}\n{result.stderr}")

#         # Strategy 2: Fallback to manual pip + pytest
#         console.log("No 'tox.ini' found. Falling back to manual pip + pytest.")
#         dependency_files = ["pyproject.toml", "requirements.txt"] # Simplified for clarity
#         install_command = None
#         for file in dependency_files:
#             file_path = os.path.join(repo_path, file)
#             if os.path.exists(file_path):
#                 if file == "pyproject.toml":
#                     install_command = ["pip", "install", "-e", ".[test,dev]"]
#                 else:
#                     install_command = ["pip", "install", "-r", file]
#                 break

#         if install_command:
#             install_result = subprocess.run(install_command, cwd=repo_path, capture_output=True, text=True, timeout=900)
#             if install_result.returncode != 0:
#                 return (False, f"Dependency installation failed:\n{install_result.stderr}")
#             console.log("Dependencies installed successfully.")
        
#         test_command = ["pytest"]
#         result = subprocess.run(test_command, cwd=repo_path, capture_output=True, text=True, timeout=600)

#         if result.returncode == 0:
#             return (True, "All tests passed successfully.")
#         else:
#             return (False, f"Pytest execution failed:\n{result.stdout}\n{result.stderr}")

#     except Exception as e:
#         return (False, f"An exception occurred during the validation process: {e}")