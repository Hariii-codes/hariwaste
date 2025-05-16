"""
Update the database schema to add missing columns.
<<<<<<< HEAD
Uses explicit transaction management and better error handling.
"""

=======
Uses explicit transaction management and better error handling for deployments.
"""

import os
>>>>>>> 29a39b63817c010f5cf573453f1150bf94574afe
import sys
import logging
from app import app, db
from sqlalchemy import text, inspect

<<<<<<< HEAD
# Configure logging
=======
# Configure more detailed logging
>>>>>>> 29a39b63817c010f5cf573453f1150bf94574afe
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def check_if_table_exists(conn, table_name):
    """Check if a table exists in the database."""
    inspector = inspect(db.engine)
    exists = table_name in inspector.get_table_names()
    logging.info(f"Table '{table_name}' exists: {exists}")
    return exists

def check_if_column_exists(conn, table_name, column_name):
    """Check if a column exists in a table."""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    exists = column_name in columns
    logging.info(f"Column '{column_name}' in table '{table_name}' exists: {exists}")
    return exists

<<<<<<< HEAD
def add_column_if_missing(conn, table_name, column_name, column_type_sql):
    """Add a column if it's missing."""
    if not check_if_column_exists(conn, table_name, column_name):
        logging.info(f"Adding column '{column_name}' to '{table_name}'...")
        # Escape identifiers using double quotes
        conn.execute(text(f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_type_sql};'))
    else:
        logging.info(f"Column '{column_name}' already exists. Skipping...")

def update_waste_item_table():
    """Add missing columns to the waste_item table."""
    with app.app_context():
        logging.info("Starting database schema update...")
        try:
            with db.engine.begin() as conn:
                table_name = 'waste_item'

                if not check_if_table_exists(conn, table_name):
                    logging.warning(f"Table '{table_name}' doesn't exist.")
                    return

                # Required columns and their types (SQLite-safe)
                required_columns = {
                    'user_id': 'INTEGER',
                    'material_detection': 'TEXT',
                    'recycling_completed': 'INTEGER DEFAULT 0',  # BOOLEAN in SQLite
                    'recycling_completion_date': 'TIMESTAMP',
                    'summary': 'TEXT',
                    'is_dropped_off': 'INTEGER DEFAULT 0',  # BOOLEAN in SQLite
                    'drop_location_id': 'INTEGER',
                    'drop_date': 'TIMESTAMP'
                }

                for column, column_type in required_columns.items():
                    add_column_if_missing(conn, table_name, column, column_type)

            logging.info("✅ Database schema update completed successfully.")
        except Exception as e:
            logging.error(f"❌ Error updating database schema: {str(e)}")

if __name__ == '__main__':
    update_waste_item_table()
=======
def update_waste_item_table():
    """Add missing columns to the waste_item table with better error handling."""
    with app.app_context():
        logging.info("Starting database schema update...")
        try:
            # Use modern SQLAlchemy execution API with explicit transaction
            with db.engine.begin() as conn:
                # First check if the table exists
                if not check_if_table_exists(conn, 'waste_item'):
                    logging.warning("waste_item table doesn't exist yet. Will be created by app startup.")
                    return

                # Add material_detection column if it doesn't exist
                if not check_if_column_exists(conn, 'waste_item', 'material_detection'):
                    logging.info("Adding material_detection column...")
                    conn.execute(text('ALTER TABLE waste_item ADD COLUMN material_detection TEXT;'))
                
                # Add recycling_completed column if it doesn't exist
                if not check_if_column_exists(conn, 'waste_item', 'recycling_completed'):
                    logging.info("Adding recycling_completed column...")
                    conn.execute(text('ALTER TABLE waste_item ADD COLUMN recycling_completed BOOLEAN DEFAULT FALSE;'))
                
                # Add recycling_completion_date column if it doesn't exist
                if not check_if_column_exists(conn, 'waste_item', 'recycling_completion_date'):
                    logging.info("Adding recycling_completion_date column...")
                    conn.execute(text('ALTER TABLE waste_item ADD COLUMN recycling_completion_date TIMESTAMP;'))
                
                # Add summary column if it doesn't exist
                if not check_if_column_exists(conn, 'waste_item', 'summary'):
                    logging.info("Adding summary column...")
                    conn.execute(text('ALTER TABLE waste_item ADD COLUMN summary TEXT;'))
                
                # Transaction is committed automatically at the end of the 'with' block
            
            logging.info("Database schema update completed successfully.")
        except Exception as e:
            logging.error(f"Error updating database schema: {str(e)}")
            # We don't raise the exception here as we want the deployment to continue
            # even if there was an issue with the schema update

if __name__ == '__main__':
    update_waste_item_table()
>>>>>>> 29a39b63817c010f5cf573453f1150bf94574afe
