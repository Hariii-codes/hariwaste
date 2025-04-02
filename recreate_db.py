from app import app, db
import logging

print("Starting database recreation...")
logging.basicConfig(level=logging.INFO)

with app.app_context():
    logging.info("Dropping all tables...")
    db.drop_all()
    
    logging.info("Creating all tables...")
    db.create_all()
    
    logging.info("Database recreation complete!")