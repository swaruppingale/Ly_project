from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.nutrition import NutritionEntry, DailyNutritionSummary
from datetime import datetime, date
import json

nutrition_bp = Blueprint('nutrition', __name__)

@nutrition_bp.route('/api/nutrition/meal', methods=['POST'])
@login_required
def add_meal():
    """Add a meal entry"""
    try:
        data = request.get_json()
        meal_name = data.get('name')
        meal_type = data.get('type')
        
        if not meal_name or not meal_type:
            return jsonify({'error': 'Meal name and type are required'}), 400
        
        #  meal entry
        meal_entry = NutritionEntry(
            user_id=current_user.id,
            entry_type='meal',
            name=meal_name,
            meal_type=meal_type,
            entry_date=date.today(),
            entry_time=datetime.now().time()
        )
        
        db.session.add(meal_entry)
        db.session.commit()
        
        # Update daily summary
        update_daily_summary(current_user.id, date.today())
        
        return jsonify({
            'message': 'Meal added successfully',
            'meal': meal_entry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@nutrition_bp.route('/api/nutrition/water', methods=['POST'])
@login_required
def add_water():
    """Add water intake"""
    try:
        data = request.get_json()
        glasses = data.get('glasses', 1)
        
        
        water_entry = NutritionEntry(
            user_id=current_user.id,
            entry_type='water',
            water_glasses=glasses,
            entry_date=date.today(),
            entry_time=datetime.now().time()
        )
        
        db.session.add(water_entry)
        db.session.commit()
        
        # Update daily summary
        update_daily_summary(current_user.id, date.today())
        
        return jsonify({
            'message': 'Water intake recorded',
            'water': water_entry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@nutrition_bp.route('/api/nutrition/daily/<date_str>', methods=['GET'])
@login_required
def get_daily_nutrition(date_str):
    """Get nutrition data for a specific date"""
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get meals for the date
        meals = NutritionEntry.query.filter_by(
            user_id=current_user.id,
            entry_type='meal',
            entry_date=target_date
        ).all()
        
        # Get water entries for the date
        water_entries = NutritionEntry.query.filter_by(
            user_id=current_user.id,
            entry_type='water',
            entry_date=target_date
        ).all()
        
        # Calculate total water glasses
        total_water = sum(entry.water_glasses for entry in water_entries)
        
        # Get or create daily summary
        summary = DailyNutritionSummary.query.filter_by(
            user_id=current_user.id,
            summary_date=target_date
        ).first()
        
        if not summary:
            summary = DailyNutritionSummary(
                user_id=current_user.id,
                summary_date=target_date,
                total_meals=len(meals),
                total_water_glasses=total_water
            )
            db.session.add(summary)
            db.session.commit()
        
        return jsonify({
            'date': date_str,
            'meals': [meal.to_dict() for meal in meals],
            'total_water_glasses': total_water,
            'summary': summary.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nutrition_bp.route('/api/nutrition/meal/<int:meal_id>', methods=['DELETE'])
@login_required
def delete_meal(meal_id):
    """Delete a meal entry"""
    try:
        meal = NutritionEntry.query.filter_by(
            id=meal_id,
            user_id=current_user.id,
            entry_type='meal'
        ).first()
        
        if not meal:
            return jsonify({'error': 'Meal not found'}), 404
        
        db.session.delete(meal)
        db.session.commit()
        
        # Update daily summary
        update_daily_summary(current_user.id, meal.entry_date)
        
        return jsonify({'message': 'Meal deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@nutrition_bp.route('/api/nutrition/reset-daily', methods=['POST'])
@login_required
def reset_daily_nutrition():
    """Reset daily nutrition data"""
    try:
        today = date.today()
        
        # Delete today's entries
        NutritionEntry.query.filter_by(
            user_id=current_user.id,
            entry_date=today
        ).delete()
        
        # Delete today's summary
        DailyNutritionSummary.query.filter_by(
            user_id=current_user.id,
            summary_date=today
        ).delete()
        
        db.session.commit()
        
        return jsonify({'message': 'Daily nutrition data reset successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def update_daily_summary(user_id, summary_date):
    """Update daily nutrition summary"""
    try:
        # Count meals for the date
        meal_count = NutritionEntry.query.filter_by(
            user_id=user_id,
            entry_type='meal',
            entry_date=summary_date
        ).count()
        
        # Sum water glasses for the date
        water_entries = NutritionEntry.query.filter_by(
            user_id=user_id,
            entry_type='water',
            entry_date=summary_date
        ).all()
        total_water = sum(entry.water_glasses for entry in water_entries)
        
        # Calculate mood score
        mood_score = '😊'
        if meal_count >= 3 and total_water >= 6:
            mood_score = '😄'
        elif meal_count < 2 or total_water < 4:
            mood_score = '😐'
        
        # Get or create summary
        summary = DailyNutritionSummary.query.filter_by(
            user_id=user_id,
            summary_date=summary_date
        ).first()
        
        if summary:
            summary.total_meals = meal_count
            summary.total_water_glasses = total_water
            summary.mood_score = mood_score
            summary.updated_at = datetime.utcnow()
        else:
            summary = DailyNutritionSummary(
                user_id=user_id,
                summary_date=summary_date,
                total_meals=meal_count,
                total_water_glasses=total_water,
                mood_score=mood_score
            )
            db.session.add(summary)
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        raise e 