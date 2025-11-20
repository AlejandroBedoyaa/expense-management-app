"""
API routes for balance and financial calculations.
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.balance_service import balance_service

balances_bp = Blueprint('balances', __name__)


@balances_bp.route('/balance/current', methods=['GET'])
@jwt_required()
def get_current_balance():
    """Get current month balance for user."""
    try:
        user_id = get_jwt_identity()
        
        if not user_id:
            logging.info("user_id is required for getting current balance.")
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        balance = balance_service.get_current_balance(user_id)
        
        logging.info(f"Retrieved current balance for user_id {user_id} successfully.")
        return jsonify({
            'success': True,
            'balance': balance
        })
    
    except Exception as e:
        logging.error(f"Error retrieving current balance for user_id {user_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@balances_bp.route('/balance/monthly', methods=['GET'])
@jwt_required()
def get_monthly_balance():
    """Get balance for specific month."""
    try:
        user_id = get_jwt_identity()
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if not user_id:
            logging.info("user_id is required for getting monthly balance.")
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        balance = balance_service.get_monthly_balance(user_id, month, year)
        
        logging.info(f"Retrieved monthly balance for user_id {user_id}, month {month}, year {year} successfully.")
        return jsonify({
            'success': True,
            'balance': balance
        })
    
    except Exception as e:
        logging.error(f"Error retrieving monthly balance for user_id {user_id}, month {month}, year {year}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@balances_bp.route('/balance/summary', methods=['GET'])
@jwt_required()
def get_summary():
    """Get financial summary."""
    try:
        user_id = get_jwt_identity()
        
        if not user_id:
            logging.info("user_id is required for getting financial summary.") 
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        summary = balance_service.get_financial_summary(user_id)
        
        logging.info(f"Retrieved financial summary for user_id {user_id} successfully.")
        return jsonify({
            'success': True,
            'summary': summary
        })
    
    except Exception as e:
        logging.error(f"Error retrieving financial summary for user_id {user_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
