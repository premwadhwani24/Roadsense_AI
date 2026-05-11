"""
Authentication module for RoadSense AI
Handles user login, JWT tokens, and role-based access control
"""
import os
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from database import DatabaseManager

# Default admin user credentials
DEFAULT_ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin@roadsense.com")
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "password123")
DEFAULT_ADMIN_EMAIL = "admin@roadsense.com"

def setup_auth(app):
    """Configure JWT and add default admin user"""
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    # Allow tokens in cookies so OAuth flow can set a cookie after external login
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False

    jwt = JWTManager(app)
    
    # Add default admin user if not exists
    admin = DatabaseManager.get_user(DEFAULT_ADMIN_USERNAME)
    if not admin:
        admin_hash = generate_password_hash(DEFAULT_ADMIN_PASSWORD)
        DatabaseManager.add_user(
            username=DEFAULT_ADMIN_USERNAME,
            email=DEFAULT_ADMIN_EMAIL,
            password_hash=admin_hash,
            role='admin'
        )
        print(f"Default admin user created: {DEFAULT_ADMIN_USERNAME}")
    
    return jwt


def create_or_get_oauth_user(email: str, name: str = None, role: str = 'viewer'):
    """Find user by email or create a new user for OAuth logins."""
    user = DatabaseManager.get_user_by_email(email)
    if user:
        return user

    # Derive username from email
    base_username = email.split('@')[0]
    username = base_username
    suffix = 1
    while DatabaseManager.get_user(username):
        username = f"{base_username}{suffix}"
        suffix += 1

    # Create a random password hash for oauth users (not used for login)
    from werkzeug.security import generate_password_hash
    import os as _os
    random_pw = _os.urandom(24).hex()
    password_hash = generate_password_hash(random_pw)

    user_id = DatabaseManager.add_user(username=username, email=email, password_hash=password_hash, role=role)
    return DatabaseManager.get_user(username)

def check_user_role(required_role: str):
    """Decorator to check if user has required role"""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            claims = get_jwt()
            user_role = claims.get('role')
            
            role_hierarchy = {'admin': 0, 'engineer': 1, 'viewer': 2}
            if role_hierarchy.get(user_role, 99) > role_hierarchy.get(required_role, 99):
                return {'error': 'Insufficient permissions'}, 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def authenticate_user(username: str, password: str):
    """Authenticate user and return JWT token"""
    user = DatabaseManager.get_user(username)
    if not user:
        return None, "Invalid credentials"
    
    if not check_password_hash(user['password_hash'], password):
        return None, "Invalid credentials"
    
    # Update last login
    import sqlite3
    conn = sqlite3.connect('roadsense.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                  (datetime.now(), user['id']))
    conn.commit()
    conn.close()
    
    access_token = create_access_token(
        identity=str(user['id']),
        additional_claims={
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'city': user['city']
        }
    )
    
    return access_token, None

def register_user(username: str, email: str, password: str, role: str = 'viewer', 
                 city: str = None, phone: str = None):
    """Register a new user"""
    existing_user = DatabaseManager.get_user(username)
    if existing_user:
        return None, "Username already exists"
    
    password_hash = generate_password_hash(password)
    try:
        user_id = DatabaseManager.add_user(username, email, password_hash, role, city, phone)
        return user_id, None
    except Exception as e:
        return None, str(e)
