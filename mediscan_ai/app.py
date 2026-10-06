"""
MediScan AI - Main Application Entry Point
Demonstrates: Flask application factory, OOP, modules, exception handling,
              database initialization, login management
"""
import os
import logging
from flask import Flask, render_template
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables before anything else
load_dotenv()

from models.database import db, User
from config import get_config
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.reports import reports_bp
from routes.api import api_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """
    Application factory pattern.
    Demonstrates: OOP, Flask, modules, configuration
    """
    app = Flask(__name__)

    # Load configuration
    config_class = get_config()
    app.config.from_object(config_class)

    # Override paths to be absolute relative to app root
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    app.config['CHARTS_FOLDER'] = os.path.join(app.root_path, 'static', 'generated_charts')

    # Ensure required directories exist
    _create_directories(app)

    # Initialize extensions
    db.init_app(app)

    # Login manager setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id: str):
        """Load user from database by ID"""
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(api_bp)

    # Initialize database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables initialized")

    # Error handlers
    _register_error_handlers(app)

    # Template context processors
    @app.context_processor
    def inject_globals():
        """Inject global variables into all templates"""
        from flask_login import current_user as cu
        from config import Config
        return {
            'app_name': 'MediScan AI',
            'app_version': '1.0.0',
            'ai_configured': Config.is_ai_configured(),
            'current_user': cu,
        }

    logger.info("MediScan AI application created successfully")
    return app


def _create_directories(app: Flask) -> None:
    """
    Create required application directories.
    Demonstrates: file I/O, os module, loops
    """
    directories = [
        app.config.get('UPLOAD_FOLDER'),
        app.config.get('CHARTS_FOLDER'),
        os.path.join(app.root_path, 'instance'),
    ]

    for directory in directories:
        if directory:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")


def _register_error_handlers(app: Flask) -> None:
    """
    Register HTTP error handlers.
    Demonstrates: Flask error handling, functions, branching
    """
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html',
                               code=403,
                               title='Access Denied',
                               message='You do not have permission to access this resource.'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html',
                               code=404,
                               title='Page Not Found',
                               message='The page you are looking for does not exist.'), 404

    @app.errorhandler(413)
    def file_too_large(e):
        return render_template('error.html',
                               code=413,
                               title='File Too Large',
                               message='The uploaded file exceeds the 10 MB size limit.'), 413

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Internal server error: {e}")
        return render_template('error.html',
                               code=500,
                               title='Server Error',
                               message='An unexpected error occurred. Please try again.'), 500


# Application instance
app = create_app()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'

    logger.info(f"Starting MediScan AI on http://127.0.0.1:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"AI configured: {app.config.get('AI_API_KEY', '') != ''}")

    app.run(host='0.0.0.0', port=port, debug=debug)
