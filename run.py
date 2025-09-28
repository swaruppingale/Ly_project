from app import create_app, db
from app.models.user import User
from app.models.mood import MoodEntry
from app.models.journal import JournalEntry
from app.models.resource import Resource
from flask import render_template, jsonify, redirect, request
from datetime import datetime

app = create_app()

@app.route('/')
def index():
    """Root endpoint - redirect to login"""
    return redirect('/login')

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')

@app.route('/mood')
def mood():
    """Mood tracking page"""
    return render_template('mood.html')

@app.route('/journal')
def journal():
    """Journal page"""
    return render_template('journal.html')

@app.route('/resources')
def resources():
    """Resources page"""
    return render_template('resources.html')

@app.route('/analytics')
def analytics():
    """Analytics page"""
    return render_template('analytics.html')

@app.route('/profile')
def profile():
    """Profile page"""
    return render_template('profile.html')

@app.route('/quiz')
def quiz():
    """Quiz page"""
    return render_template('quiz.html')

@app.route('/api')
def api_info():
    """API information endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Mental Health API is running',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'user': '/api/user',
            'mood': '/api/mood',
            'journal': '/api/journal',
            'resources': '/api/resources'
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 