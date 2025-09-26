from app import db
from datetime import datetime

class NutritionEntry(db.Model):
    """Nutrition tracking model for meals and hydration"""
    __tablename__ = 'nutrition_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    entry_type = db.Column(db.String(20), nullable=False)  # 'meal' or 'water'
    name = db.Column(db.String(200), nullable=True)  # meal name
    meal_type = db.Column(db.String(20), nullable=True)  # breakfast, lunch, dinner, snack
    water_glasses = db.Column(db.Integer, nullable=True)  # number of water glasses
    entry_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    entry_time = db.Column(db.Time, nullable=False, default=datetime.utcnow().time)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='nutrition_entries')
    
    def __init__(self, user_id, entry_type, **kwargs):
        self.user_id = user_id
        self.entry_type = entry_type
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        """Convert nutrition entry to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'entry_type': self.entry_type,
            'name': self.name,
            'meal_type': self.meal_type,
            'water_glasses': self.water_glasses,
            'entry_date': self.entry_date.isoformat(),
            'entry_time': self.entry_time.strftime('%H:%M:%S'),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<NutritionEntry {self.entry_type} - {self.entry_date}>'

class DailyNutritionSummary(db.Model):
    """Daily nutrition summary for quick access"""
    __tablename__ = 'daily_nutrition_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    summary_date = db.Column(db.Date, nullable=False)
    total_meals = db.Column(db.Integer, default=0)
    total_water_glasses = db.Column(db.Integer, default=0)
    mood_score = db.Column(db.String(10), nullable=True)  # emoji or score
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='nutrition_summaries')
    
    def __init__(self, user_id, summary_date, **kwargs):
        self.user_id = user_id
        self.summary_date = summary_date
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        """Convert daily summary to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'summary_date': self.summary_date.isoformat(),
            'total_meals': self.total_meals,
            'total_water_glasses': self.total_water_glasses,
            'mood_score': self.mood_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<DailyNutritionSummary {self.summary_date} - {self.total_meals} meals>' 