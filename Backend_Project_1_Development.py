from flask import Flask, request, render_template_string
import re

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Regex101++ Matcher</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f6f8; padding: 30px; }
        .container { max-width: 900px; margin: auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h1 { text-align: center; }
        textarea, input { width: 100%; padding: 10px; margin-top: 8px; font-size: 14px; }
        button { margin-top: 15px; padding: 10px 20px; font-size: 16px; cursor: pointer; }
        .match { background: #d1f7c4; padding: 3px 6px; border-radius: 4px; margin: 2px; display: inline-block; }
        .error { color: red; margin-top: 10px; }
        .results { margin-top: 20px; }
        .positions { font-size: 13px; color: #555; }
        .highlight span { background: yellow; padding: 2px; }
        .flags { margin-top: 10px; }
        .ml-box { margin-top: 20px; padding: 15px; background: #eef3ff; border-radius: 6px; }
    </style>
</head>
<body>
<div class="container">
    <h1>Regex101++ Web Matcher</h1>

    <form method="post">
        <label><strong>Regular Expression</strong></label>
        <input type="text" name="regex" value="{{ regex or '' }}" required>

        <div class="flags">
            <label><input type="checkbox" name="ignorecase" {% if ignorecase %}checked{% endif %}> Ignore Case (i)</label>
            <label><input type="checkbox" name="multiline" {% if multiline %}checked{% endif %}> Multiline (m)</label>
            <label><input type="checkbox" name="dotall" {% if dotall %}checked{% endif %}> Dot All (s)</label>
        </div>

        <label><strong>Test String</strong></label>
        <textarea name="text" rows="6" required>{{ text or '' }}</textarea>

        <button type="submit">Test Regex</button>
    </form>

    {% if error %}
        <div class="error">{{ error }}</div>
    {% endif %}

    {% if matches is not none %}
        <div class="results">
            <h3>Matches ({{ matches|length }})</h3>
            {% for m in matches %}
                <div class="match">{{ m[0] }}</div>
                <div class="positions">Start: {{ m[1] }}, End: {{ m[2] }}</div>
            {% endfor %}
        </div>

        <h3>Highlighted Output</h3>
        <div class="highlight">{{ highlighted|safe }}</div>

        <div class="ml-box">
            <h3>ML / Smart Analysis</h3>
            <p><strong>Pattern Complexity:</strong> {{ complexity }}</p>
            <p><strong>Suggested Use Case:</strong> {{ suggestion }}</p>
        </div>
    {% endif %}
</div>
</body>
</html>
"""


def analyze_regex(pattern):
    score = 0
    if ".*" in pattern or ".+" in pattern:
        score += 2
    if "(" in pattern and ")" in pattern:
        score += 1
    if "|" in pattern:
        score += 1

    if score >= 4:
        return "High", "May cause performance issues (backtracking risk)"
    elif score >= 2:
        return "Medium", "Safe for moderate input sizes"
    else:
        return "Low", "Efficient and safe regex"


@app.route('/', methods=['GET', 'POST'])
def index():
    matches = None
    error = None
    regex = None
    text = None
    highlighted = ""
    complexity = None
    suggestion = None

    ignorecase = multiline = dotall = False

    if request.method == 'POST':
        regex = request.form.get('regex')
        text = request.form.get('text')

        flags = 0
        if request.form.get('ignorecase'):
            flags |= re.IGNORECASE
            ignorecase = True
        if request.form.get('multiline'):
            flags |= re.MULTILINE
            multiline = True
        if request.form.get('dotall'):
            flags |= re.DOTALL
            dotall = True

        try:
            matches = [(m.group(), m.start(), m.end()) for m in re.finditer(regex, text, flags)]

            # Highlight matches
            highlighted = text
            for m in reversed(list(re.finditer(regex, text, flags))):
                highlighted = highlighted[:m.start()] + f"<span>{m.group()}</span>" + highlighted[m.end():]

            complexity, suggestion = analyze_regex(regex)

        except re.error as e:
            error = f"Regex Error: {e}"

    return render_template_string(
        HTML_TEMPLATE,
        matches=matches,
        error=error,
        regex=regex,
        text=text,
        highlighted=highlighted,
        complexity=complexity,
        suggestion=suggestion,
        ignorecase=ignorecase,
        multiline=multiline,
        dotall=dotall
    )


if __name__ == '__main__':
    app.run(debug=True)
