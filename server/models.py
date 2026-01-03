# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# database object
db = SQLAlchemy()

# bcrypt for password hashing
bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # username + password hash
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    # relationship: one user can have many notes
    notes = db.relationship("Note", backref="user", cascade="all, delete-orphan")

    def set_password(self, password):
        """
        Hash the plain password and store it.
         NEVER store the real password in the database.
        """
        hashed = bcrypt.generate_password_hash(password.encode("utf-8"))
        self.password_hash = hashed.decode("utf-8")

    def check_password(self, password):
        """Check if the given password matches the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password.encode("utf-8"))


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)

    # lab requirement: at least 2 fields besides id
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)

    # foreign key: note belongs to a user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
