import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.income_service import income_service

incomes_bp = Blueprint('incomes', __name__)

@incomes_bp.route('/incomes', methods=['GET'])
@jwt_required()
def get_incomes():
    """Get all incomes with optional filtering."""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', type=int)
        
        incomes = income_service.get_all_incomes(limit)

        logging.info(f"Fetched {len(incomes)} incomes successfully.")
        return jsonify({
            'success': True,
            'incomes': [income.to_dict() for income in incomes]
        })
    
    except Exception as e:
        logging.error(f"Error fetching incomes: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@incomes_bp.route("/incomes/monthly", methods=['GET'])
@jwt_required()
def get_monthly_incomes():
    """Get total income amounts grouped by month for the current user."""
    try:
        user_id = get_jwt_identity()
        monthly_incomes = income_service.get_monthly_incomes(user_id)
        
        return jsonify({
            'success': True,
            'monthly_incomes': monthly_incomes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@incomes_bp.route('/incomes/<string:income_id>', methods=['DELETE'])
@jwt_required()
def delete_income(income_id):
    """Delete an income."""
    try:
        user_id = get_jwt_identity()
        
        success = income_service.delete_income(income_id)
        if not success:
            logging.info(f"Income with ID {income_id} not found for deletion.")
            return jsonify({
                'success': False,
                'error': 'Income not found'
            }), 404
        
        logging.info(f"Deleted income with ID {income_id} successfully.")
        return jsonify({
            'success': True,
            'message': 'Income deleted successfully'
        })
    
    except Exception as e:
        logging.error(f"Error deleting income with ID {income_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500