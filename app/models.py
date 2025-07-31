# server/app/models.py
# This file defines the database models for the application using Flask-SQLAlchemy.

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the SQLAlchemy object.
# In a full Flask application, this would be initialized in the main __init__.py
# and then imported here. For this file, we define it directly.
db = SQLAlchemy()

class User(db.Model):
    """Represents a player's account."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Relationships ---
    # This creates a one-to-many relationship between User and Character.
    # The 'back_populates' argument links this relationship to the one in the Character model.
    # 'cascade="all, delete-orphan"' means if a User is deleted, their Characters are also deleted.
    characters = db.relationship('Character', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'

class Character(db.Model):
    """Represents a single, playable avatar within the game world."""
    __tablename__ = 'characters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    map_id = db.Column(db.String(50), nullable=False, default='starting_zone')
    position_x = db.Column(db.Float, default=0.0)
    position_y = db.Column(db.Float, default=0.0)

    # --- Foreign Keys ---
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # --- Relationships ---
    # This defines the "many" side of the one-to-many relationship with User.
    user = db.relationship('User', back_populates='characters')
    
    # One-to-many relationship with InventorySlot and CharacterQuest
    inventory = db.relationship('InventorySlot', back_populates='character', cascade="all, delete-orphan")
    quests = db.relationship('CharacterQuest', back_populates='character', cascade="all, delete-orphan")


    def __repr__(self):
        return f'<Character {self.name}>'

class Item(db.Model):
    """A master catalog of every possible item in the game."""
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    item_type = db.Column(db.String(50), nullable=False) # e.g., "Consumable", "Weapon"

    def __repr__(self):
        return f'<Item {self.name}>'

class InventorySlot(db.Model):
    """Links a Character to an Item to represent ownership and quantity."""
    __tablename__ = 'inventory_slots'

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=1)

    # --- Foreign Keys ---
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)

    # --- Relationships ---
    character = db.relationship('Character', back_populates='inventory')
    item = db.relationship('Item')

    def __repr__(self):
        return f'<InventorySlot character_id={self.character_id} item_id={self.item_id} qty={self.quantity}>'

class Quest(db.Model):
    """A master catalog of every possible quest in the game."""
    __tablename__ = 'quests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    reward_xp = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Quest {self.name}>'

class CharacterQuest(db.Model):
    """Tracks the status of a specific quest for a specific character."""
    __tablename__ = 'character_quests'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), default='not_started') # e.g., "in_progress", "completed"

    # --- Foreign Keys ---
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    quest_id = db.Column(db.Integer, db.ForeignKey('quests.id'), nullable=False)

    # --- Relationships ---
    character = db.relationship('Character', back_populates='quests')
    quest = db.relationship('Quest')

    def __repr__(self):
        return f'<CharacterQuest character_id={self.character_id} quest_id={self.quest_id} status={self.status}>'
