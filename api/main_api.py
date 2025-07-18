# api/main_api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import shutil

# Import your core logic
from core.git_handler import clone_repo
from core.analyzer import analyze_codebase
from core.llm_client import get_refactoring_suggestion, get_corrected_patch, get_algorithmic_optimization
from core.validator import run_tests

app = FastAPI(title="RefactorGen API")

class RepoRequest(BaseModel):
    repo_url: str

class CodeRequest(BaseModel):
    code: str

@app.post("/analyze-repo")
async def analyze_repository(request: RepoRequest):
    """
    The main endpoint to clone, analyze, patch, and validate a repository.
    """
    repo_path = "temp_repo"
    if not clone_repo(request.repo_url, repo_path):
        raise HTTPException(status_code=400, detail="Failed to clone repository.")

    try:
        # 1. Run baseline tests
        tests_ok, diagnostics = run_tests(repo_path)
        if not tests_ok:
            raise HTTPException(status_code=400, detail=f"Repository's initial test suite failed. Diagnostics:\n{diagnostics}")
            
        # 2. Analyze for issues
        issues = analyze_codebase(repo_path)
        if not issues:
            return {"message": "No high-priority issues found to fix."}
        
        final_report = []

        # 3. Loop through issues and attempt to fix them
        for issue in issues:
            report_entry = {"issue": issue, "status": "Pending"}
            
            # Get initial suggestion
            suggestion = get_refactoring_suggestion(issue['code_snippet'])
            
            if "error" in suggestion or not suggestion.get("refactored_code"):
                report_entry["status"] = "Suggestion Failed"
                final_report.append(report_entry)
                continue
            
            # Read original file content
            original_file_content = ""
            with open(issue['file_path'], 'r', encoding='utf-8') as f:
                original_file_content = f.read()
            
            # Apply first patch
            first_patch_code = suggestion['refactored_code']
            patched_code = original_file_content.replace(issue['code_snippet'], first_patch_code)
            with open(issue['file_path'], 'w', encoding='utf-8') as f:
                f.write(patched_code)
            
            # Validate first patch
            tests_ok, diagnostics = run_tests(repo_path)
            
            if tests_ok:
                report_entry["status"] = "✅ Verified & Patched"
                report_entry["solution"] = suggestion
            else:
                # Self-Correction Loop
                report_entry["status"] = "Correction Attempted"
                correction = get_corrected_patch(issue['code_snippet'], first_patch_code, diagnostics)
                
                if "error" in correction or not correction.get("corrected_code"):
                    report_entry["status"] = "❌ Correction Failed"
                else:
                    # Apply corrected patch
                    second_patch_code = correction['corrected_code']
                    corrected_patched_code = original_file_content.replace(issue['code_snippet'], second_patch_code)
                    with open(issue['file_path'], 'w', encoding='utf-8') as f:
                        f.write(corrected_patched_code)
                    
                    # Final validation
                    final_tests_ok, _ = run_tests(repo_path)
                    if final_tests_ok:
                        report_entry["status"] = "✅ Verified on 2nd Attempt"
                        report_entry["solution"] = correction
                    else:
                        report_entry["status"] = "❌ Rejected: Both patches failed tests"

            # IMPORTANT: Revert to the original state for the next issue
            with open(issue['file_path'], 'w', encoding='utf-8') as f:
                f.write(original_file_content)
            
            final_report.append(report_entry)

        return final_report

    finally:
        # Clean up the cloned repo
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)

@app.post("/optimize-code")
async def optimize_code_snippet(request: CodeRequest):
    # ... (This endpoint's code is fine and remains the same) ...
    if not request.code or not isinstance(request.code, str) or len(request.code) < 10:
        raise HTTPException(status_code=422, detail="A valid 'code' string is required.")
    optimization_data = get_algorithmic_optimization(request.code)
    if "error" in optimization_data:
        raise HTTPException(status_code=500, detail=optimization_data["error"])
    return optimization_data

@app.get("/")
def read_root():
    return {"message": "RefactorGen API is running. Go to /docs for the API documentation."}