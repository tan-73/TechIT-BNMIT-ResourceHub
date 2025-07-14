# backend/app.py

from flask import Flask
from routes import register_routes
from config import Config
from db import models  # ✅ Ensure models are loaded before DB use
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for frontend-backend interaction (e.g., Streamlit)

app.config.from_object(Config)
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
