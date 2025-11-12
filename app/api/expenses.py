"""
API routes for managing expenses.
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.expense_service import expense_service
from werkzeug.utils import secure_filename
import os
import tempfile

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_expenses():
    """Get all expenses with optional filtering."""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', type=int)
        expenses = expense_service.get_all_expenses(user_id, limit)

        logging.info(f"Fetched {len(expenses)} expenses successfully.")
        return jsonify({
            'success': True,
            'expenses': [expense.to_dict() for expense in expenses]
        })
    
    except Exception as e:
        logging.error(f"Error fetching expenses: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@expenses_bp.route('/expenses/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    """Get a specific expense by ID."""
    try:
        user_id = get_jwt_identity()
        expense = expense_service.get_expense_by_id(expense_id)
        
        if not expense:
            logging.info(f"Expense with ID {expense_id} not found.")
            return jsonify({
                'success': False,
                'error': 'Expense not found'
            }), 404
        
        logging.info(f"Fetched expense with ID {expense_id} successfully.")
        return jsonify({
            'success': True,
            'expense': expense.to_dict()
        })
    
    except Exception as e:
        logging.error(f"Error fetching expense with ID {expense_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@expenses_bp.route('/expenses', methods=['POST'])
@jwt_required()
def create_expense():
    """Create a new expense."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            logging.info("No data provided for creating an expense.")
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['payment_concept', 'total']
        for field in required_fields:
            if field not in data:
                logging.info(f"Missing required field for creating an expense: {field}")
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        expense = expense_service.create_expense(data)
        
        logging.info(f"Created expense with ID {expense.id} successfully.")
        return jsonify({
            'success': True,
            'expense': expense.to_dict()
        }), 201
    
    except Exception as e:
        logging.error(f"Error creating expense: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@expenses_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    """Update an existing expense."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            logging.info("No data provided for updating an expense.")
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        expense = expense_service.update_expense(expense_id, data)
        
        if not expense:
            logging.info(f"Expense with ID {expense_id} not found for update.")
            return jsonify({
                'success': False,
                'error': 'Expense not found'
            }), 404
        
        logging.info(f"Updated expense with ID {expense_id} successfully.")
        return jsonify({
            'success': True,
            'expense': expense.to_dict()
        })
    
    except Exception as e:
        logging.error(f"Error updating expense with ID {expense_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@expenses_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    """Delete an expense."""
    try:
        user_id = get_jwt_identity()
        success = expense_service.delete_expense(expense_id)
        
        if not success:
            logging.info(f"Expense with ID {expense_id} not found for deletion.")
            return jsonify({
                'success': False,
                'error': 'Expense not found'
            }), 404
        
        logging.info(f"Deleted expense with ID {expense_id} successfully.")
        return jsonify({
            'success': True,
            'message': 'Expense deleted successfully'
        })
    
    except Exception as e:
        logging.error(f"Error deleting expense with ID {expense_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@expenses_bp.route('/expenses/upload-receipt', methods=['POST'])
@jwt_required()
def upload_receipt():
    """Upload and process a receipt image."""
    try:
        user_id = get_jwt_identity()
        if 'file' not in request.files:
            logging.info("No file uploaded for receipt processing.")
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logging.info("No file selected for receipt processing.")
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not _allowed_file(file.filename):
            logging.info(f"Invalid file type for receipt processing: {file.filename}")
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: jpg, jpeg, png, bmp, tiff'
            }), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            file.save(tmp_file.name)
            
            # Process the receipt
            expense_data = expense_service.process_receipt_image(tmp_file.name)
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
        
        logging.info(f"Processed receipt image successfully: {file.filename}")
        return jsonify({
            'success': True,
            'extracted_data': expense_data,
            'message': 'Receipt processed successfully'
        })
    
    except Exception as e:
        logging.error(f"Error processing receipt image: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@expenses_bp.route('/expenses/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """Get expense statistics."""
    try:
        user_id = get_jwt_identity()
        stats = expense_service.get_expense_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _allowed_file(filename):
    """Check if uploaded file has allowed extension."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS