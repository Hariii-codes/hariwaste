from datetime import datetime
from app import db

class WasteItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    is_recyclable = db.Column(db.Boolean, default=False)
    is_ewaste = db.Column(db.Boolean, default=False)
    material = db.Column(db.String(100))
    full_analysis = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Fields for marketplace listings
    is_listed = db.Column(db.Boolean, default=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    
    # Municipality routing
    sent_to_municipality = db.Column(db.Boolean, default=False)
    municipality_status = db.Column(db.String(50), default="Not Sent")  # Not Sent, Pending, Accepted, Rejected

    def __repr__(self):
        return f"<WasteItem {self.id}: {'Recyclable' if self.is_recyclable else 'Non-Recyclable'}>"
