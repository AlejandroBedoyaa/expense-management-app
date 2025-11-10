"""
API routes for balance and financial calculations.
"""
from flask import Blueprint, request, jsonify
from app.services.balance_service import balance_service

balance_bp = Blueprint('balance', __name__)


@balance_bp.route('/balance/current', methods=['GET'])
def get_current_balance():
    """Get current month balance for user."""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        balance = balance_service.get_current_balance(user_id)
        
        return jsonify({
            'success': True,
            'balance': balance
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@balance_bp.route('/balance/monthly', methods=['GET'])
def get_monthly_balance():
    """Get balance for specific month."""
    try:
        user_id = request.args.get('user_id')
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        balance = balance_service.get_monthly_balance(user_id, month, year)
        
        return jsonify({
            'success': True,
            'balance': balance
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@balance_bp.route('/balance/summary', methods=['GET'])
def get_summary():
    """Get financial summary."""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        summary = balance_service.get_financial_summary(user_id)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
