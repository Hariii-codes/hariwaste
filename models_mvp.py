from datetime import datetime
import json
from app import db
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User status
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    waste_items = db.relationship('WasteItem', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.username}>"


class WasteItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    is_recyclable = db.Column(db.Boolean, default=False)
    is_ewaste = db.Column(db.Boolean, default=False)
    material = db.Column(db.String(100))
    full_analysis = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Additional analysis fields
    recycling_instructions = db.Column(db.Text)
    environmental_impact = db.Column(db.Text)
    disposal_recommendations = db.Column(db.Text)
    
    # Material detection results (stored as JSON string)
    _material_detection = db.Column('material_detection', db.Text, nullable=True)
    
    # Fields for marketplace listings
    is_listed = db.Column(db.Boolean, default=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    
    @property
    def material_detection(self):
        """Getter: Deserialize JSON string to Python dictionary"""
        if self._material_detection:
            return json.loads(self._material_detection)
        return {}
    
    @material_detection.setter
    def material_detection(self, value):
        """Setter: Serialize Python dictionary to JSON string"""
        if value:
            self._material_detection = json.dumps(value)
        else:
            self._material_detection = None
    
    def __repr__(self):
        return f"<WasteItem {self.id}>"


class DropLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accepted_materials = db.Column(db.String(255))  # Comma-separated list of materials
    
    def __repr__(self):
        return f"<DropLocation {self.name}>"