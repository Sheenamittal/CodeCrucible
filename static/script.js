document.addEventListener('DOMContentLoaded', () => {
    // --- Initialize Input Code Editor ---
    const codeEditor = CodeMirror.fromTextArea(document.getElementById('code-snippet'), {
        lineNumbers: true,
        mode: 'python',
        theme: 'material-darker',
        indentUnit: 4
    });
    codeEditor.setValue("# Paste your Python function here to optimize it...");

    // --- Get Form and Result Elements ---
    const repoForm = document.getElementById('repo-form');
    const optimizeForm = document.getElementById('optimize-form');
    const resultsContainer = document.getElementById('results-container');
    const resultsOutput = document.getElementById('results-output');
    const repoSubmitButton = document.getElementById('repo-submit-button');
    const optimizeSubmitButton = document.getElementById('optimize-submit-button');

    // --- Add Event Listeners ---
    repoForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const repoUrl = document.getElementById('repo_url').value;
        handleApiRequest('/analyze-repo', { repo_url: repoUrl }, repoSubmitButton);
    });

    optimizeForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const code = codeEditor.getValue();
        handleApiRequest('/optimize-code', { code: code }, optimizeSubmitButton);
    });

    // --- Main API Handling Function ---
    async function handleApiRequest(endpoint, body, button) {
        showLoadingState(true, button);
        resultsOutput.innerHTML = '<p>Analyzing... This may take several minutes for a full repository.</p>';

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const data = await response.json();
            renderResults(data, endpoint);
        } catch (error) {
            renderError(error);
        } finally {
            showLoadingState(false, button);
        }
    }

    // --- UI Update Functions ---
    function showLoadingState(isLoading, button) {
        resultsContainer.setAttribute('aria-busy', isLoading ? 'true' : 'false');
        if (button) button.disabled = isLoading;
    }
    
    function renderError(error) {
        resultsOutput.innerHTML = `<h5>Error</h5><pre><code>${error.toString()}</code></pre>`;
    }

    function renderResults(data, endpoint) {
        resultsOutput.innerHTML = ''; 

        if (data.detail) { 
            renderError(data.detail);
            return;
        }

        if (endpoint === '/optimize-code') {
            renderOptimizationResult(data);
        } else if (endpoint === '/analyze-repo') {
            renderAnalysisReport(data);
        } else {
            resultsOutput.innerHTML = `<pre><code>${JSON.stringify(data, null, 2)}</code></pre>`;
        }
    }

    function renderOptimizationResult(data) {
        resultsOutput.innerHTML += `<h5>Original Complexity</h5><p>${data.original_complexity || 'N/A'}</p>`;
        resultsOutput.innerHTML += `<h5>Explanation</h5><p>${data.explanation || 'N/A'}</p>`;
        
        resultsOutput.innerHTML += `<h5>✨ Optimized Solution</h5>`;
        const codeDiv = document.createElement('div');
        resultsOutput.appendChild(codeDiv);
        CodeMirror(codeDiv, {
            value: data.optimized_code,
            mode: 'python',
            theme: 'material-darker',
            readOnly: true,
            lineNumbers: true
        });
    }

    function renderAnalysisReport(data) {
        const header = document.createElement('h4');
        header.textContent = data.message || 'Analysis Report';
        resultsOutput.appendChild(header);

        if (!data.issues || data.issues.length === 0) {
            resultsOutput.innerHTML += '<p>No significant issues were found to report.</p>';
            return;
        }

        data.issues.forEach(item => {
            if (!item.suggestion) return; // Skip issues where no suggestion was generated

            const details = document.createElement('details');
            details.open = true;
            
            const summary = document.createElement('summary');
            summary.textContent = item.description;
            details.appendChild(summary);

            const content = document.createElement('div');
            content.innerHTML = `<p><strong>File:</strong> ${item.file_path}</p>`;
            content.innerHTML += `<p><strong>Explanation:</strong> ${item.suggestion.explanation || 'N/A'}</p>`;
            
            const grid = document.createElement('div');
            grid.className = 'grid';

            // "Before" Code Block
            const beforeDiv = document.createElement('div');
            beforeDiv.innerHTML = '<h6>Original Code</h6>';
            const beforeCode = document.createElement('div');
            beforeDiv.appendChild(beforeCode);
            grid.appendChild(beforeDiv);
            
            // "After" Code Block
            const afterDiv = document.createElement('div');
            afterDiv.innerHTML = '<h6>✨ Refactored Code</h6>';
            const afterCode = document.createElement('div');
            afterDiv.appendChild(afterCode);
            grid.appendChild(afterDiv);

            content.appendChild(grid);
            details.appendChild(content);
            resultsOutput.appendChild(details);
            
            // Render the CodeMirror editors
            const lang = getLanguageFromType(item.type);
            CodeMirror(beforeCode, { value: item.code_snippet, mode: lang, theme: 'material-darker', readOnly: true, lineNumbers: true });
            CodeMirror(afterCode, { value: item.suggestion.refactored_code, mode: lang, theme: 'material-darker', readOnly: true, lineNumbers: true });
        });
    }
    
    function getLanguageFromType(typeString = '') {
        const lang = typeString.split(' ')[0].toLowerCase();
        // Map to CodeMirror modes
        const modeMap = {
            'c++': 'text/x-c++src',
            'java': 'text/x-java',
            'javascript': 'javascript',
            'html': 'htmlmixed',
            'css': 'css',
            'python': 'python'
        };
        return modeMap[lang] || 'text/plain';
    }
});