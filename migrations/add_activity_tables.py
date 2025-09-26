"""
Migration script to add nutrition and activity tracking tables
Run this script to create the new database tables
"""

from app import create_app, db
from app.models.nutrition import NutritionEntry, DailyNutritionSummary
from app.models.exercise import ExerciseSession, MeditationSession, BreathingMethod

def migrate():
    """Create new tables for nutrition and activity tracking"""
    app = create_app()
    
    with app.app_context():
        print("Creating nutrition and activity tracking tables...")
        
        # Create nutrition tables
        db.create_all()
        
        print("✅ Migration completed successfully!")
        print("New tables created:")
        print("- nutrition_entries")
        print("- daily_nutrition_summaries")
        print("- exercise_sessions")
        print("- meditation_sessions")
        print("- breathing_methods")

if __name__ == "__main__":
    migrate() 