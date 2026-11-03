"""
Apla Shetkari – AI Helper for Farmers
Main Flask Application
"""

import os
import sys
import time
import json
from functools import wraps

# Ensure UTF-8 output on Windows consoles
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, g
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
import database
import ai_service

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Ensure database tables exist on startup
with app.app_context():
    database.init_db()

# ----------------- Authentication Helpers -----------------

def login_required(f):
    """Decorator to protect routes that require user authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("कृपया पुढे जाण्यासाठी आधी लॉगिन करा (Please log in to continue).", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_logged_in_user():
    """Loads currently logged-in user into Flask's g object for easy template access."""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        try:
            g.user = database.get_user_by_id(user_id)
        except Exception:
            g.user = None

@app.context_processor
def inject_global_data():
    """Injects common context variables across all Jinja2 templates."""
    return {
        'current_user': g.user,
        'app_name': 'Apla Shetkari',
        'tagline': 'Smart Farming, Better Future',
        'has_gemini_key': bool(Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != 'your_gemini_api_key_here')
    }

# ----------------- Core Routes -----------------

@app.route('/')
def index():
    """Homepage: hero section, features, agriculture tips, about section."""
    return render_template('index.html')

@app.route('/about')
def about():
    """About Us page: Mission, vision, technical overview, and farming advisor principles."""
    return render_template('about.html')

