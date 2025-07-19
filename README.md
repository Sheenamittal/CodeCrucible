# RefactorGen AI Assistant

![Python Version](https://img.shields.io/badge/python-3.12-blue)
![Framework](https://img.shields.io/badge/framework-FastAPI-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

An AI-powered, full-stack application that analyzes, refactors, and optimizes code across multiple languages, acting as an intelligent pair programmer.

---

##  Demo

![RefactorGen Demo](https://via.placeholder.com/800x450.png?text=Your+UI+Demo+Goes+Here)

## Overview

RefactorGen is a tool designed to meet the modern demands of software development. It goes beyond simple linting by leveraging a powerful Large Language Model (LLM) to perform a deep semantic analysis of codebases. It can identify complex issues—from security vulnerabilities to algorithmic inefficiencies—and provide actionable, refactored code suggestions in a clean, interactive user interface.

This project was built to explore the challenges of creating a reliable, multi-language AI assistant, focusing on a robust backend API and a polished user experience.

## Features

* **Multi-Language Code Analysis:** Analyzes code in Python, Java, C++, JavaScript, HTML, and CSS using a flexible, LLM-based approach.
* **AI-Powered Refactoring:** Identifies code smells and vulnerabilities and provides intelligent, refactored code snippets with clear explanations.
* **Algorithmic Optimization:** A dedicated endpoint analyzes the time and space complexity of Python functions and suggests optimal solutions.
* **Interactive Web UI:** A clean, modern frontend built with vanilla HTML/CSS/JS that includes:
    * **CodeMirror Editors:** For professional-grade code input and syntax highlighting.
    * **"Before & After" View:** A side-by-side comparison of the original and refactored code.
* **RESTful API Backend:** Built with FastAPI, providing a scalable and well-documented service.
* **Robust Git Repository Handling:** Efficiently clones repositories using shallow clones and skips large files to ensure fast analysis.

## Architecture

The project is a full-stack application with a clear separation between the backend service and the frontend interface.

```mermaid
graph TD
    A["Frontend UI (HTML, CSS, JS, CodeMirror)"] -->|HTTP POST Request| B("FastAPI Backend /analyze-repo");
    B --> C{"Git Handler (Clones Repo)"};
    C --> D["Analyzer (Finds issues with LLM)"];
    D --> E["LLM Client (Gets refactoring)"];
    E --> B;
    B -->|JSON Response| A;