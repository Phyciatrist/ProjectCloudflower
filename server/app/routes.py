# server/app/routes.py
# This file defines the API endpoints for the application.

import jwt
from functools import wraps
from flask import request, jsonify, Blueprint, current_app
from .models import db, User, Character
import bcrypt

# Create a Blueprint. A Blueprint is a way to organize a group of related views
# and other code. We will register this blueprint with the main app in __init__.py.
api = Blueprint('api', __name__)

# --- Token Required Decorator ---
# This is a custom decorator that will protect our routes, ensuring only
# authenticated users can access them.
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if the 'x-access-token' header is in the request
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token using the app's SECRET_KEY
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            # Find the user based on the 'public_id' in the token
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        # Pass the user object to the decorated function
        return f(current_user, *args, **kwargs)
    return decorated

# --- Authentication Routes ---

@api.route('/auth/register', methods=['POST'])
def register_user():
    """Endpoint to register a new user."""
    data = request.get_json()

    # Basic validation
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password are required'}), 400

    # Check if user already exists
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'message': 'Username already exists'}), 409

   # --- PEPPERING THE PASSWORD ---
    # Combine the provided password with the secret pepper from the app config
    password_with_pepper = data.get('password') + current_app.config['SECRET_PEPPER']

    # Hash the combined string for security
    hashed_password = bcrypt.hashpw(password_with_pepper.encode('utf-8'), bcrypt.gensalt())

    new_user = User(
        username=data.get('username'),
        email=data.get('email'), # Assuming email is optional for now
        password_hash=hashed_password.decode('utf-8')
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'}), 201

@api.route('/auth/login', methods=['POST'])
def login():
    """Endpoint to authenticate a user and return a token."""
    auth = request.get_json()

    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify'}), 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

    user = User.query.filter_by(username=auth.get('username')).first()

    if not user:
        return jsonify({'message': 'Could not verify'}), 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

    # --- PEPPERING THE PASSWORD ---
        # Combine the provided password with the secret pepper
        password_with_pepper = auth.get('password') + current_app.config['SECRET_PEPPER']
        
        # Check the combined string against the stored hash
        if bcrypt.checkpw(password_with_pepper.encode('utf-8'), user.password_hash.encode('utf-8')):
            # Generate the JWT token
        token = jwt.encode({
            'id': user.id,
            # 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30) # Optional: add expiration
        }, current_app.config['SECRET_KEY'], "HS256")

        return jsonify({'token': token})

    return jsonify({'message': 'Could not verify'}), 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}


# --- Character Routes ---

@api.route('/characters', methods=['POST'])
@token_required
def create_character(current_user):
    """Endpoint to create a new character for the logged-in user."""
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'message': 'Character name is required'}), 400

    new_character = Character(
        name=data['name'],
        user_id=current_user.id
        # Other character attributes can be set here
    )
    db.session.add(new_character)
    db.session.commit()

    return jsonify({'message': 'New character created!'}), 201

@api.route('/characters', methods=['GET'])
@token_required
def get_characters(current_user):
    """Endpoint to get all characters for the logged-in user."""
    characters = Character.query.filter_by(user_id=current_user.id).all()
    output = []

    for character in characters:
        character_data = {}
        character_data['id'] = character.id
        character_data['name'] = character.name
        character_data['level'] = character.level
        character_data['map_id'] = character.map_id
        character_data['position_x'] = character.position_x
        character_data['position_y'] = character.position_y
        output.append(character_data)

    return jsonify({'characters': output})

@api.route('/characters/<int:character_id>', methods=['PUT'])
@token_required
def update_character(current_user, character_id):
    """Endpoint to update a character's data."""
    character = Character.query.filter_by(id=character_id, user_id=current_user.id).first()

    # Ensure the character exists and belongs to the current user
    if not character:
        return jsonify({'message': 'Character not found or access denied'}), 404

    data = request.get_json()
    
    # Update fields if they are provided in the request
    if 'level' in data:
        character.level = data['level']
    if 'experience' in data:
        character.experience = data['experience']
    if 'map_id' in data:
        character.map_id = data['map_id']
    if 'position_x' in data:
        character.position_x = data['position_x']
    if 'position_y' in data:
        character.position_y = data['position_y']

    db.session.commit()

    return jsonify({'message': 'Character has been updated.'})
