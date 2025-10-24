from flask import Blueprint, request, jsonify
from app.services.expense_service import expense_service
from app.services.ocr_service import ocr_service
from werkzeug.utils import secure_filename
import os
import tempfile

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/expenses', methods=['GET'])
def get_expenses():
    """Get all expenses with optional filtering."""
    try:
        # Get query parameters
        category = request.args.get('category')
        limit = request.args.get('limit', type=int)
        
        if category:
            expenses = expense_service.get_expenses_by_category(category)
        else:
            expenses = expense_service.get_all_expenses(limit)
        
        return jsonify({
            'success': True,
            'expenses': [expense.to_dict() for expense in expenses]
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@expenses_bp.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """Get a specific expense by ID."""
    try:
        expense = expense_service.get_expense_by_id(expense_id)
        
        if not expense:
            return jsonify({
                'success': False,
                'error': 'Expense not found'
            }), 404
        
        return jsonify({
            'success': True,
            'expense': expense.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@expenses_bp.route('/expenses', methods=['POST'])
def create_expense():
    """Create a new expense."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['payment_concept', 'total']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        expense = expense_service.create_expense(data)
        
        return jsonify({
            'success': True,
            'expense': expense.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@expenses_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """Update an existing expense."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        expense = expense_service.update_expense(expense_id, data)
        
        if not expense:
            return jsonify({
                'success': False,
                'error': 'Expense not found'
            }), 404
        
        return jsonify({
            'success': True,
            'expense': expense.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@expenses_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete an expense."""
    try:
        success = expense_service.delete_expense(expense_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Expense not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Expense deleted successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@expenses_bp.route('/expenses/upload-receipt', methods=['POST'])
def upload_receipt():
    """Upload and process a receipt image."""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not _allowed_file(file.filename):
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
        
        return jsonify({
            'success': True,
            'extracted_data': expense_data,
            'message': 'Receipt processed successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@expenses_bp.route('/expenses/statistics', methods=['GET'])
def get_statistics():
    """Get expense statistics."""
    try:
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