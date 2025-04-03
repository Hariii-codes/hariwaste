from datetime import datetime
from app import db, bcrypt
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(120))
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User status and scores
    is_active = db.Column(db.Boolean, default=True)
    eco_points = db.Column(db.Integer, default=0)
    recycling_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    waste_items = db.relationship('WasteItem', backref='user', lazy=True)
    rewards = db.relationship('Reward', backref='user', lazy=True)
    achievements = db.relationship('UserAchievement', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def award_points(self, points):
        self.eco_points += points
        db.session.commit()
    
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
    
    # Drop-off tracking
    is_dropped_off = db.Column(db.Boolean, default=False)
    drop_location_id = db.Column(db.Integer, db.ForeignKey('drop_location.id'), nullable=True)
    drop_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<WasteItem {self.id}: {'Recyclable' if self.is_recyclable else 'Non-Recyclable'}>"


class DropLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accepted_materials = db.Column(db.String(255))  # Comma-separated list of materials
    
    # Relationships
    waste_items = db.relationship('WasteItem', backref='drop_location', lazy=True)
    
    def __repr__(self):
        return f"<DropLocation {self.name}>"


class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    badge_image = db.Column(db.String(255))
    points_awarded = db.Column(db.Integer, default=0)
    
    # Achievement requirements
    required_items = db.Column(db.Integer, default=0)  # Number of items required
    required_material = db.Column(db.String(100))  # Specific material type if applicable
    
    # Relationships
    users = db.relationship('UserAchievement', backref='achievement', lazy=True)
    
    def __repr__(self):
        return f"<Achievement {self.name}>"


class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserAchievement user_id={self.user_id} achievement_id={self.achievement_id}>"


class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    description = db.Column(db.String(255), nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)  # 'drop_off', 'listing', 'achievement'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Reward {self.id}: {self.points} points for {self.reward_type}>"
