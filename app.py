# app.py - Python Backend for Discover India
# Run with: python app.py

# imports
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq
import os, json, re
app = Flask(__name__)
CORS(app)
# load env
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY, timeout=10.0)
 
@app.route("/recommend", methods=["POST"])
def recommend():
    """
    Receives: { "state": "Kerala", "interest": "beaches and coastal" }
    Returns:  { "places": [ { name, location, best_time, type, description, tip } ] }
    """
    data = request.get_json()

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

    # print("GROQ KEY:", GROQ_API_KEY) # Removed for security
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
            {"role": "user", "content": prompt}
        ]
    )

        raw = response.choices[0].message.content
        print("RAW RESPONSE:", raw)

    # Extract JSON safely
        match = re.search(r'\{[\s\S]*\}', raw)

        if not match:
            print("RAW OUTPUT:", raw)

            return jsonify({
                "places": [
                    {
                        "name": "Invalid AI Response",
                        "location": state,
                        "best_time": "N/A",
                        "type": "Error",
                        "description": "The AI response was invalid. This could be due to a temporary glitch.",
                        "tip": "Try a different combination of state and interest.",
                        "image_keyword": "travel",
                        "rating": "0.0"
                    }
                ]
            })
        cleaned = match.group(0)

        try:
            result = json.loads(cleaned)
        except Exception:
            print("JSON ERROR:", cleaned)

            return jsonify({
                "places": [
                    {
                        "name": "Data Formatting Error",
                        "location": state,
                        "best_time": "Unknown",
                        "type": "Error",
                        "description": "The AI provided a response, but it was in a format we couldn't understand. Please try again.",
                        "tip": "Refresh the page.",
                        "image_keyword": "puzzled",
                        "rating": "0.0"
                    }
                ]
            })
        return jsonify(result)
    except Exception as e:
        print("ERROR:", str(e))

        return jsonify({
            "places": [
                {
                    "name": "Destination Discovery Failed",
                    "location": state,
                    "best_time": "N/A",
                    "type": "Error",
                    "description": "We couldn't connect to the travel AI. Please ensure your GROQ_API_KEY is configured correctly in the .env file.",
                    "tip": "Check backend logs for details.",
                    "image_keyword": "travel",
                    "rating": "0.0"
                }
            ],
            "error": "API Connection Failed"
        })
    
@app.route("/")
def home():
    return render_template("index.html")


# if __name__ == "__main__":
#     print("Starting Discover India backend...")
#     print("📍 Running at http://localhost:5000")
#     print("🛑 Press Ctrl+C to stop\n")
#     app.run(debug=True, port=5000)
# print("GROQ KEY:", GROQ_API_KEY)
if __name__ == "__main__":
    print("Starting Discover India backend on Hugging Face...")
    # Hugging Face requires port 7860 to show your website
    app.run(host="0.0.0.0", port=7860)