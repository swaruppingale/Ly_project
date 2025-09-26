from app import db
from datetime import datetime

class Resource(db.Model):
    """Resource model for mental health educational content"""
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)  # e.g., "Anxiety", "Depression", "Meditation"
    type = db.Column(db.String(50), nullable=False)  # e.g., "Article", "Video", "Exercise"
    url = db.Column(db.String(500), nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # in minutes
    difficulty_level = db.Column(db.String(20), nullable=True)  # "Beginner", "Intermediate", "Advanced"
    tags = db.Column(db.Text, nullable=True)  # JSON string of tags
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, title, description, content, category, type, **kwargs):
        self.title = title
        self.description = description
        self.content = content
        self.category = category
        self.type = type
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        """Convert resource to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'category': self.category,
            'type': self.type,
            'url': self.url,
            'duration': self.duration,
            'difficulty_level': self.difficulty_level,
            'tags': self.tags,
            'is_featured': self.is_featured,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Resource {self.title}>' 