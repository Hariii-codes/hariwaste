"""
Update the database schema to add the material_detection column.
"""

from app import app, db
from sqlalchemy import text

def add_material_detection_column():
    """Add the material_detection column to the waste_item table."""
    with app.app_context():
        print("Adding material_detection column to waste_item table...")
        # Use modern SQLAlchemy execution API
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE waste_item ADD COLUMN IF NOT EXISTS material_detection TEXT;'))
            conn.commit()
        print("Column added successfully.")

if __name__ == '__main__':
    add_material_detection_column()