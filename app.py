# app.py - Python Backend for Discover India
# Run with: python app.py

import os, json, re, time, requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# load env
load_dotenv()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
PEXELS_API_KEY     = os.environ.get("PEXELS_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Free models on OpenRouter (tried in order)
MODELS = [
    "google/gemma-4-27b-it:free",
    "nvidia/nemotron-3.5-lightning:free",
    "google/gemma-4-31b-it:free",
    "liquid/lfm-2.5-2.6b:free",
]

MAX_RETRIES   = 3
BACKOFF_START = 2   # seconds


def call_openrouter_with_retry(prompt: str) -> str:
    """
    Try each model in MODELS with exponential backoff via OpenRouter.
    Returns the raw text content on success, raises on total failure.
    """
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set in .env")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:7860",
        "X-Title": "Discover India"
    }

    last_error = None
    for model in MODELS:
        delay = BACKOFF_START
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"[OpenRouter] Model={model} Attempt={attempt}")
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}]
                }
                res = requests.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                data = res.json()

                if res.status_code == 200 and data.get("choices"):
                    return data["choices"][0]["message"]["content"]

                # Rate-limit → back off
                if res.status_code in (429, 503):
                    print(f"[OpenRouter] Rate limited ({res.status_code}). Waiting {delay}s …")
                    time.sleep(delay)
                    delay *= 2
                    last_error = data
                    continue

                # Any other error → try next model
                print(f"[OpenRouter] Error on {model}: {res.status_code} {data}")
                last_error = data
                break

            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                if any(k in err_str for k in ("timeout", "connection")):
                    print(f"[OpenRouter] Network error ({e}). Waiting {delay}s …")
                    time.sleep(delay)
                    delay *= 2
                else:
                    print(f"[OpenRouter] Non-retriable error on {model}: {e}")
                    break

        print(f"[OpenRouter] All retries exhausted for {model}, trying next model …")

    raise RuntimeError(f"All OpenRouter models failed. Last error: {last_error}")


# ── /recommend ──────────────────────────────────────────────────────────────────
@app.route("/recommend", methods=["POST"])
def recommend():
    """
    Receives: { "state": "Kerala", "interest": "beaches and coastal" }
    Returns:  { "places": [ { name, location, best_time, type, description, tip } ] }
    """
    data     = request.get_json()
    state    = data.get("state", "Rajasthan")
    interest = data.get("interest", "heritage and history")

    prompt = f"""You are an expert Indian travel guide. Recommend 4 must-visit tourist places in {state}, India focused on {interest}.

Reply ONLY with a valid JSON object (no markdown, no code fences). Format:
{{
  "places": [
    {{
      "name": "Place Name",
      "location": "City or District, {state}",
      "best_time": "Month range",
      "type": "Category label (e.g. Fort, Beach, Temple)",
      "description": "3-4 engaging sentences about what makes this place special.",
      "tip": "One practical travel tip for visitors.",
      "image_keyword": "A specific keyword for searching a travel photo of this place",
      "rating": "A number between 4.5 and 5.0"
    }}
  ]
}}"""

    try:
        raw = call_openrouter_with_retry(prompt)
        print("RAW RESPONSE:", raw)

        # Extract JSON safely
        match = re.search(r'\{[\s\S]*\}', raw)
        if not match:
            print("RAW OUTPUT (no JSON found):", raw)
            return jsonify({
                "places": [{
                    "name": "Invalid AI Response", "location": state,
                    "best_time": "N/A", "type": "Error",
                    "description": "The AI response was invalid. This could be due to a temporary glitch.",
                    "tip": "Try a different combination of state and interest.",
                    "image_keyword": "travel", "rating": "0.0"
                }]
            })

        cleaned = match.group(0)
        try:
            result = json.loads(cleaned)
        except Exception:
            print("JSON PARSE ERROR:", cleaned)
            return jsonify({
                "places": [{
                    "name": "Data Formatting Error", "location": state,
                    "best_time": "Unknown", "type": "Error",
                    "description": "The AI provided a response, but it couldn't be parsed. Please try again.",
                    "tip": "Refresh the page.",
                    "image_keyword": "puzzled", "rating": "0.0"
                }]
            })

        return jsonify(result)

    except Exception as e:
        print("FATAL ERROR:", str(e))
        return jsonify({
            "places": [{
                "name": "Destination Discovery Failed", "location": state,
                "best_time": "N/A", "type": "Error",
                "description": "We couldn't reach the travel AI after multiple attempts. The service may be temporarily overloaded.",
                "tip": "Wait a moment and try again.",
                "image_keyword": "travel", "rating": "0.0"
            }],
            "error": str(e)
        })


# ── /search_images ──────────────────────────────────────────────────────────────
@app.route("/search_images", methods=["POST"])
def search_images():
    data  = request.get_json()
    query = data.get("query", "India Travel")

    if not PEXELS_API_KEY:
        return jsonify({"image": "/static/hero.png"})

    for attempt in range(1, 3):
        try:
            url  = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
            res  = requests.get(url, headers={"Authorization": PEXELS_API_KEY}, timeout=8)
            data = res.json()
            if data.get("photos"):
                return jsonify({"image": data["photos"][0]["src"]["large"]})
            break
        except Exception as e:
            print(f"PEXELS ERROR (attempt {attempt}):", e)
            time.sleep(1)

    return jsonify({"image": "/static/hero.png"})


# ── Static routes ───────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    print("Starting Discover India backend …")
    app.run(host="0.0.0.0", port=7860)