# app/models/user.py
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class User(db.Model):
    """
    Represents a user of the applications.
    """
    __tablename__ = 'user'

    id  = db.Column(db.String(36), primary_key=True, default=lambda :str(uuid.uuid4()))
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='candidate') # 'candidate' or 'recruiter'


    # One-to-many link where one User (recruiter) can have many Jobs.
    jobs = db.relationship('Job', back_populates='uploader', lazy=True, cascade="all, delete-orphan")

    #One-to-many' link where one User (candidate) can have many Resumes.
    resumes = db.relationship('Resume', back_populates='candidate', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str):
        """Hashes and sets the user's passwords"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        """String Representation of the User object"""
        return f"<User id='{self.id}' username='{self.username}' role='{self.role}'>"