# ----------------- User Authentication Routes -----------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles farmer registration."""
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        state = request.form.get('state', '').strip()
        district = request.form.get('district', '').strip()

        # Input validations
        errors = []
        if not full_name or len(full_name) < 2:
            errors.append("Please provide your valid full name.")
        if not mobile or len(mobile) < 10 or not mobile.isdigit():
            errors.append("Please enter a valid 10-digit mobile number.")
        if not email or '@' not in email:
            errors.append("Please enter a valid email address.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if not state:
            errors.append("Please select your State.")
        if not district:
            errors.append("Please enter your District.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template('register.html', form_data=request.form)

        # Check existing user
        try:
            existing_user = database.get_user_by_email_or_mobile(email)
            if not existing_user:
                existing_user = database.get_user_by_email_or_mobile(mobile)

            if existing_user:
                flash("An account with this mobile number or email already exists. Please log in.", "warning")
                return redirect(url_for('login'))

            password_hash = generate_password_hash(password)
            user_id = database.create_user(full_name, mobile, email, password_hash, state, district)

            session.clear()
            session['user_id'] = user_id
            session['user_name'] = full_name
            flash(f"Welcome to Apla Shetkari, {full_name}! Your account has been created successfully.", "success")
            return redirect(url_for('dashboard'))

        except Exception as e:
            flash(f"Error during registration: {str(e)}", "danger")
            return render_template('register.html', form_data=request.form)

    return render_template('register.html', form_data={})

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles farmer login via Email or Mobile number."""
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        if not identifier or not password:
            flash("Please enter both Mobile/Email and Password.", "warning")
            return render_template('login.html', identifier=identifier)

        try:
            user = database.get_user_by_email_or_mobile(identifier)
            if user and check_password_hash(user['password_hash'], password):
                session.clear()
                session['user_id'] = user['id']
                session['user_name'] = user['full_name']
                flash(f"Welcome back, {user['full_name']}! (नमस्कार शेतकरी बंधू)", "success")
                
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid login credentials. Please check your mobile/email and password.", "danger")
        except Exception as e:
            flash(f"Login error: {str(e)}", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs out current user and clears session."""
    session.clear()
    flash("You have been successfully logged out. धन्यवाद!", "info")
    return redirect(url_for('index'))

# ----------------- Dashboard Route -----------------

@app.route('/dashboard')
@login_required
def dashboard():
    """Farmer personal dashboard showing stats, recent chats, and saved recommendations."""
    user_id = session.get('user_id')
    stats = database.get_user_dashboard_stats(user_id)
    chat_history = database.get_chat_history(user_id, limit=20)
    saved_recommendations = database.get_crop_recommendations(user_id, limit=10)

    # Process JSON recommendations for presentation
    parsed_recommendations = []
    for rec in saved_recommendations:
        try:
            crops_data = json.loads(rec['recommended_crops'])
        except Exception:
            crops_data = []
        parsed_recommendations.append({
            'id': rec['id'],
            'soil_type': rec['soil_type'],
            'location': rec['location'],
            'season': rec['season'],
            'created_at': rec['created_at'],
            'crops': crops_data
        })

    return render_template(
        'dashboard.html',
        stats=stats,
        chat_history=chat_history,
        recommendations=parsed_recommendations
    )

# ----------------- AI Chatbot Routes -----------------

@app.route('/chat')
def chat():
    """Renders the AI Farming Chatbot page."""
    user_id = session.get('user_id')
    # Load recent history if logged in
    previous_history = []
    if user_id:
        previous_history = database.get_chat_history(user_id, limit=30)
    return render_template('chatbot.html', previous_history=previous_history)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """
    JSON API endpoint for chatbot communication.
    Accepts: { "message": "...", "language": "English|Hindi|Marathi" }
    """
    data = request.get_json(silent=True) or request.form
    user_message = data.get('message', '').strip()
    language = data.get('language', 'English').strip()
    user_id = session.get('user_id')

    if not user_message:
        return jsonify({"success": False, "error": "Please enter a valid farming question."}), 400

    # Basic rate limiting: at least 1.5 seconds between queries per session
    now = time.time()
    last_query_time = session.get('last_chat_ts', 0)
    if now - last_query_time < 1.2:
        return jsonify({
            "success": False,
            "error": "कृपया थोडा वेळ थांबा (Please wait a moment before sending another message)."
        }), 429
    session['last_chat_ts'] = now

    # Retrieve recent context for logged-in user
    chat_context = []
    if user_id:
        chat_context = database.get_chat_history(user_id, limit=5)

    # Call AI service
    success, ai_reply = ai_service.get_chat_response(
        user_message=user_message,
        language=language,
        chat_history=chat_context
    )

    if success:
        # Save to database
        try:
            database.save_chat_message(user_id, user_message, ai_reply)
        except Exception as e:
            app.logger.warning(f"Could not persist chat message: {e}")

        return jsonify({
            "success": True,
            "response": ai_reply,
            "language": language
        })
    else:
        return jsonify({
            "success": False,
            "error": ai_reply
        }), 200

@app.route('/chat-history')
@login_required
def chat_history():
    """Dedicated view for full chat history."""
    user_id = session.get('user_id')
    history = database.get_chat_history(user_id, limit=100)
    return render_template('dashboard.html', chat_history=history, active_tab='chats')

@app.route('/clear-history', methods=['POST'])
def clear_history():
    """Clears conversation history for the logged-in user."""
    user_id = session.get('user_id')
    if user_id:
        database.clear_chat_history(user_id)
        if request.is_json:
            return jsonify({"success": True, "message": "Chat history cleared successfully."})
        flash("Your chat history has been cleared.", "info")
        return redirect(url_for('chat'))
    return jsonify({"success": True, "message": "History cleared for guest."})

# ----------------- Crop Recommendation Routes -----------------

@app.route('/crop-recommendation', methods=['GET', 'POST'])
def crop_recommendation():
    """
    Dedicated Crop Recommendation system.
    Supports both traditional POST with server rendering and AJAX JSON requests.
    """
    user_id = session.get('user_id')
    results = None
    form_data = {}

    if request.method == 'POST':
        state = request.form.get('state', '').strip()
        district = request.form.get('district', '').strip()
        soil_type = request.form.get('soil_type', '').strip()
        land_area = request.form.get('land_area', '').strip()
        season = request.form.get('season', '').strip()
        water_availability = request.form.get('water_availability', '').strip()
        previous_crop = request.form.get('previous_crop', '').strip()
        language = request.form.get('language', 'English').strip()

        form_data = {
            'state': state,
            'district': district,
            'soil_type': soil_type,
            'land_area': land_area,
            'season': season,
            'water_availability': water_availability,
            'previous_crop': previous_crop,
            'language': language
        }

        # Validation
        if not (state and district and soil_type and season and water_availability):
            flash("Please fill in all required fields (State, District, Soil, Season, Water).", "warning")
            return render_template('crop_recommendation.html', form_data=form_data, results=None)

        success, crops_data, msg = ai_service.get_crop_recommendations_ai(
            state=state,
            district=district,
            soil_type=soil_type,
            land_area=land_area or "1 Acre",
            season=season,
            water_availability=water_availability,
            previous_crop=previous_crop,
            language=language
        )

        if success and crops_data:
            results = crops_data
            # Save recommendation in database if user is logged in
            if user_id:
                try:
                    location_str = f"{district}, {state}"
                    database.save_crop_recommendation(
                        user_id=user_id,
                        soil_type=soil_type,
                        location=location_str,
                        season=season,
                        recommended_crops_json=json.dumps(crops_data)
                    )
                except Exception as e:
                    app.logger.warning(f"Could not persist crop recommendation: {e}")
            flash(f"Found {len(crops_data)} tailored crop recommendations for your field!", "success")
        else:
            flash(msg, "danger")

    # Pre-fill location from logged in user if available
    elif g.user and not form_data.get('state'):
        form_data['state'] = g.user['state']
        form_data['district'] = g.user['district']

    return render_template('crop_recommendation.html', form_data=form_data, results=results)

@app.route('/api/crop-recommendation', methods=['POST'])
def api_crop_recommendation():
    """AJAX endpoint for generating crop recommendations asynchronously."""
    data = request.get_json(silent=True) or request.form
    state = data.get('state', '').strip()
    district = data.get('district', '').strip()
    soil_type = data.get('soil_type', '').strip()
    land_area = data.get('land_area', '1 Acre').strip()
    season = data.get('season', '').strip()
    water_availability = data.get('water_availability', '').strip()
    previous_crop = data.get('previous_crop', '').strip()
    language = data.get('language', 'English').strip()
    user_id = session.get('user_id')

    if not (state and district and soil_type and season and water_availability):
        return jsonify({"success": False, "error": "Please provide State, District, Soil Type, Season, and Water Availability."}), 400

    success, crops, msg = ai_service.get_crop_recommendations_ai(
        state=state,
        district=district,
        soil_type=soil_type,
        land_area=land_area,
        season=season,
        water_availability=water_availability,
        previous_crop=previous_crop,
        language=language
    )

    if success and crops:
        if user_id:
            try:
                database.save_crop_recommendation(
                    user_id=user_id,
                    soil_type=soil_type,
                    location=f"{district}, {state}",
                    season=season,
                    recommended_crops_json=json.dumps(crops)
                )
            except Exception as e:
                app.logger.warning(f"Error saving crop recommendation: {e}")

        return jsonify({"success": True, "crops": crops, "message": msg})
    else:
        return jsonify({"success": False, "error": msg}), 200

# ----------------- Profile Update Route -----------------

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Updates user's name and location."""
    user_id = session.get('user_id')
    full_name = request.form.get('full_name', '').strip()
    state = request.form.get('state', '').strip()
    district = request.form.get('district', '').strip()

    if full_name and state and district:
        database.update_user_profile(user_id, full_name, state, district)
        session['user_name'] = full_name
        flash("Your profile details have been updated successfully.", "success")
    else:
        flash("Please provide valid details for all fields.", "warning")

    return redirect(url_for('dashboard'))

# ----------------- Error Handlers -----------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', not_found=True), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error occurred."}), 500

if __name__ == '__main__':
    port = Config.PORT
    debug = Config.DEBUG
    print(f"Starting Apla Shetkari Web Application on http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=debug)
