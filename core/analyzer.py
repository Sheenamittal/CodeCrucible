# core/analyzer.py

import os
from rich.console import Console
# The LLM client will now do the analysis
from .llm_client import find_issues_in_code 

console = Console()

# Map file extensions to language names for the LLM prompt
LANGUAGE_MAP = {
    ".py": "Python",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C++",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".html": "HTML",
    ".css": "CSS"
}

def analyze_codebase(repo_path: str) -> list[dict]:
    """
    Walks through a repository, identifies files of various languages,
    and uses an LLM to find the most critical issue in each file.
    """
    issues_found = []
    
    for subdir, _, files in os.walk(repo_path):
        for file in files:
            file_extension = os.path.splitext(file)[1]
            language = LANGUAGE_MAP.get(file_extension)

            # If the file type is one we support
            if language:
                file_path = os.path.join(subdir, file)
                console.log(f"Analyzing {language} file: {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # For simplicity, we analyze the whole file. A more advanced
                        # tool might break it into functions/classes first.
                        content = f.read()

                    # Skip very small files
                    if len(content.splitlines()) < 10:
                        continue
                    
                    # Use the LLM to find an issue
                    analysis_result = find_issues_in_code(content, language)

                    if analysis_result.get("issue_found"):
                        issues_found.append({
                            "type": f"{language} Issue",
                            "file_path": file_path,
                            "line_number": 1, # Placeholder, as we analyze the whole file
                            "function_name": os.path.basename(file_path),
                            "description": analysis_result.get("description"),
                            "code_snippet": analysis_result.get("code_snippet")
                        })
                except Exception as e:
                    console.print(f"[red]Error analyzing file {file_path}: {e}[/red]")
        
    return issues_found











# # core/analyzer.py

# import subprocess
# import json
# import os
# from rich.console import Console

# console = Console()

# def get_function_code(file_path: str, func_name: str) -> str | None:
#     """A helper to extract the source code of a single function."""
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             source = f.read()
#         import ast
#         tree = ast.parse(source)
#         for node in ast.walk(tree):
#             if isinstance(node, ast.FunctionDef) and node.name == func_name:
#                 return ast.get_source_segment(source, node)
#     except Exception:
#         return None
#     return None

# def analyze_codebase(repo_path: str) -> list[dict]:
#     """
#     Orchestrates static analysis tools (Bandit, Radon) to find actionable issues.
#     """
#     issues_found = []
    
#     # 1. Run Bandit for security vulnerabilities
#     console.log("Running Bandit for security analysis...")
#     try:
#         bandit_cmd = f"bandit -r {repo_path} -f json"
#         result = subprocess.run(bandit_cmd, shell=True, capture_output=True, text=True)
#         bandit_results = json.loads(result.stdout)
        
#         for issue in bandit_results.get("results", []):
#             if issue['issue_severity'] in ["HIGH", "MEDIUM"]:
#                 issues_found.append({
#                     "type": "Security Vulnerability",
#                     "file_path": issue['filename'],
#                     "line_number": issue['line_number'],
#                     "function_name": issue['test_name'], # Not always accurate, but a start
#                     "description": f"Bandit - {issue['issue_text']} (Severity: {issue['issue_severity']})",
#                     "code_snippet": issue['code']
#                 })
#     except Exception as e:
#         console.print(f"[red]Error running Bandit: {e}[/red]")

#     # 2. Run Radon for cyclomatic complexity
#     console.log("Running Radon for complexity analysis...")
#     try:
#         radon_cmd = f"radon cc {repo_path} -j"
#         result = subprocess.run(radon_cmd, shell=True, capture_output=True, text=True)
#         radon_results = json.loads(result.stdout)

#         for file, functions in radon_results.items():
#             for func in functions:
#                 if func['rank'] in ['C', 'D', 'F']: # Ranks C and above are complex
#                     func_code = get_function_code(file, func['name'])
#                     if func_code:
#                         issues_found.append({
#                             "type": "High Complexity",
#                             "file_path": file,
#                             "line_number": func['lineno'],
#                             "function_name": func['name'],
#                             "description": f"Radon - High cyclomatic complexity of {func['complexity']} (Rank: {func['rank']})",
#                             "code_snippet": func_code
#                         })
#     except Exception as e:
#         console.print(f"[red]Error running Radon: {e}[/red]")
        
#     return issues_found



