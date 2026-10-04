from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config
from app.models import db

jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for React frontend cross-origin requests
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.room_routes import room_bp
    from app.routes.guest_routes import guest_bp
    from app.routes.booking_routes import booking_bp
    from app.routes.cancellation_routes import cancellation_bp
    from app.routes.payment_routes import payment_bp
    from app.routes.analytics_routes import analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(guest_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(cancellation_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(analytics_bp)

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({'error': 'Internal server error occurred', 'status': 500}), 500

    @app.errorhandler(404)
    def not_found_error(e):
        return jsonify({'error': 'Requested API resource not found', 'status': 404}), 404

    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'system': 'Hotel Booking & Revenue Analytics API',
            'database': 'MySQL 8.0'
        }), 200

    return app
