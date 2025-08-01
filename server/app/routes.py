```python
# server/app/routes.py
# --- CORRECTED FILE ---

import jwt
from functools import wraps
from flask import request, jsonify, Blueprint, current_app
# We import the db object from __init__.py and the Models from models.py
from . import db
from .models import User, Character
import bcrypt

api = Blueprint('api', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['id']).first()
        except Exception:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@api.route('/auth/register', methods=['POST'])
def register_user():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password are required'}), 400

    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'message': 'Username already exists'}), 409

    hashed_password = bcrypt.hashpw(data.get('password').encode('utf-8'), bcrypt.gensalt())

    new_user = User(
        username=data.get('username'),
        email=data.get('email'),
        password_hash=hashed_password.decode('utf-8')
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'}), 201

# --- The rest of the routes (login, create_character, etc.)
# --- remain the same. They will now work correctly because they
# --- are using the proper 'db' and 'User' objects.

@api.route('/auth/login', methods=['POST'])
def login():
    auth = request.get_json()

    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify'}), 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

    user = User.query.filter_by(username=auth.get('username')).first()

    if not user:
        return jsonify({'message': 'Could not verify'}), 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

    if bcrypt.checkpw(auth.get('password').encode('utf-8'), user.password_hash.encode('utf-8')):
        token = jwt.encode({
            'id': user.id,
        }, current_app.config['SECRET_KEY'], "HS256")

        return jsonify({'token': token})

    return jsonify({'message': 'Could not verify'}), 401, {'WWW-Authenticate': 'Basic realm="Login required!"'}

@api.route('/characters', methods=['POST'])
@token_required
def create_character(current_user):
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'message': 'Character name is required'}), 400

    new_character = Character(name=data['name'], user_id=current_user.id)
    db.session.add(new_character)
    db.session.commit()

    return jsonify({'message': 'New character created!'}), 201

@api.route('/characters', methods=['GET'])
@token_required
def get_characters(current_user):
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
    character = Character.query.filter_by(id=character_id, user_id=current_user.id).first()

    if not character:
        return jsonify({'message': 'Character not found or access denied'}), 404

    data = request.get_json()
    
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

# --- END OF routes.py ---
