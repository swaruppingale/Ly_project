"""
Migration script to add sentiment column to journal_entries table
Run this script to add the sentiment column to existing database
"""

from app import create_app, db
import sqlite3
import os

def migrate():
    """Add sentiment column to journal_entries table"""
    app = create_app()

    with app.app_context():
        print("Adding sentiment column to journal_entries table...")

        # For SQLite, use raw SQL to add column
        db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'mental_health_dev.db')

        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check if column exists
            cursor.execute("PRAGMA table_info(journal_entries)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'sentiment' not in columns:
                cursor.execute("ALTER TABLE journal_entries ADD COLUMN sentiment VARCHAR(20)")
                conn.commit()
                print("✅ Sentiment column added successfully!")
            else:
                print("✅ Sentiment column already exists.")

            conn.close()
        else:
            print("Database file not found. New installations will have the column.")

if __name__ == "__main__":
    migrate()
