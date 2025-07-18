# core/analyzer.py

import subprocess
import json
import os
from rich.console import Console

console = Console()

def get_function_code(file_path: str, func_name: str) -> str | None:
    """A helper to extract the source code of a single function."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        import ast
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                return ast.get_source_segment(source, node)
    except Exception:
        return None
    return None

def analyze_codebase(repo_path: str) -> list[dict]:
    """
    Orchestrates static analysis tools (Bandit, Radon) to find actionable issues.
    """
    issues_found = []
    
    # 1. Run Bandit for security vulnerabilities
    console.log("Running Bandit for security analysis...")
    try:
        bandit_cmd = f"bandit -r {repo_path} -f json"
        result = subprocess.run(bandit_cmd, shell=True, capture_output=True, text=True)
        bandit_results = json.loads(result.stdout)
        
        for issue in bandit_results.get("results", []):
            if issue['issue_severity'] in ["HIGH", "MEDIUM"]:
                issues_found.append({
                    "type": "Security Vulnerability",
                    "file_path": issue['filename'],
                    "line_number": issue['line_number'],
                    "function_name": issue['test_name'], # Not always accurate, but a start
                    "description": f"Bandit - {issue['issue_text']} (Severity: {issue['issue_severity']})",
                    "code_snippet": issue['code']
                })
    except Exception as e:
        console.print(f"[red]Error running Bandit: {e}[/red]")

    # 2. Run Radon for cyclomatic complexity
    console.log("Running Radon for complexity analysis...")
    try:
        radon_cmd = f"radon cc {repo_path} -j"
        result = subprocess.run(radon_cmd, shell=True, capture_output=True, text=True)
        radon_results = json.loads(result.stdout)

        for file, functions in radon_results.items():
            for func in functions:
                if func['rank'] in ['C', 'D', 'F']: # Ranks C and above are complex
                    func_code = get_function_code(file, func['name'])
                    if func_code:
                        issues_found.append({
                            "type": "High Complexity",
                            "file_path": file,
                            "line_number": func['lineno'],
                            "function_name": func['name'],
                            "description": f"Radon - High cyclomatic complexity of {func['complexity']} (Rank: {func['rank']})",
                            "code_snippet": func_code
                        })
    except Exception as e:
        console.print(f"[red]Error running Radon: {e}[/red]")
        
    return issues_found