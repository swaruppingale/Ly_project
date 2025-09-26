from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.resource import Resource

resources_bp = Blueprint('resources', __name__)

@resources_bp.route('/', methods=['GET'])
def get_resources():
    """Get all active resources"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category', '')
        type_filter = request.args.get('type', '')
        difficulty = request.args.get('difficulty', '')
        featured = request.args.get('featured', type=bool)
        search = request.args.get('search', '')
        
        # Build query
        query = Resource.query.filter_by(is_active=True)
        
        # Apply filters
        if category:
            query = query.filter(Resource.category == category)
        
        if type_filter:
            query = query.filter(Resource.type == type_filter)
        
        if difficulty:
            query = query.filter(Resource.difficulty_level == difficulty)
        
        if featured is not None:
            query = query.filter(Resource.is_featured == featured)
        
        if search:
            query = query.filter(
                Resource.title.contains(search) | 
                Resource.description.contains(search) |
                Resource.content.contains(search)
            )
        
        # Order by featured first, then by creation date
        query = query.order_by(Resource.is_featured.desc(), Resource.created_at.desc())
        
        # Paginate results
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        resources = [resource.to_dict() for resource in pagination.items]
        
        return jsonify({
            'resources': resources,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get resources', 'details': str(e)}), 500

@resources_bp.route('/<int:resource_id>', methods=['GET'])
def get_resource(resource_id):
    """Get a specific resource"""
    try:
        resource = Resource.query.filter_by(
            id=resource_id, is_active=True
        ).first()
        
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        
        return jsonify({
            'resource': resource.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get resource', 'details': str(e)}), 500

@resources_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all available resource categories"""
    try:
        categories = db.session.query(Resource.category).distinct().all()
        category_list = [category[0] for category in categories if category[0]]
        
        return jsonify({
            'categories': category_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get categories', 'details': str(e)}), 500

@resources_bp.route('/types', methods=['GET'])
def get_types():
    """Get all available resource types"""
    try:
        types = db.session.query(Resource.type).distinct().all()
        type_list = [type_[0] for type_ in types if type_[0]]
        
        return jsonify({
            'types': type_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get types', 'details': str(e)}), 500

@resources_bp.route('/featured', methods=['GET'])
def get_featured_resources():
    """Get featured resources"""
    try:
        featured_resources = Resource.query.filter_by(
            is_featured=True, is_active=True
        ).order_by(Resource.created_at.desc()).limit(10).all()
        
        resources = [resource.to_dict() for resource in featured_resources]
        
        return jsonify({
            'featured_resources': resources
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get featured resources', 'details': str(e)}), 500

@resources_bp.route('/recommended', methods=['GET'])
@jwt_required()
def get_recommended_resources():
    """Get recommended resources based on user's mood history"""
    try:
        current_user_id = get_jwt_identity()
        
       
        from app.models.mood import MoodEntry
        from datetime import datetime, timedelta
        
        recent_moods = MoodEntry.query.filter_by(user_id=current_user_id).filter(
            MoodEntry.created_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        if not recent_moods:
            # If no mood data, return featured resources
            return get_featured_resources()
        
        # Calculate average mood
        avg_mood = sum(mood.mood_score for mood in recent_moods) / len(recent_moods)
        
        
        if avg_mood <= 4:
            # Low mood - recommend uplifting and coping resources
            recommended = Resource.query.filter(
                Resource.category.in_(['Depression', 'Coping', 'Self-Care']),
                Resource.is_active == True
            ).limit(5).all()
        elif avg_mood <= 6:
            # Moderate mood - recommend general wellness resources
            recommended = Resource.query.filter(
                Resource.category.in_(['Wellness', 'Meditation', 'Exercise']),
                Resource.is_active == True
            ).limit(5).all()
        else:
            # High mood - recommend maintenance and growth resources
            recommended = Resource.query.filter(
                Resource.category.in_(['Growth', 'Mindfulness', 'Happiness']),
                Resource.is_active == True
            ).limit(5).all()
        
        # If not enough specific recommendations, add featured resources
        if len(recommended) < 5:
            featured = Resource.query.filter_by(
                is_featured=True, is_active=True
            ).limit(5 - len(recommended)).all()
            recommended.extend(featured)
        
        resources = [resource.to_dict() for resource in recommended]
        
        return jsonify({
            'recommended_resources': resources,
            'recommendation_basis': {
                'average_mood': round(avg_mood, 2),
                'mood_entries_analyzed': len(recent_moods)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get recommended resources', 'details': str(e)}), 500

# Admin routes (would require admin authentication in production)
@resources_bp.route('/', methods=['POST'])
@jwt_required()
def create_resource():
    """Create a new resource (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'content', 'category', 'type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create resource
        resource = Resource(
            title=data['title'],
            description=data['description'],
            content=data['content'],
            category=data['category'],
            type=data['type'],
            url=data.get('url'),
            duration=data.get('duration'),
            difficulty_level=data.get('difficulty_level'),
            tags=data.get('tags'),
            is_featured=data.get('is_featured', False),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(resource)
        db.session.commit()
        
        return jsonify({
            'message': 'Resource created successfully',
            'resource': resource.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create resource', 'details': str(e)}), 500

@resources_bp.route('/<int:resource_id>', methods=['PUT'])
@jwt_required()
def update_resource(resource_id):
    """Update a resource (admin only)"""
    try:
        data = request.get_json()
        
        resource = Resource.query.get(resource_id)
        
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        
        # Update fields
        updateable_fields = [
            'title', 'description', 'content', 'category', 'type',
            'url', 'duration', 'difficulty_level', 'tags',
            'is_featured', 'is_active'
        ]
        
        for field in updateable_fields:
            if field in data:
                setattr(resource, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Resource updated successfully',
            'resource': resource.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update resource', 'details': str(e)}), 500

@resources_bp.route('/<int:resource_id>', methods=['DELETE'])
@jwt_required()
def delete_resource(resource_id):
    """Delete a resource (admin only)"""
    try:
        resource = Resource.query.get(resource_id)
        
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        
        db.session.delete(resource)
        db.session.commit()
        
        return jsonify({
            'message': 'Resource deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete resource', 'details': str(e)}), 500 