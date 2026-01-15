from flask import Flask, request, render_template_string, jsonify
import re
import time

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Regex101 AI++</title>
  <style>
    body { font-family: 'Segoe UI', Arial; background:#f8fafc; padding:25px; margin:0 }
    .box { background:#fff; padding:25px; max-width:900px; margin:auto; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.08) }
    h2 { text-align:center; color:#1e293b; margin-top:0 }
    label { display:block; margin-top:16px; font-weight:600; color:#334155 }
    input, textarea { width:100%; padding:10px; margin-top:6px; border:1px solid #cbd5e1; border-radius:6px; font-size:15px }
    button { background:#3b82f6; color:white; border:none; padding:12px 24px; margin-top:15px; border-radius:6px; cursor:pointer; font-size:16px; width:100% }
    button:hover { background:#2563eb }
    .match { background:#fef08a; padding:2px 4px; border-radius:4px; font-weight:bold }
    .bar-container { height:24px; background:#e2e8f0; border-radius:12px; overflow:hidden; margin:10px 0 }
    .perf-fill { height:100%; background:linear-gradient(to right, #10b981, #f59e0b, #ef4444); transition: width 0.4s ease }
    .error { color:#ef4444; margin-top:10px; font-weight:500 }
    .suggestion { background:#f0f9ff; padding:14px; border-left:4px solid #3b82f6; margin-top:15px; border-radius:0 6px 6px 0 }
    #matches { font-family:monospace; background:#f1f5f9; padding:12px; border-radius:6px; white-space:pre-wrap }
    #highlight { line-height:1.6; padding:12px; background:#f8fafc; border:1px dashed #cbd5e1; border-radius:6px; margin-top:8px }
  </style>
</head>
<body>
<div class='box'>
  <h2>🔥 Regex101 AI++</h2>

  <label>Regular Expression</label>
  <input id='regex' placeholder='e.g. \\b\\d{3}-\\d{2}-\\d{4}\\b'>

  <label>Test String</label>
  <textarea id='text' rows='5' placeholder='Paste your text here...'>The future is multiplanetary. Contact: elon@spacex.com or call +1-555-123-4567.</textarea>

  <label>NLP → Regex (AI Assistant)</label>
  <input id='nlp' placeholder='e.g. extract phone numbers, find emails, get URLs'>

  <button onclick='run()'>⚡ Run Regex Analysis</button>

  <div id='error' class='error'></div>

  <h3>Matches (<span id='match-count'>0</span>)</h3>
  <div id='matches'>No matches yet.</div>

  <h3>Highlighted Output</h3>
  <div id='highlight'>Your text will appear here with matches highlighted.</div>

  <h3>Performance Risk Score</h3>
  <div class='bar-container'><div id='perf' class='perf-fill' style='width:0%'></div></div>
  <div id='perf-label' style='font-size:14px; color:#64748b; margin-top:4px'>Safe</div>

  <div class='suggestion'>
    <strong>AI Recommendation:</strong> <span id='suggest'>Enter a regex or use NLP to get suggestions.</span>
  </div>
</div>

<script>
async function run(){
  const r = document.getElementById('regex').value;
  const t = document.getElementById('text').value;
  const n = document.getElementById('nlp').value;

  const res = await fetch('/api/live', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({regex: r, text: t, nlp: n})
  });
  const d = await res.json();

  // Clear previous
  document.getElementById('error').innerText = d.error || '';
  
  if (d.error) {
    document.getElementById('matches').innerText = 'Fix the error above.';
    document.getElementById('highlight').innerHTML = '';
    return;
  }

  // Update matches
  document.getElementById('match-count').innerText = d.matches.length;
  document.getElementById('matches').innerText = d.matches.join('\\n') || 'None found';

  // Highlight
  document.getElementById('highlight').innerHTML = d.highlight || t;

  // Performance bar
  const score = d.score || 0;
  document.getElementById('perf').style.width = score + '%';
  let label = 'Safe';
  if (score > 80) label = '⚠️ High Risk (ReDoS)';
  else if (score > 50) label = 'Medium Risk';
  document.getElementById('perf-label').innerText = label;

  // Suggestion
  document.getElementById('suggest').innerText = d.suggestion || 'No suggestion.';
}
</script>
</body>
</html>
"""


# === NLP → REGEX ENGINE (Enhanced) ===
def nlp_to_regex(intent: str) -> str | None:
    intent = intent.lower().strip()
    patterns = {
        # Emails
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "emails": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        # Phone (US & generic)
        "phone": r"\+?1?-?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}",
        "phones": r"\+?1?-?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}",
        "number": r"\b\d+\b",
        "numbers": r"\b\d+\b",
        # URLs
        "url": r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?",
        "urls": r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?",
        # Dates (simple)
        "date": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        # Words (long)
        "word": r"\b\w{5,}\b",
        "words": r"\b\w{5,}\b",
        # Hashtags
        "hashtag": r"#\w+",
        # Mentions
        "mention": r"@\w+",
    }
    for key, pattern in patterns.items():
        if key in intent:
            return pattern
    return None


# === ML-BASED REGEX RECOMMENDER ===
def recommend_regex(text: str) -> tuple[str, str]:
    """Suggest a regex based on content analysis"""
    if re.search(r"@\w+\.\w+", text):
        return r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "Detected email-like patterns → extracting emails"
    elif re.search(r"\+?\d{10,}", text.replace(" ", "").replace("-", "")):
        return r"\+?1?-?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}", "Possible phone number detected"
    elif re.search(r"https?://", text):
        return r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?", "URLs found → extracting links"
    elif len([w for w in text.split() if w.istitle() and len(w) > 3]) > 2:
        return r"\b[A-Z][a-z]{3,}\b", "Many capitalized words → extracting proper nouns"
    else:
        return r"\b\w{5,}\b", "Default: extracting long words (likely meaningful terms)"


# === PERFORMANCE SCORER (ReDoS-aware) ===
def score_regex(pattern: str) -> int:
    score = 10
    # Nested quantifiers = high risk
    if re.search(r"$$[^)]*\*.*\*|$$[^)]*\+.*\+", pattern):
        score += 70
    # Repetition of group with alternation
    if re.search(r"$$[^)]*\|[^)]*$$[\*\+]", pattern):
        score += 60
    # .* or .+ (greedy dot)
    if ".*" in pattern or ".+" in pattern:
        score += 30
    # Alternation at top level
    if "|" in pattern and not pattern.startswith("(?"):
        score += 20
    # Capturing groups (not inherently bad, but can compound risk)
    if pattern.count("(") - pattern.count("(?:") > 2:
        score += 15
    return min(score, 100)


@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/live', methods=['POST'])
def live():
    data = request.get_json()
    regex = data.get('regex', '').strip()
    text = data.get('text', '')
    nlp = data.get('nlp', '').strip()

    # Step 1: Use NLP to generate regex if provided
    if nlp:
        generated = nlp_to_regex(nlp)
        if generated:
            regex = generated
        else:
            # Fallback: try ML recommender on text
            regex, suggestion = recommend_regex(text)
            return jsonify(
                error="NLP intent not recognized. Using smart recommendation.",
                regex=regex,
                matches=[],
                highlight="",
                score=score_regex(regex),
                suggestion=suggestion
            )

    # Step 2: Validate & run regex
    if not regex:
        return jsonify(error="Regex cannot be empty.", matches=[], highlight="", score=0, suggestion="")

    try:
        start = time.time()
        compiled = re.compile(regex)
        matches = [m.group() for m in compiled.finditer(text)]
        elapsed = (time.time() - start) * 1000  # ms

        # Timeout protection (basic)
        if elapsed > 1000:
            return jsonify(error="Regex took too long (>1s) – possible ReDoS!", matches=[], highlight="", score=100, suggestion="Avoid nested quantifiers like (a+)+")

        # Highlight matches
        highlight = text
        for m in reversed(list(compiled.finditer(text))):
            highlight = highlight[:m.start()] + f"<span class='match'>{m.group()}</span>" + highlight[m.end():]

        score = score_regex(regex)
        suggestion = (
            "✅ Safe for production." if score < 40 else
            "⚠️ Medium risk – test with large inputs." if score < 80 else
            "❌ High ReDoS risk! Avoid in user-facing apps."
        )

        return jsonify(
            matches=matches,
            highlight=highlight,
            score=score,
            suggestion=suggestion
        )

    except re.error as e:
        return jsonify(error=f"Invalid regex: {str(e)}", matches=[], highlight="", score=0, suggestion="")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)