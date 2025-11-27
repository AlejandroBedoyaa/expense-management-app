"""
API routes for managing expenses.
"""
import logging
import uuid
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services.expense_service import expense_service
import os
import tempfile
from app.config import Config

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

@expenses_bp.route('/expenses/<string:expense_id>', methods=['GET'])
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

@expenses_bp.route('/expenses/<string:expense_id>', methods=['PUT'])
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

@expenses_bp.route('/expenses/<string:expense_id>', methods=['DELETE'])
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

@expenses_bp.route('/expenses/upload-ticket', methods=['POST'])
@jwt_required()
def upload_ticket():
    """Upload and process a ticket image."""
    try:
        user_id = get_jwt_identity()
        if 'file' not in request.files:
            logging.info("No file uploaded for ticket processing.")
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.file_name == '':
            logging.info("No file selected for ticket processing.")
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not _allowed_file(file.file_name):
            logging.info(f"Invalid file type for ticket processing: {file.file_name}")
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: jpg, jpeg, png, bmp, tiff'
            }), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.file_name)[1]) as tmp_file:
            file.save(tmp_file.name)
            
            # Process the ticket
            expense_data = expense_service.process_ticket_image(tmp_file.name)
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
        
        logging.info(f"Processed ticket image successfully: {file.file_name}")
        return jsonify({
            'success': True,
            'extracted_data': expense_data,
            'message': 'ticket processed successfully'
        })
    
    except Exception as e:
        logging.error(f"Error processing ticket image: {str(e)}")
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
    

@expenses_bp.route("/file/ticket/<uuid:expense_id>", methods=['GET'])
@jwt_required()
def get_file(expense_id: uuid.UUID) -> str:
    """Get the full file path for an uploaded file."""
    try:
        user_id = get_jwt_identity()   
        expense = expense_service.get_expense_by_id(expense_id)
        if not expense or not expense.file_name:
            logging.info(f"File for expense ID {expense_id} not found.")
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        if user_id != expense.user_id:
            logging.info(f"Unauthorized access attempt by user {user_id} for expense ID {expense_id}.")
            return jsonify({
                'success': False,
                'error': 'Unauthorized access'
            }), 403
        
        files_path = os.path.join(Config.FILE_FOLDER, user_id)
        user_file = os.path.join(files_path, expense.file_name)
        file_rel_path = os.path.abspath(user_file)

        print(os.path.abspath(os.path.join(Config.FILE_FOLDER, expense.file_name)))

        return_file = send_file(file_rel_path)
        logging.info(f"Retrieved file path successfully: {expense.file_name}")
        return return_file
    except Exception as e:
        logging.error(f"Error retrieving file: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@expenses_bp.route("/expenses/monthly", methods=['GET'])
@jwt_required()
def get_monthly_expenses():
    """Get total expense amounts grouped by month for the current user."""
    try:
        user_id = get_jwt_identity()
        monthly_expenses = expense_service.get_monthly_expenses(user_id)
        
        return jsonify({
            'success': True,
            'monthly_expenses': monthly_expenses
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _allowed_file(file_name):
    """Check if uploaded file has allowed extension."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}
    return '.' in file_name and \
            file_name.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
