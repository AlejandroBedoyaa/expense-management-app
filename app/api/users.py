import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token
from app.utils import to_datetime
from app.services.user_service import user_service
from datetime import datetime, timedelta, timezone
import os

from app.utils.helpers import utc_now

users_bp = Blueprint('user', __name__)

TOKEN_EXPIRATION_MINUTES = int(os.getenv('TOKEN_EXPIRATION_MINUTES', '15')) 

@users_bp.route("/signup", methods=["POST"])
def signup():
    """Register a new user."""
    try:
        data = request.get_json()
        token = data.get("token")
        email = data.get("email")
        password = data.get("password")

        user = user_service.get_user_by_token(token)
        if not user:
            logging.info(f"Failed account linking attempt with invalid token: {token}")
            return jsonify({
                    'success': False,
                    'error': 'User not found'
                }), 404
        if user.is_linked:
            logging.info(f"Attempt to link already linked user: {user.id}")
            return jsonify({
                'success': False,
                "error": "User already linked"
            }), 400
        
        now = utc_now()
        vinculation_token_created = to_datetime(user.vinculation_token_created)
        if not vinculation_token_created:
            logging.info(f"Token creation date not found for User {user.id}")
            return jsonify({
                "success": False,
                "error": "Invalid token"
            }), 400
            
        time_difference = now - vinculation_token_created
        expiration_time = timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
        
        if time_difference > expiration_time:
            logging.info(f"Token expired for User {user.id}. Created: {vinculation_token_created}, Expired after: {TOKEN_EXPIRATION_MINUTES} minutes")
            return jsonify({
                "success": False,
                "error": "Token expired"
            }), 400

        user.email = email
        user.set_password(password)
        user.is_linked = True
        user.vinculation_token = None
        user.vinculation_token_created = None
        user_service.update_user(user.id, {
            "email": user.email,
            "password": user.password,
            "is_linked": user.is_linked,
            "vinculation_token": user.vinculation_token
        })
        logging.info(f"User {user.id} linked their account successfully.")
        return jsonify({
            "success": True,
            "message": "Account linked successfully",
        })
    except Exception as e:
        logging.error(f"Error linking account: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@users_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user with email and password."""
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not all([email, password]):
            logging.info(f"Login attempt with missing credentials: email={email}, password={'***' if password else None}")
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        logging.info(f"request data: {data}")

        user = user_service.get_user_by_email(email)
        if not user or not user.check_password(password):
            logging.info(f"Failed login attempt for email: {email}")
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
        logging.info(f"User found with: {user}")

        if not user.is_linked:
            logging.info(f"Login attempt for unlinked account: User {user.id}")
            return jsonify({
                'success': False,
                'error': 'Account not linked.'
            }), 401
        
        access_token = create_access_token(identity=user.id)
        logging.info(f"User {user.id} Email {email} logged in successfully.")
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
            },
            'access_token': access_token
        })

    except Exception as e:
        logging.error(f"Error during login: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@users_bp.route("/refresh", methods=["POST"])
@jwt_required()
def refresh():
    """Refresh access token."""
    try:
        user_id = get_jwt_identity()
        
        # Verify user still exists and is active
        user = user_service.get_user_by_id(user_id)
        if not user:
            logging.info(f"Token refresh attempt for non-existent user: {user_id}")
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        if not user.is_linked:
            logging.info(f"Token refresh attempt for unlinked account: {user_id}")
            return jsonify({
                'success': False,
                'error': 'Account not linked'
            }), 401
        
        # Create new access token
        new_access_token = create_access_token(identity=user_id)
        
        logging.info(f"Token refreshed successfully for user: {user_id}")
        return jsonify({
            'success': True,
            'message': 'Token refreshed successfully',
            'access_token': new_access_token
        })
    
    except Exception as e:
        logging.error(f"Error refreshing token: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@users_bp.route("/change-password", methods=["POST"]) 
@jwt_required()
def change_password():
    """Change user password."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        email = data.get("email")
        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if not all([email, current_password, new_password]):
            return jsonify({
                'success': False,
                'error': 'Email, current password and new password are required'
            }), 400

        user = user_service.get_user_by_email(email)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        if not user.check_password(current_password):
            return jsonify({
                'success': False,
                'error': 'Current password is incorrect'
            }), 401

        user.set_password(new_password)
        user_service.update_user(user.id, {"password": user.password})

        return jsonify({
            'success': True,
            'message': 'Password changed successfully',
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

