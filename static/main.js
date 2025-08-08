// LinkedIn Profile Analyzer - Main JS
// Handles form submission, output formatting, and user feedback

/**
 * Formats AI output (Markdown-like) to HTML for display.
 * Supports headings, lists, and bold text.
 * @param {string} text
 * @returns {string} HTML
 */
function formatAIOutput(text) {
    let html = text
        .replace(/^### (.*)$/gm, '<h3>$1</h3>')
        .replace(/^## (.*)$/gm, '<h3>$1</h3>')
        .replace(/^# (.*)$/gm, '<h2>$1</h2>')
        .replace(/\n- (.*)/g, '\n<ul><li>$1</li></ul>')
        .replace(/^- (.*)$/gm, '<ul><li>$1</li></ul>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Merge adjacent <ul>s
    html = html.replace(/<\/ul>\s*<ul>/g, '');
    return html;
}

// Only attach if form exists (for progressive enhancement)
const analyzeForm = document.getElementById('analyze-form');
const loader = document.getElementById('loader');
const mainContent = document.getElementById('main-content');
if (analyzeForm) {
    analyzeForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);

        // Show loader immediately
        if (loader) {
            loader.style.display = 'flex';
            loader.classList.add('fade-in');
        }

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (data.redirect) {
                window.location.href = data.redirect;
            } else if (data.error) {
                alert(data.error);
                if (loader) loader.style.display = 'none';
            } else {
                alert('Unexpected error.');
                if (loader) loader.style.display = 'none';
            }
        } catch (err) {
            // Graceful network error handling
            alert('Network error. Please check your connection and try again.');
            if (loader) loader.style.display = 'none';
        }
    });
}
