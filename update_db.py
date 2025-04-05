"""
Update the database schema to add missing columns.
"""

from app import app, db
from sqlalchemy import text

def update_waste_item_table():
    """Add missing columns to the waste_item table."""
    with app.app_context():
        print("Updating waste_item table schema...")
        # Use modern SQLAlchemy execution API
        with db.engine.connect() as conn:
            # Add material_detection column if it doesn't exist
            conn.execute(text('ALTER TABLE waste_item ADD COLUMN IF NOT EXISTS material_detection TEXT;'))
            
            # Add recycling_completed column if it doesn't exist
            conn.execute(text('ALTER TABLE waste_item ADD COLUMN IF NOT EXISTS recycling_completed BOOLEAN DEFAULT FALSE;'))
            
            # Add recycling_completion_date column if it doesn't exist
            conn.execute(text('ALTER TABLE waste_item ADD COLUMN IF NOT EXISTS recycling_completion_date TIMESTAMP;'))
            
            # Add summary column if it doesn't exist
            conn.execute(text('ALTER TABLE waste_item ADD COLUMN IF NOT EXISTS summary TEXT;'))
            
            conn.commit()
        print("Table schema updated successfully.")

if __name__ == '__main__':
    update_waste_item_table()