# server/app/models.py
"""This file defines the database models for the application using Flask-SQLAlchemy."""

# 1. Standard library imports
from datetime import datetime

# 2. Local application imports
from . import db


class User(db.Model):
    """Represents a player's account."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    characters = db.relationship(
        'Character',
        back_populates='user',
        cascade="all, delete-orphan"
    )

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

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='characters')

    inventory = db.relationship(
        'InventorySlot',
        back_populates='character',
        cascade="all, delete-orphan"
    )
    quests = db.relationship(
        'CharacterQuest',
        back_populates='character',
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f'<Character {self.name}>'


class Item(db.Model):
    """A master catalog of every possible item in the game."""
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    item_type = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Item {self.name}>'


class InventorySlot(db.Model):
    """Links a Character to an Item to represent ownership and quantity."""
    __tablename__ = 'inventory_slots'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    character = db.relationship('Character', back_populates='inventory')
    item = db.relationship('Item')

    def __repr__(self):
        return f'<InventorySlot character_id={self.character_id} item_id={self.item_id}>'


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
    status = db.Column(db.String(50), default='not_started')
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    quest_id = db.Column(db.Integer, db.ForeignKey('quests.id'), nullable=False)
    character = db.relationship('Character', back_populates='quests')
    quest = db.relationship('Quest')

    def __repr__(self):
        return f'<CharacterQuest character_id={self.character_id} quest_id={self.quest_id}>'
