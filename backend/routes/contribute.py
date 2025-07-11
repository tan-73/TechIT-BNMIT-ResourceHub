# backend/routes/contribute.py

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import distinct
from io import BytesIO

from db.database import SessionLocal
from db.models import Resource
from services.file_utils import classify_file
from services.github_upload import create_github_pr
from services.drive_upload import upload_to_drive

contribute_bp = Blueprint("contribute", __name__)

@contribute_bp.route("/contribute", methods=["POST"])
def handle_contribution():
    files = request.files.getlist("files")
    department = request.form.get("department")
    semester = request.form.get("semester")
    subject = request.form.get("subject")
    type_label = request.form.get("type", "contributions")

    if not files or not department or not semester or not subject:
        return jsonify({"error": "Missing required fields"}), 400

    session = SessionLocal()
    responses = []

    for file in files:
        try:
            filename = secure_filename(file.filename)
            file_bytes = BytesIO(file.read())
            file.seek(0)
            category = classify_file(filename)

            if category == "code":
                link = create_github_pr(file_bytes, filename, department, semester, subject, type_label)
                source = "github"
            elif category == "binary":
                link = upload_to_drive(file_bytes, filename, department, semester, subject, type_label)
                source = "drive"
            else:
                responses.append({
                    "filename": filename,
                    "status": "skipped",
                    "reason": "unsupported file type"
                })
                continue

            # Save resource to DB
            resource = Resource(
                title=filename,
                link=link,
                subject=subject,
                department=department,
                semester=semester,
                type=type_label,
                source=source
            )
            session.add(resource)
            session.commit()

            responses.append({
                "filename": filename,
                "status": "success",
                "link": link,
                "source": source
            })

        except SQLAlchemyError as db_err:
            session.rollback()
            responses.append({
                "filename": filename,
                "status": "db_error",
                "error": str(db_err)
            })
        except Exception as e:
            responses.append({
                "filename": filename,
                "status": "error",
                "error": str(e)
            })

    session.close()
    return jsonify(responses), 200


@contribute_bp.route("/metadata", methods=["GET"])
def get_metadata():
    session = SessionLocal()
    try:
        departments = [row[0] for row in session.query(distinct(Resource.department)).all() if row[0]]
        semesters = [row[0] for row in session.query(distinct(Resource.semester)).all() if row[0]]
        subjects = [row[0] for row in session.query(distinct(Resource.subject)).all() if row[0]]

        return jsonify({
            "departments": departments,
            "semesters": semesters,
            "subjects": subjects
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
