import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from email_validator import validate_email, EmailNotValidError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        if data is None:
            logging.warning(f"No JSON data received from {request.remote_addr}")
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        logging.info(f"Registration attempt from {request.remote_addr}: {data}")

        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                logging.warning(f"Missing required field: {field} from {request.remote_addr}")
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        try:
            validate_email(data['email'])
        except EmailNotValidError:
            logging.warning(f"Invalid email format: {data['email']} from {request.remote_addr}")
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            logging.warning(f"Duplicate username: {data['username']} from {request.remote_addr}")
            return jsonify({'error': 'Username already exists'}), 409
        
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            logging.warning(f"Duplicate email: {data['email']} from {request.remote_addr}")
            return jsonify({'error': 'Email already exists'}), 409
        
        # Validate password strength
        if len(data['password']) < 6:
            logging.warning(f"Password too short: {len(data['password'])} characters from {request.remote_addr}")
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        logging.info(f"All validations passed for {data['username']} from {request.remote_addr}")
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone=data.get('phone'),
            emergency_contact=data.get('emergency_contact')
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        logging.info(f"User {user.id} registered successfully from {request.remote_addr}")
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Registration exception for {request.remote_addr}: {str(e)}")
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        if data is None:
            logging.warning(f"No JSON data received from {request.remote_addr}")
            return jsonify({'error': 'Invalid JSON data'}), 400

        logging.info(f"Login attempt from {request.remote_addr}: username={data.get('username')}")

        # Validate required fields
        if not data.get('username') or not data.get('password'):
            logging.warning(f"Missing username or password from {request.remote_addr}")
            return jsonify({'error': 'Username and password are required'}), 400

        # Find user by username or email
        user = User.query.filter(
            (User.username == data['username']) | (User.email == data['username'])
        ).first()

        if not user:
            logging.warning(f"User not found: {data['username']} from {request.remote_addr}")
            return jsonify({'error': 'Invalid username or password'}), 401

        if not user.check_password(data['password']):
            logging.warning(f"Invalid password for user: {data['username']} from {request.remote_addr}")
            return jsonify({'error': 'Invalid username or password'}), 401

        if not user.is_active:
            logging.warning(f"Deactivated account login attempt: {data['username']} from {request.remote_addr}")
            return jsonify({'error': 'Account is deactivated'}), 401

        logging.info(f"Login successful for user: {user.username} from {request.remote_addr}")

        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200

    except Exception as e:
        logging.error(f"Login exception for {request.remote_addr}: {str(e)}")
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Token refresh failed', 'details': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard tokens)"""
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user information', 'details': str(e)}), 500 