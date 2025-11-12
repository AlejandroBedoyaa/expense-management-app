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