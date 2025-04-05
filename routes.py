import os
import uuid
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app, jsonify
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from app import db
from models import WasteItem, DropLocation

main_bp = Blueprint('main', __name__)

def register_routes(app):
    """Register main application routes"""
    app.register_blueprint(main_bp)

@main_bp.route("/")
def index():
    """Home page route"""
    return render_template('index.html', title='Home')
    
@main_bp.route("/analyze", methods=['GET', 'POST'])
def analyze():
    """Analyze waste item page"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file:
            # Generate unique filename
            _, file_ext = os.path.splitext(file.filename)
            filename = f"{uuid.uuid4()}{file_ext}"
            
            # Save file
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Create waste item record
            waste_item = WasteItem(
                image_path=os.path.join('uploads', filename),
            )
            
            # Associate with user if logged in
            if current_user.is_authenticated:
                waste_item.user_id = current_user.id
                
            db.session.add(waste_item)
            db.session.commit()
            
            # Redirect to analysis page
            return redirect(url_for('main.item_details', item_id=waste_item.id))
            
    return render_template('analyze.html', title='Analyze Waste')
    
@main_bp.route("/item/<int:item_id>")
def item_details(item_id):
    """Display waste item details"""
    waste_item = WasteItem.query.get_or_404(item_id)
    return render_template('item_details.html', title='Waste Analysis', item=waste_item)
    
@main_bp.route("/marketplace")
def marketplace():
    """Marketplace of listed recyclable items"""
    items = WasteItem.query.filter_by(is_listed=True).order_by(WasteItem.created_at.desc()).all()
    return render_template('marketplace.html', title='Marketplace', items=items)
    
@main_bp.route("/list_item/<int:item_id>", methods=['GET', 'POST'])
@login_required
def list_item(item_id):
    """List a recyclable item in the marketplace"""
    waste_item = WasteItem.query.get_or_404(item_id)
    
    # Ensure item belongs to current user
    if waste_item.user_id != current_user.id:
        flash('You can only list your own items', 'danger')
        return redirect(url_for('main.marketplace'))
        
    if request.method == 'POST':
        waste_item.title = request.form.get('title')
        waste_item.description = request.form.get('description')
        waste_item.contact_email = request.form.get('contact_email')
        waste_item.contact_phone = request.form.get('contact_phone')
        waste_item.location = request.form.get('location')
        waste_item.is_listed = True
        
        db.session.commit()
        flash('Your item has been listed in the marketplace!', 'success')
        return redirect(url_for('main.marketplace'))
        
    return render_template('list_item.html', title='List Item', item=waste_item)
    
@main_bp.route("/my_items")
@login_required
def my_items():
    """Display user's waste items"""
    items = WasteItem.query.filter_by(user_id=current_user.id).order_by(WasteItem.created_at.desc()).all()
    return render_template('my_items.html', title='My Items', items=items)
    
@main_bp.route("/drop_locations")
def drop_locations():
    """Display map of drop locations"""
    locations = DropLocation.query.all()
    return render_template('drop_locations.html', title='Drop Locations', locations=locations)

@main_bp.route("/api/drop_locations")
def api_drop_locations():
    """API endpoint for drop locations data"""
    locations = DropLocation.query.all()
    locations_data = []
    
    for location in locations:
        materials = location.accepted_materials.split(',') if location.accepted_materials else []
        locations_data.append({
            'id': location.id,
            'name': location.name,
            'address': location.address,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'accepted_materials': materials
        })
        
    return jsonify(locations_data)