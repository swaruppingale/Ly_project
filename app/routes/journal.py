from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.journal import JournalEntry
import json

journal_bp = Blueprint('journal', __name__)

@journal_bp.route('/', methods=['POST'])
@jwt_required()
def create_journal_entry():
    """Create a new journal entry"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('content'):
            return jsonify({'error': 'content is required'}), 400
        
        # Create journal entry
        journal_entry = JournalEntry(
            user_id=current_user_id,
            content=data['content'],
            title=data.get('title'),
            mood_before=data.get('mood_before'),
            mood_after=data.get('mood_after'),
            tags=json.dumps(data.get('tags', [])) if data.get('tags') else None,
            is_private=data.get('is_private', True)
        )
        
        db.session.add(journal_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Journal entry created successfully',
            'journal_entry': journal_entry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create journal entry', 'details': str(e)}), 500

@journal_bp.route('/', methods=['GET'])
@jwt_required()
def get_journal_entries():
    """Get user's journal entries"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        tags = request.args.get('tags', '')
        
        # Build query
        query = JournalEntry.query.filter_by(user_id=current_user_id)
        
        # Search functionality
        if search:
            query = query.filter(
                JournalEntry.content.contains(search) | 
                JournalEntry.title.contains(search)
            )
        
        # Filter by tags
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                query = query.filter(JournalEntry.tags.contains(tag))
        
        # Order by creation date (newest first)
        query = query.order_by(JournalEntry.created_at.desc())
        
        # Get all entries for this user 
        if page == 1 and per_page >= 100:  
            journal_entries = query.limit(100).all()
            return jsonify([entry.to_dict() for entry in journal_entries]), 200
        
        # Paginate results
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        journal_entries = [entry.to_dict() for entry in pagination.items]
        
        return jsonify(journal_entries), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get journal entries', 'details': str(e)}), 500

@journal_bp.route('/<int:entry_id>', methods=['GET'])
@jwt_required()
def get_journal_entry(entry_id):
    """Get a specific journal entry"""
    try:
        current_user_id = get_jwt_identity()
        
        journal_entry = JournalEntry.query.filter_by(
            id=entry_id, user_id=current_user_id
        ).first()
        
        if not journal_entry:
            return jsonify({'error': 'Journal entry not found'}), 404
        
        return jsonify({
            'journal_entry': journal_entry.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get journal entry', 'details': str(e)}), 500

@journal_bp.route('/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_journal_entry(entry_id):
    """Update a journal entry"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        journal_entry = JournalEntry.query.filter_by(
            id=entry_id, user_id=current_user_id
        ).first()
        
        if not journal_entry:
            return jsonify({'error': 'Journal entry not found'}), 404
        
        # Update fields
        if 'content' in data:
            journal_entry.content = data['content']
        
        if 'title' in data:
            journal_entry.title = data['title']
        
        if 'mood_before' in data:
            journal_entry.mood_before = data['mood_before']
        
        if 'mood_after' in data:
            journal_entry.mood_after = data['mood_after']
        
        if 'tags' in data:
            journal_entry.tags = json.dumps(data['tags']) if data['tags'] else None
        
        if 'is_private' in data:
            journal_entry.is_private = data['is_private']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Journal entry updated successfully',
            'journal_entry': journal_entry.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update journal entry', 'details': str(e)}), 500

@journal_bp.route('/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_journal_entry(entry_id):
    """Delete a journal entry"""
    try:
        current_user_id = get_jwt_identity()
        
        journal_entry = JournalEntry.query.filter_by(
            id=entry_id, user_id=current_user_id
        ).first()
        
        if not journal_entry:
            return jsonify({'error': 'Journal entry not found'}), 404
        
        db.session.delete(journal_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Journal entry deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete journal entry', 'details': str(e)}), 500

@journal_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_journal_analytics():
    """Get journal analytics for the user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get all journal entries for the user
        journal_entries = JournalEntry.query.filter_by(user_id=current_user_id).all()
        
        if not journal_entries:
            return jsonify({
                'total_entries': 0,
                'average_mood_before': 0,
                'average_mood_after': 0,
                'most_common_tags': [],
                'writing_streak': 0,
                'total_tags_used': 0,
                'message': 'No journal entries available'
            }), 200
        
        # Calculate analytics
        total_entries = len(journal_entries)
        
        # Mood analytics
        mood_before_entries = [e for e in journal_entries if e.mood_before is not None]
        mood_after_entries = [e for e in journal_entries if e.mood_after is not None]
        
        average_mood_before = sum(e.mood_before for e in mood_before_entries) / len(mood_before_entries) if mood_before_entries else 0
        average_mood_after = sum(e.mood_after for e in mood_after_entries) / len(mood_after_entries) if mood_after_entries else 0
        
        # Tag analytics
        all_tags = []
        for entry in journal_entries:
            if entry.tags:
                try:
                    tags = json.loads(entry.tags)
                    all_tags.extend(tags)
                except:
                    pass
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        most_common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        
        from datetime import datetime, timedelta
        entry_dates = set(entry.created_at.date() for entry in journal_entries)
        sorted_dates = sorted(entry_dates, reverse=True)
        
        writing_streak = 0
        current_date = datetime.utcnow().date()
        
        for i in range(len(sorted_dates)):
            if current_date - sorted_dates[i] == timedelta(days=i):
                writing_streak += 1
            else:
                break
        
        return jsonify({
            'total_entries': total_entries,
            'average_mood_before': round(average_mood_before, 2),
            'average_mood_after': round(average_mood_after, 2),
            'most_common_tags': most_common_tags,
            'writing_streak': writing_streak,
            'total_tags_used': len(tag_counts)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get journal analytics', 'details': str(e)}), 500 