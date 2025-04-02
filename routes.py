import os
import uuid
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from app import db
from models import WasteItem
from gemini_service import analyze_waste
import logging

def register_routes(app):
    """Register all application routes"""
    
    @app.route("/", methods=["GET", "POST"])
    def index():
        """Handle home page and waste image uploads"""
        result = None
        image_path = None
        waste_item = None
        
        if request.method == "POST":
            if "file" not in request.files:
                flash("No file uploaded", "danger")
                return redirect(request.url)
            
            file = request.files["file"]
            if file.filename == "":
                flash("No selected file", "danger")
                return redirect(request.url)
            
            if file:
                try:
                    # Generate unique filename to prevent overwrites
                    filename = secure_filename(file.filename)
                    filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    
                    # Save the uploaded file
                    file.save(file_path)
                    
                    # Analyze the image using Gemini AI
                    analysis_result = analyze_waste(file_path)
                    
                    if "error" in analysis_result:
                        flash(f"Analysis error: {analysis_result['error']}", "danger")
                        return render_template("index.html")
                    
                    # Create a new waste item record in the database with additional fields
                    waste_item = WasteItem(
                        image_path=file_path.replace("static/", ""),
                        is_recyclable=analysis_result["is_recyclable"],
                        is_ewaste=analysis_result["is_ewaste"],
                        material=analysis_result["material"],
                        full_analysis=analysis_result["full_analysis"],
                        recycling_instructions=analysis_result.get("recycling_instructions", ""),
                        environmental_impact=analysis_result.get("environmental_impact", ""),
                        disposal_recommendations=analysis_result.get("disposal_recommendations", "")
                    )
                    db.session.add(waste_item)
                    db.session.commit()
                    
                    # Store the waste item ID in session for listing form
                    session["last_analyzed_item_id"] = waste_item.id
                    
                    # Set display paths
                    image_path = "/" + file_path
                    result = analysis_result
                    
                except Exception as e:
                    logging.error(f"Error processing upload: {e}")
                    flash(f"Error processing upload: {str(e)}", "danger")
        
        return render_template("index.html", result=result, image_path=image_path, waste_item=waste_item)
    
    @app.route("/marketplace")
    def marketplace():
        """Display marketplace listings"""
        items = WasteItem.query.filter_by(is_listed=True).order_by(WasteItem.created_at.desc()).all()
        return render_template("marketplace.html", items=items)
    
    @app.route("/municipality")
    def municipality():
        """Display items routed to municipality"""
        items = WasteItem.query.filter_by(sent_to_municipality=True).order_by(WasteItem.created_at.desc()).all()
        return render_template("municipality.html", items=items)
    
    @app.route("/item/<int:item_id>")
    def item_details(item_id):
        """Display details for a specific item"""
        item = WasteItem.query.get_or_404(item_id)
        return render_template("item_details.html", item=item)
    
    @app.route("/list-item", methods=["GET", "POST"])
    def list_item():
        """Handle marketplace listing form"""
        if "last_analyzed_item_id" not in session:
            flash("No recently analyzed item to list", "warning")
            return redirect(url_for("index"))
        
        item_id = session["last_analyzed_item_id"]
        item = WasteItem.query.get_or_404(item_id)
        
        if request.method == "POST":
            item.title = request.form.get("title")
            item.description = request.form.get("description")
            item.contact_email = request.form.get("contact_email")
            item.contact_phone = request.form.get("contact_phone")
            item.location = request.form.get("location")
            item.is_listed = True
            
            # If item is plastic, automatically route to municipality
            if item.material.lower() == "plastic":
                item.sent_to_municipality = True
                item.municipality_status = "Pending"
                flash("This plastic item has been automatically sent to the municipality", "info")
            
            db.session.commit()
            flash("Item listed successfully", "success")
            
            # Clear the session variable
            session.pop("last_analyzed_item_id", None)
            
            return redirect(url_for("marketplace"))
        
        return render_template("listing_form.html", item=item)
    
    @app.route("/send-to-municipality/<int:item_id>", methods=["POST"])
    def send_to_municipality(item_id):
        """Route an item to municipality"""
        item = WasteItem.query.get_or_404(item_id)
        item.sent_to_municipality = True
        item.municipality_status = "Pending"
        db.session.commit()
        flash("Item sent to municipality successfully", "success")
        return redirect(url_for("item_details", item_id=item_id))
    
    @app.route("/update-municipality-status/<int:item_id>", methods=["POST"])
    def update_municipality_status(item_id):
        """Update municipality status (for demo purposes)"""
        item = WasteItem.query.get_or_404(item_id)
        status = request.form.get("status")
        if status in ["Pending", "Accepted", "Rejected"]:
            item.municipality_status = status
            db.session.commit()
            flash(f"Status updated to {status}", "success")
        return redirect(url_for("municipality"))
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("error.html", error="Page not found"), 404
    
    @app.route("/drop-points")
    def drop_points():
        """Display map with waste drop points in Bangalore"""
        # Predefined drop points in Bangalore
        drop_points = [
            {
                "name": "Dry Waste Collection Center - Koramangala",
                "lat": 12.9352,
                "lon": 77.6245,
                "address": "Koramangala 3rd Block, Bengaluru",
                "types": ["Plastic", "Paper", "Glass"]
            },
            {
                "name": "E-Waste Collection Center - Indiranagar",
                "lat": 12.9784,
                "lon": 77.6408,
                "address": "100 Feet Road, Indiranagar, Bengaluru",
                "types": ["E-Waste", "Batteries"]
            },
            {
                "name": "Saahas Zero Waste - HSR Layout",
                "lat": 12.9116,
                "lon": 77.6473,
                "address": "HSR Layout, Bengaluru",
                "types": ["Plastic", "Paper", "Organic"]
            },
            {
                "name": "ITC WOW Collection Point - Whitefield",
                "lat": 12.9698,
                "lon": 77.7500,
                "address": "Whitefield, Bengaluru",
                "types": ["Paper", "Cardboard"]
            },
            {
                "name": "BBMP Recycling Center - Jayanagar",
                "lat": 12.9250,
                "lon": 77.5938,
                "address": "Jayanagar 4th Block, Bengaluru",
                "types": ["Plastic", "Metal", "Glass", "Paper"]
            }
        ]
        return render_template("drop_points.html", drop_points=drop_points)

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", error="Server error"), 500
