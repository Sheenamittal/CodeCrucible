# Generative Code Refactoring and Vulnerability Detection Assistant

An AI-powered tool that analyzes GitHub repositories to suggest code improvements and detect vulnerabilities.

## Installation

1.  Clone this repository.
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Create a `.env` file and add your LLM API key:
    ```
    API_KEY=your_api_key_here
    ```