from app import db
from datetime import datetime

class ExerciseSession(db.Model):
    
    __tablename__ = 'exercise_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise_type = db.Column(db.String(50), nullable=False)  # jumping-jacks, push-ups, etc.
    exercise_name = db.Column(db.String(100), nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=True)
    session_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    user = db.relationship('User', backref='exercise_sessions')
    
    def __init__(self, user_id, exercise_type, exercise_name, duration_seconds, **kwargs):
        self.user_id = user_id
        self.exercise_type = exercise_type
        self.exercise_name = exercise_name
        self.duration_seconds = duration_seconds
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exercise_type': self.exercise_type,
            'exercise_name': self.exercise_name,
            'duration_seconds': self.duration_seconds,
            'duration_minutes': round(self.duration_seconds / 60, 1),
            'completed': self.completed,
            'session_date': self.session_date.isoformat(),
            'completed_at': self.completed_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ExerciseSession {self.exercise_name} - {self.session_date}>'

class MeditationSession(db.Model):
    
    __tablename__ = 'meditation_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_type = db.Column(db.String(50), nullable=False)  # 'basic', 'box', '478', etc.
    session_name = db.Column(db.String(100), nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=False)
    breath_count = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=True)
    session_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='meditation_sessions')
    
    def __init__(self, user_id, session_type, session_name, duration_seconds, **kwargs):
        self.user_id = user_id
        self.session_type = session_type
        self.session_name = session_name
        self.duration_seconds = duration_seconds
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_type': self.session_type,
            'session_name': self.session_name,
            'duration_seconds': self.duration_seconds,
            'duration_minutes': round(self.duration_seconds / 60, 1),
            'breath_count': self.breath_count,
            'completed': self.completed,
            'session_date': self.session_date.isoformat(),
            'completed_at': self.completed_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<MeditationSession {self.session_name} - {self.session_date}>'

class BreathingMethod(db.Model):
   
    __tablename__ = 'breathing_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    method_type = db.Column(db.String(50), nullable=False)  # 'box', '478', 'triangle', 'alternate'
    method_name = db.Column(db.String(100), nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=False)
    cycles_completed = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=True)
    session_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='breathing_sessions')
    
    def __init__(self, user_id, method_type, method_name, duration_seconds, **kwargs):
        self.user_id = user_id
        self.method_type = method_type
        self.method_name = method_name
        self.duration_seconds = duration_seconds
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'method_type': self.method_type,
            'method_name': self.method_name,
            'duration_seconds': self.duration_seconds,
            'duration_minutes': round(self.duration_seconds / 60, 1),
            'cycles_completed': self.cycles_completed,
            'completed': self.completed,
            'session_date': self.session_date.isoformat(),
            'completed_at': self.completed_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<BreathingMethod {self.method_name} - {self.session_date}>' 