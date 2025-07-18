# core/analyzer.py
import os
from rich.console import Console
from .llm_client import find_issues_in_code 

console = Console()

LANGUAGE_MAP = {
    ".py": "Python",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C++ Header",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".html": "HTML",
    ".css": "CSS"
}

def analyze_codebase(repo_path: str) -> list[dict]:
    """
    Walks through a repository and uses an LLM to find the most
    critical issue in each supported file.
    """
    issues_found = []
    
    for subdir, _, files in os.walk(repo_path):
        for file in files:
            file_extension = os.path.splitext(file)[1]
            language = LANGUAGE_MAP.get(file_extension)

            if language:
                file_path = os.path.join(subdir, file)
                console.log(f"Analyzing {language} file: {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if len(content.splitlines()) < 10:
                        continue
                    
                    analysis_result = find_issues_in_code(content, language)

                    if analysis_result.get("issue_found"):
                        issues_found.append({
                            "type": f"{language} Issue",
                            "file_path": file_path,
                            "description": analysis_result.get("description"),
                            "code_snippet": analysis_result.get("code_snippet")
                        })
                except Exception as e:
                    console.print(f"[red]Error analyzing file {file_path}: {e}[/red]")
        
    return issues_found