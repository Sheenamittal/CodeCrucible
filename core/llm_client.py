# core/llm_client.py

import os
import requests
import json
import time
import random
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = os.getenv("API_KEY")
MODEL = "llama3-70b-8192"

def get_refactoring_suggestion(code_snippet: str) -> dict:
    if not API_KEY:
        return {"error": "API_KEY not found."}

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    prompt = f"""
    You are an expert AI pair programmer. Your task is to analyze the following code snippet,
    identify any code smells or vulnerabilities, and provide a refactored version.

    Your response MUST be a single, valid JSON object with two keys:
    1. "refactored_code": A string containing the complete, refactored code.
    2. "explanation": A string explaining the key improvements you made.

    Problematic Code:
    ```python
    {code_snippet}
    ```
    """
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        response_data = response.json()
        if 'error' in response_data:
            return {"error": response_data['error'].get('message', 'Unknown API error')}
        content_string = response_data['choices'][0]['message']['content']
        return json.loads(content_string)
    except Exception as e:
        return {"error": f"API request for suggestion failed: {e}"}

def get_corrected_patch(original_code: str, failed_patch: str, test_error: str) -> dict:
    """
    Asks the LLM to generate a new patch based on a failed test.
    """
    if not API_KEY:
        return {"error": "API_KEY not found."}

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    prompt = f"""
    You are an expert debugging AI. Your previous attempt to refactor a function failed.
    The goal is to fix the original code, but your last patch broke the unit tests.

    Original Code:
    ```python
    {original_code}
    ```

    Your Failed Patch:
    ```python
    {failed_patch}
    ```

    The unit test failed with this error:
    ```
    {test_error}
    ```

    Please generate a new patch that fixes the original code's issue AND passes the unit tests.
    Your response MUST be a single, valid JSON object with the key "corrected_code".
    """
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "response_format": {"type": "json_object"},
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        response_data = response.json()
        if 'error' in response_data:
            return {"error": response_data['error'].get('message', 'Unknown API error')}
        content_string = response_data['choices'][0]['message']['content']
        return json.loads(content_string)
    except Exception as e:
        return {"error": f"API request for correction failed: {e}"}

def get_algorithmic_optimization(code_snippet: str) -> dict:
    """
    Sends a code snippet to an LLM and asks for an optimal algorithmic solution.
    """
    if not API_KEY:
        return {"error": "API_KEY not found. Please set it in your .env file."}

    headers = { "Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json" }

    prompt = f"""
    You are a world-class competitive programmer and algorithm expert, like a principal engineer at Google.
    Your task is to analyze the following Python function, which is likely a brute-force or suboptimal solution to a programming problem.

    1.  First, determine the time and space complexity (Big O notation) of the provided code.
    2.  Second, provide a new, optimally efficient version of the function. The new solution should be significantly better in terms of time complexity.
    3.  Third, explain the complexities of both the original and the new solution, and describe the algorithmic approach you used for the optimization (e.g., "Used a hash map for O(1) lookups," "Used a two-pointer approach," "Applied dynamic programming").

    Your response MUST be a single, valid JSON object with three keys:
    1.  "optimized_code": A string containing the complete, optimal code.
    2.  "explanation": A detailed explanation of the complexities and the new algorithm.
    3.  "original_complexity": A string describing the Big O of the original code (e.g., "Time: O(n^2), Space: O(1)").

    Problematic Code:
    ```python
    {code_snippet}
    ```
    """

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        response_data = response.json()

        if 'error' in response_data:
            return {"error": response_data['error'].get('message', 'Unknown API error')}

        content_string = response_data['choices'][0]['message']['content']
        return json.loads(content_string)
    except Exception as e:
        return {"error": f"API request failed: {e}"}
    
# Add this new function to core/llm_client.py

def find_issues_in_code(code_snippet: str, language: str) -> dict:
    """
    Uses an LLM to find potential issues in a code snippet of any language.
    """
    if not API_KEY:
        return {"error": "API_KEY not found."}

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    prompt = f"""
    You are an expert static analysis tool. Analyze the following code snippet written in {language}.
    Identify the single most critical issue related to code smells (e.g., high complexity, duplication),
    performance bottlenecks, or common security vulnerabilities.

    If a critical issue is found, your response MUST be a single, valid JSON object with three keys:
    1. "issue_found": A boolean set to true.
    2. "description": A short, one-sentence description of the issue.
    3. "code_snippet": A string containing the exact lines of code with the issue.
    
    If no significant issues are found, return a JSON object with one key:
    1. "issue_found": A boolean set to false.

    Language: {language}
    Code:
    ```
    {code_snippet}
    ```
    """
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()
        response_data = response.json()
        if 'error' in response_data:
            return {"error": response_data['error'].get('message', 'Unknown API error')}
        content_string = response_data['choices'][0]['message']['content']
        return json.loads(content_string)
    except Exception as e:
        return {"error": f"API request for analysis failed: {e}"}