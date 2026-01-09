from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)

# ---------- Helper Functions ----------
def time_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning ☀️"
    elif hour < 18:
        return "Good Afternoon 🌤️"
    else:
        return "Good Evening 🌙"

def personality_prediction(name):
    length = len(name)
    first_letter = name[0].lower()

    if length <= 4:
        personality = "Quick Thinker ⚡"
    elif length <= 7:
        personality = "Balanced & Calm 🌿"
    else:
        personality = "Strong Leader 💪"

    if first_letter in ["a", "s", "p", "r"]:
        trait = "Highly Motivated 🚀"
    elif first_letter in ["m", "n", "k"]:
        trait = "Creative Mind 🎨"
    else:
        trait = "Practical Thinker 🧠"

    return personality, trait

# ---------- Route ----------
@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        name = request.form.get("name")

        personality, trait = personality_prediction(name)

        result = {
            "original": name,
            "upper": name.upper(),
            "reverse": name[::-1],
            "length": len(name),
            "personality": personality,
            "trait": trait
        }

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Name Personality Analyzer</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="card shadow p-4">
                <h2 class="text-primary">🧠 Name Personality Analyzer</h2>
                <p>{{ greeting }}</p>

                <form method="POST">
                    <input type="text" name="name" class="form-control" placeholder="Enter your name" required>
                    <button class="btn btn-warning mt-3">Analyze</button>
                </form>

                {% if result %}
                <hr>
                <h4>🔍 Analysis Result</h4>
                <p><b>Original Name:</b> {{ result.original }}</p>
                <p><b>Upper Case:</b> {{ result.upper }}</p>
                <p><b>Reverse:</b> {{ result.reverse }}</p>
                <p><b>Length:</b> {{ result.length }}</p>

                <h5 class="mt-3">🎯 Personality Prediction</h5>
                <p><b>Type:</b> {{ result.personality }}</p>
                <p><b>Trait:</b> {{ result.trait }}</p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """, result=result, greeting=time_greeting())

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)