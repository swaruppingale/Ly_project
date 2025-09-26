from app import db
from datetime import datetime

class JournalEntry(db.Model):
    """Journal entry model for personal diary entries"""
    __tablename__ = 'journal_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=False)
    mood_before = db.Column(db.Integer, nullable=True)  # 1-10 scale
    mood_after = db.Column(db.Integer, nullable=True)  # 1-10 scale
    tags = db.Column(db.Text, nullable=True)  # JSON string of tags
    is_private = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, content, **kwargs):
        self.user_id = user_id
        self.content = content
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        """Convert journal entry to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'mood_before': self.mood_before,
            'mood_after': self.mood_after,
            'tags': self.tags,
            'is_private': self.is_private,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<JournalEntry {self.title or "Untitled"}>' 