from app import db
from datetime import datetime

class MoodEntry(db.Model):
    """Mood entry model for tracking user mood"""
    __tablename__ = 'mood_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mood_score = db.Column(db.Integer, nullable=False)  # 1-10 scale
    mood_label = db.Column(db.String(50), nullable=False)  # e.g., "Happy", "Sad", "Anxious"
    notes = db.Column(db.Text, nullable=True)
    activities = db.Column(db.Text, nullable=True)  # JSON string of activities
    sleep_hours = db.Column(db.Float, nullable=True)
    stress_level = db.Column(db.Integer, nullable=True)  # 1-10 scale
    energy_level = db.Column(db.Integer, nullable=True)  # 1-10 scale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, mood_score, mood_label, **kwargs):
        self.user_id = user_id
        self.mood_score = mood_score
        self.mood_label = mood_label
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        """Convert mood entry to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'mood_score': self.mood_score,
            'mood_label': self.mood_label,
            'notes': self.notes,
            'activities': self.activities,
            'sleep_hours': self.sleep_hours,
            'stress_level': self.stress_level,
            'energy_level': self.energy_level,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<MoodEntry {self.mood_label} - {self.mood_score}/10>' 