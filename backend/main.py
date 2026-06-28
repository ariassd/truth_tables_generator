import os
from dotenv import load_dotenv
from flask import (
    Blueprint,
    Flask,
    request,
    jsonify,
    render_template,
    send_from_directory,
)
from truth_table import compute_truth_table

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "dist"))
PUBLIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "public"))

app = Flask(__name__, template_folder=DIST_DIR, static_folder=DIST_DIR)
api_bp = Blueprint("api", __name__, url_prefix="/api")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/public/<path:path>")
def serve_static(path):
    return send_from_directory(PUBLIC_DIR, path)


@app.route("/<path:path>")
def serve_static_pu(path):
    return send_from_directory(DIST_DIR, path)


@api_bp.route("/evaluate", methods=["POST"])
def evaluate_web():
    data = request.get_json()
    expression = data.get("expression", "").strip()
    if not expression:
        return jsonify({"error": "No expression provided"}), 400
    try:
        result = compute_truth_table(expression)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


app.register_blueprint(api_bp)
if __name__ == "__main__":
    is_develop = os.getenv("APP_ENV", "DEV") == "DEV"
    port = int(os.getenv("PORT", 8000))
    app.run(debug=is_develop, host="0.0.0.0", port=port)
