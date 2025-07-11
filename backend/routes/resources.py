# backend/routes/resources.py

from flask import Blueprint, request, jsonify
from sqlalchemy import or_, func
from db.database import SessionLocal
from db.models import Resource

resources_bp = Blueprint("resources", __name__)

@resources_bp.route("/resources/search", methods=["GET"])
def search_resources():
    session = SessionLocal()
    try:
        query = request.args.get("q", "")
        department = request.args.get("department")
        semester = request.args.get("semester")
        type_ = request.args.get("type")
        show = request.args.get("show")  # "All", "Files only", "Folders only"
        sort_by = request.args.get("sort_by", "date")  # or "title"
        order = request.args.get("order", "desc")

        base_query = session.query(Resource)

        # Full-text search using PostgreSQL tsvector
        if query:
            ts_query = func.plainto_tsquery(query)
            results = base_query.filter(Resource.search_vector.op("@@")(ts_query))
            
            if results.count() == 0:
                pattern = f"%{query}%"
                results = base_query.filter(
                    or_(
                        Resource.title.ilike(pattern),
                        Resource.subject.ilike(pattern),
                        Resource.department.ilike(pattern),
                        Resource.semester.ilike(pattern)
                    )
                )
        else:
            results = base_query

        # Filters
        if department and department.lower() != "all":
            results = results.filter(Resource.department.ilike(department))
        if semester and semester.lower() != "all":
            results = results.filter(Resource.semester.ilike(semester))
        if type_ and type_.lower() != "all":
            results = results.filter(Resource.type.ilike(type_))
        if show == "Files only":
            results = results.filter(Resource.type != "folder")
        elif show == "Folders only":
            results = results.filter(Resource.type == "folder")

        # Sorting
        sort_col = Resource.last_updated if sort_by == "date" else Resource.title
        sort_col = sort_col.desc() if order == "desc" else sort_col.asc()
        results = results.order_by(sort_col)

        return jsonify([
            {
                "id": r.id,
                "title": r.title,
                "subject": r.subject,
                "semester": r.semester,
                "department": r.department,
                "type": r.type,
                "source": r.source,
                "link": r.link,
                "last_updated": r.last_updated.isoformat()
            }
            for r in results.all()
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@resources_bp.route("/resources/metadata", methods=["GET"])
def get_metadata():
    session = SessionLocal()
    try:
        departments = [row[0] for row in session.query(Resource.department).distinct().all() if row[0]]
        semesters = [row[0] for row in session.query(Resource.semester).distinct().all() if row[0]]
        subjects = [row[0] for row in session.query(Resource.subject).distinct().all() if row[0]]
        return jsonify({
            "departments": departments,
            "semesters": semesters,
            "subjects": subjects
        })
    except Exception as e:
        print("[!] Metadata fetch error:", e)
        return jsonify({"error": "Metadata fetch failed"}), 500
    finally:
        session.close()
