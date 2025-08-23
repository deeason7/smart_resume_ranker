# app/models/job.py
from datetime import datetime, timezone
from app.extensions import db
import uuid

class Job(db.Model):
    """
    Represents a job posting created by a recruiter.
    """
    __tablename__ = 'job'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    processed_description = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # JSON column to store the sectioned document
    sectioned_text = db.Column(db.JSON, nullable=True)

    # Foreign Key to link to the User who uploaded the job
    uploader_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

    # Many-to-one relationships with User
    uploader = db.relationship('User', back_populates='jobs')

    # One-to-many relationship with Application
    applications = db.relationship('Application', back_populates='job', lazy=True, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Job id = '{self.id}' title= '{self.title}'>"