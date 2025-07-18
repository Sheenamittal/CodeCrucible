# api/main_api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import shutil
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from core.git_handler import clone_repo
from core.analyzer import analyze_codebase
from core.llm_client import get_refactoring_suggestion, get_algorithmic_optimization # No longer need get_corrected_patch for this simplified flow
from core.validator import run_tests

app = FastAPI(title="RefactorGen API")

app.mount("/static", StaticFiles(directory="static"), name="static")

class RepoRequest(BaseModel):
    repo_url: str

class CodeRequest(BaseModel):
    code: str

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/analyze-repo")
async def analyze_repository(request: RepoRequest):
    repo_path = "temp_repo"
    if not clone_repo(request.repo_url, repo_path):
        raise HTTPException(status_code=400, detail="Failed to clone repository.")

    try:
        tests_ok, diagnostics = run_tests(repo_path)
        if not tests_ok:
            raise HTTPException(status_code=400, detail=f"Repository's test suite failed. Diagnostics:\n{diagnostics}")
            
        # --- NEW: Two-Step AI Logic ---
        # 1. Find issues first
        issues = analyze_codebase(repo_path)
        if not issues:
            return {"message": "Analysis complete. No high-priority issues found."}
        
        # 2. For each issue found, get a refactoring suggestion
        for issue in issues:
            suggestion = get_refactoring_suggestion(issue['code_snippet'])
            if "error" not in suggestion:
                issue['suggestion'] = suggestion # Attach the suggestion to the issue object
        
        return {"message": f"Analysis complete. Found {len(issues)} potential improvements.", "issues": issues}

    finally:
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)

@app.post("/optimize-code")
async def optimize_code_snippet(request: CodeRequest):
    # This logic remains the same
    if not request.code or not isinstance(request.code, str) or len(request.code) < 10:
        raise HTTPException(status_code=422, detail="A valid 'code' string is required.")
    optimization_data = get_algorithmic_optimization(request.code)
    if "error" in optimization_data:
        raise HTTPException(status_code=500, detail=optimization_data["error"])
    return optimization_data