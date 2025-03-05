from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import google.generativeai as genai

gemini_bp = Blueprint('gemini', __name__)
model = genai.GenerativeModel("gemini-2.0-flash")

@gemini_bp.route("/ask_gemini", methods=["POST"])
@login_required
def ask_gemini():
    try:
        data = request.get_json()
        user_input = data.get("query") if data else None
        
        if not user_input:
            return jsonify({"error": "No query provided"}), 400

        response = model.generate_content(user_input)
        return jsonify({"response": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@gemini_bp.route("/gemini")
@login_required
def gemini_page():
    return render_template("gemini.html", title="gemini")