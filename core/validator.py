import subprocess
import os
import sys
from rich.console import Console

console = Console()

def run_tests(repo_path: str) -> tuple[bool, str]:
    """
    Installs dependencies and runs the test suite, prioritizing a single,
    relevant 'tox' environment for speed and reliability.
    """
    try:
        # Strategy 1: Use 'tox' if available (professional standard)
        if os.path.exists(os.path.join(repo_path, "tox.ini")):
            console.log("Found 'tox.ini', running tests with a specific tox environment...")
            
            # Smartly select only the relevant tox environment (e.g., 'py312')
            py_version_env = f"py{sys.version_info.major}{sys.version_info.minor}"
            console.log(f"Attempting to run the '{py_version_env}' tox environment for a fast pass...")
            tox_command = ["tox", "-e", py_version_env]

            result = subprocess.run(
                tox_command, cwd=repo_path, capture_output=True, text=True, timeout=1200 # 20 min timeout
            )
            
            # If the specific environment passes, we are good
            if result.returncode == 0:
                return (True, "All tests passed successfully using the primary tox environment.")
            
            # If the specific version fails (e.g., not defined), try the default 'tox' command as a fallback
            console.log(f"[yellow]Tox environment '{py_version_env}' failed or was not found. Trying default 'tox' command...[/yellow]")
            result = subprocess.run(["tox"], cwd=repo_path, capture_output=True, text=True, timeout=1200)
            
            if result.returncode == 0:
                    return (True, "All tests passed successfully using default tox environment.")
            else:
                error_output = result.stdout + "\n" + result.stderr
                return (False, f"Tox execution failed:\n{error_output}")

        # Strategy 2: Fallback to manual pip + pytest if no tox.ini
        console.log("No 'tox.ini' found. Falling back to manual pip + pytest.")
        
        dependency_files = [
            "pyproject.toml", "requirements/dev.txt",
            "requirements-dev.txt", "requirements.txt"
        ]
        install_command = None
        for file in dependency_files:
            file_path = os.path.join(repo_path, file)
            if os.path.exists(file_path):
                console.log(f"Found dependency file: {file}")
                if file == "pyproject.toml":
                    install_command = ["pip", "install", "-e", ".[test,dev]"]
                else:
                    install_command = ["pip", "install", "-r", file]
                break

        if install_command:
            install_result = subprocess.run(install_command, cwd=repo_path, capture_output=True, text=True, timeout=900)
            if install_result.returncode != 0:
                return (False, f"Dependency installation failed:\n{install_result.stderr}")
            console.log("Dependencies installed successfully.")
        else:
            console.log("[yellow]No common dependency file found. Skipping installation.[/yellow]")
        
        test_command = ["pytest"]
        console.log(f"Running tests with command: '{' '.join(test_command)}'")
        result = subprocess.run(
            test_command, cwd=repo_path, capture_output=True, text=True, timeout=600
        )

        if result.returncode == 0:
            return (True, "All tests passed successfully.")
        else:
            error_output = result.stdout + "\n" + result.stderr
            return (False, error_output)

    except Exception as e:
        return (False, f"An exception occurred during the validation process: {e}")