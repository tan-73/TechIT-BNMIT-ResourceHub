# backend/routes/sync.py

from flask import Blueprint, jsonify
from services.github_scanner import run_github_sync
from services.drive_scanner import run_drive_sync

sync_bp = Blueprint("sync", __name__)

@sync_bp.route("/sync/github", methods=["POST"])
def sync_github():
    try:
        run_github_sync()
        return jsonify({"message": "✅ GitHub sync completed."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sync_bp.route("/sync/drive", methods=["POST"])
def sync_drive():
    try:
        run_drive_sync()
        return jsonify({"message": "✅ Google Drive sync completed."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
