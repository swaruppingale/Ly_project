from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.mood import MoodEntry
from app.models.user import User
from datetime import datetime, timedelta
import json

mood_bp = Blueprint('mood', __name__)

@mood_bp.route('/', methods=['POST'])
@jwt_required()
def log_mood():
    """Log a new mood entry"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('mood_score') or not data.get('mood_label'):
            return jsonify({'error': 'mood_score and mood_label are required'}), 400
        
        # Validate mood score
        mood_score = int(data['mood_score'])
        if not 1 <= mood_score <= 10:
            return jsonify({'error': 'mood_score must be between 1 and 10'}), 400
        
        # Create mood entry
        mood_entry = MoodEntry(
            user_id=current_user_id,
            mood_score=mood_score,
            mood_label=data['mood_label'],
            notes=data.get('notes'),
            activities=json.dumps(data.get('activities', [])) if data.get('activities') else None,
            sleep_hours=data.get('sleep_hours'),
            stress_level=data.get('stress_level'),
            energy_level=data.get('energy_level')
        )
        
        db.session.add(mood_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Mood logged successfully',
            'mood_entry': mood_entry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to log mood', 'details': str(e)}), 500

@mood_bp.route('/', methods=['GET'])
@jwt_required()
def get_mood_history():
    """Get user's mood history"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        days = request.args.get('days', type=int)
        
        # Build query
        query = MoodEntry.query.filter_by(user_id=current_user_id)
        
        # Filter by days if specified
        if days:
            start_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(MoodEntry.created_at >= start_date)
        
        # Order by creation date (newest first)
        query = query.order_by(MoodEntry.created_at.desc())
        
        # Get all entries for this user (for simple list)
        if page == 1 and per_page >= 100:  
            mood_entries = query.limit(100).all()
            return jsonify([entry.to_dict() for entry in mood_entries]), 200
        
        # Paginate results
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        mood_entries = [entry.to_dict() for entry in pagination.items]
        
        return jsonify(mood_entries), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get mood history', 'details': str(e)}), 500

@mood_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_mood_analytics():
    """Get mood analytics for the user"""
    try:
        current_user_id = get_jwt_identity()
        days = request.args.get('days', 30, type=int)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        
        all_mood_entries = MoodEntry.query.filter_by(user_id=current_user_id).all()
        
        # Get mood entries in date range for analytics
        mood_entries = MoodEntry.query.filter(
            MoodEntry.user_id == current_user_id,
            MoodEntry.created_at >= start_date,
            MoodEntry.created_at <= end_date
        ).order_by(MoodEntry.created_at.asc()).all()
        
        # Calculate basic stats
        total_entries = len(all_mood_entries)
        
        if not all_mood_entries:
            return jsonify({
                'total_entries': 0,
                'average_mood': 0,
                'current_streak': 0,
                'recent_trend': 0,
                'mood_data': [],
                'mood_distribution': {},
                'message': 'No mood data available'
            }), 200
        
        # Calculate average mood from all entries
        average_mood = sum(entry.mood_score for entry in all_mood_entries) / len(all_mood_entries)
        
        # Calculate current streak
        current_streak = 0
        if all_mood_entries:
            # Sort entries by date (newest first)
            sorted_entries = sorted(all_mood_entries, key=lambda x: x.created_at, reverse=True)
            current_date = datetime.utcnow().date()
            
            for entry in sorted_entries:
                entry_date = entry.created_at.date()
                if entry_date == current_date or entry_date == current_date - timedelta(days=1):
                    current_streak += 1
                    current_date = entry_date
                else:
                    break
        
        # Calculate recent trend (last 7 days vs previous 7 days)
        recent_trend = 0
        if len(all_mood_entries) >= 2:
            last_week = end_date - timedelta(days=7)
            previous_week = last_week - timedelta(days=7)
            
            recent_entries = [e for e in all_mood_entries if e.created_at >= last_week]
            previous_entries = [e for e in all_mood_entries if last_week > e.created_at >= previous_week]
            
            if recent_entries and previous_entries:
                recent_avg = sum(e.mood_score for e in recent_entries) / len(recent_entries)
                previous_avg = sum(e.mood_score for e in previous_entries) / len(previous_entries)
                recent_trend = recent_avg - previous_avg
        
        # Prepare mood data for chart (last 30 days)
        mood_data = []
        if mood_entries:
            for entry in mood_entries:
                mood_data.append({
                    'date': entry.created_at.strftime('%Y-%m-%d'),
                    'mood_score': entry.mood_score,
                    'mood_label': entry.mood_label
                })
        
        # Calculate mood distribution
        mood_distribution = {}
        for entry in all_mood_entries:
            mood_distribution[entry.mood_label] = mood_distribution.get(entry.mood_label, 0) + 1
        
        return jsonify({
            'total_entries': total_entries,
            'average_mood': round(average_mood, 2),
            'current_streak': current_streak,
            'recent_trend': round(recent_trend, 2),
            'mood_data': mood_data,
            'mood_distribution': mood_distribution
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get mood analytics', 'details': str(e)}), 500

@mood_bp.route('/<int:mood_id>', methods=['GET'])
@jwt_required()
def get_mood_entry(mood_id):
    """Get a specific mood entry"""
    try:
        current_user_id = get_jwt_identity()
        
        mood_entry = MoodEntry.query.filter_by(
            id=mood_id, user_id=current_user_id
        ).first()
        
        if not mood_entry:
            return jsonify({'error': 'Mood entry not found'}), 404
        
        return jsonify({
            'mood_entry': mood_entry.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get mood entry', 'details': str(e)}), 500

@mood_bp.route('/<int:mood_id>', methods=['PUT'])
@jwt_required()
def update_mood_entry(mood_id):
    """Update a mood entry"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        mood_entry = MoodEntry.query.filter_by(
            id=mood_id, user_id=current_user_id
        ).first()
        
        if not mood_entry:
            return jsonify({'error': 'Mood entry not found'}), 404
        
        # Update fields
        if 'mood_score' in data:
            mood_score = int(data['mood_score'])
            if not 1 <= mood_score <= 10:
                return jsonify({'error': 'mood_score must be between 1 and 10'}), 400
            mood_entry.mood_score = mood_score
        
        if 'mood_label' in data:
            mood_entry.mood_label = data['mood_label']
        
        if 'notes' in data:
            mood_entry.notes = data['notes']
        
        if 'activities' in data:
            mood_entry.activities = json.dumps(data['activities']) if data['activities'] else None
        
        if 'sleep_hours' in data:
            mood_entry.sleep_hours = data['sleep_hours']
        
        if 'stress_level' in data:
            mood_entry.stress_level = data['stress_level']
        
        if 'energy_level' in data:
            mood_entry.energy_level = data['energy_level']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Mood entry updated successfully',
            'mood_entry': mood_entry.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update mood entry', 'details': str(e)}), 500

@mood_bp.route('/<int:mood_id>', methods=['DELETE'])
@jwt_required()
def delete_mood_entry(mood_id):
    """Delete a mood entry"""
    try:
        current_user_id = get_jwt_identity()
        
        mood_entry = MoodEntry.query.filter_by(
            id=mood_id, user_id=current_user_id
        ).first()
        
        if not mood_entry:
            return jsonify({'error': 'Mood entry not found'}), 404
        
        db.session.delete(mood_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Mood entry deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete mood entry', 'details': str(e)}), 500 