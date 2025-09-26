from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.exercise import ExerciseSession, MeditationSession, BreathingMethod
from datetime import datetime, date, timedelta
import json

activities_bp = Blueprint('activities', __name__)

# Exercise Routes
@activities_bp.route('/api/exercise/complete', methods=['POST'])
@login_required
def complete_exercise():
    
    try:
        data = request.get_json()
        exercise_type = data.get('exercise_type')
        exercise_name = data.get('exercise_name')
        duration_seconds = data.get('duration_seconds')
        
        if not all([exercise_type, exercise_name, duration_seconds]):
            return jsonify({'error': 'Exercise type, name, and duration are required'}), 400
        
        # Create exercise session
        exercise_session = ExerciseSession(
            user_id=current_user.id,
            exercise_type=exercise_type,
            exercise_name=exercise_name,
            duration_seconds=duration_seconds,
            session_date=date.today(),
            completed_at=datetime.utcnow()
        )
        
        db.session.add(exercise_session)
        db.session.commit()
        
        return jsonify({
            'message': 'Exercise completed successfully',
            'exercise': exercise_session.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@activities_bp.route('/api/exercise/history', methods=['GET'])
@login_required
def get_exercise_history():
    
    try:
       
        days = request.args.get('days', 7, type=int)
        start_date = date.today() - timedelta(days=days)
        
        exercises = ExerciseSession.query.filter(
            ExerciseSession.user_id == current_user.id,
            ExerciseSession.session_date >= start_date
        ).order_by(ExerciseSession.session_date.desc()).all()
        
        return jsonify({
            'exercises': [exercise.to_dict() for exercise in exercises]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Meditation Routes
@activities_bp.route('/api/meditation/complete', methods=['POST'])
@login_required
def complete_meditation():
    
    try:
        data = request.get_json()
        session_type = data.get('session_type', 'basic')
        session_name = data.get('session_name', 'Basic Meditation')
        duration_seconds = data.get('duration_seconds')
        breath_count = data.get('breath_count', 0)
        
        if not duration_seconds:
            return jsonify({'error': 'Duration is required'}), 400
        
        # Create meditation session
        meditation_session = MeditationSession(
            user_id=current_user.id,
            session_type=session_type,
            session_name=session_name,
            duration_seconds=duration_seconds,
            breath_count=breath_count,
            session_date=date.today(),
            completed_at=datetime.utcnow()
        )
        
        db.session.add(meditation_session)
        db.session.commit()
        
        return jsonify({
            'message': 'Meditation completed successfully',
            'meditation': meditation_session.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@activities_bp.route('/api/meditation/history', methods=['GET'])
@login_required
def get_meditation_history():
    
    try:
        # Get date range from query params
        days = request.args.get('days', 7, type=int)
        start_date = date.today() - timedelta(days=days)
        
        meditations = MeditationSession.query.filter(
            MeditationSession.user_id == current_user.id,
            MeditationSession.session_date >= start_date
        ).order_by(MeditationSession.session_date.desc()).all()
        
        return jsonify({
            'meditations': [meditation.to_dict() for meditation in meditations]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Breathing Methods Routes
@activities_bp.route('/api/breathing/complete', methods=['POST'])
@login_required
def complete_breathing():
    
    try:
        data = request.get_json()
        method_type = data.get('method_type')
        method_name = data.get('method_name')
        duration_seconds = data.get('duration_seconds')
        cycles_completed = data.get('cycles_completed', 0)
        
        if not all([method_type, method_name, duration_seconds]):
            return jsonify({'error': 'Method type, name, and duration are required'}), 400
        
        # Create breathing method session
        breathing_session = BreathingMethod(
            user_id=current_user.id,
            method_type=method_type,
            method_name=method_name,
            duration_seconds=duration_seconds,
            cycles_completed=cycles_completed,
            session_date=date.today(),
            completed_at=datetime.utcnow()
        )
        
        db.session.add(breathing_session)
        db.session.commit()
        
        return jsonify({
            'message': 'Breathing session completed successfully',
            'breathing': breathing_session.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@activities_bp.route('/api/breathing/history', methods=['GET'])
@login_required
def get_breathing_history():
    
    try:
        # Get date range from query params
        days = request.args.get('days', 7, type=int)
        start_date = date.today() - timedelta(days=days)
        
        breathing_sessions = BreathingMethod.query.filter(
            BreathingMethod.user_id == current_user.id,
            BreathingMethod.session_date >= start_date
        ).order_by(BreathingMethod.session_date.desc()).all()
        
        return jsonify({
            'breathing_sessions': [session.to_dict() for session in breathing_sessions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Combined Activity Statistics
@activities_bp.route('/api/activities/stats', methods=['GET'])
@login_required
def get_activity_stats():
    
    try:
        today = date.today()
        
        # Today's exercise sessions
        today_exercises = ExerciseSession.query.filter_by(
            user_id=current_user.id,
            session_date=today
        ).all()
        
        # Today's meditation sessions
        today_meditations = MeditationSession.query.filter_by(
            user_id=current_user.id,
            session_date=today
        ).all()
        
        # Today's breathing sessions
        today_breathing = BreathingMethod.query.filter_by(
            user_id=current_user.id,
            session_date=today
        ).all()
        
        # Calculate totals
        total_exercise_time = sum(ex.duration_seconds for ex in today_exercises)
        total_meditation_time = sum(med.duration_seconds for med in today_meditations)
        total_breathing_time = sum(bre.duration_seconds for bre in today_breathing)
        total_breaths = sum(med.breath_count for med in today_meditations)
        
        return jsonify({
            'today': {
                'exercises': len(today_exercises),
                'exercise_time_minutes': round(total_exercise_time / 60, 1),
                'meditations': len(today_meditations),
                'meditation_time_minutes': round(total_meditation_time / 60, 1),
                'breathing_sessions': len(today_breathing),
                'breathing_time_minutes': round(total_breathing_time / 60, 1),
                'total_breaths': total_breaths
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 