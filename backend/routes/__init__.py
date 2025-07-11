# backend/routes/__init__.py

from .resources import resources_bp
from .sync import sync_bp
from .contribute import contribute_bp

def register_routes(app):
    app.register_blueprint(resources_bp)
    app.register_blueprint(sync_bp)
    app.register_blueprint(contribute_bp)
