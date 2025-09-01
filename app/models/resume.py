# app/models/resume.py
from datetime import datetime, timezone
from app.extensions import  db
import uuid

class Resume(db.Model):
    """
    Represents a resume documents uploaded by a candidate.
    """

    __tablename__ = 'resume'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    original_filename = db.Column(db.String(255), nullable=False)

    extracted_text = db.Column(db.Text, nullable=True)
    date_uploaded = db.Column(db.DateTime, default= datetime.now(timezone.utc))

    sectioned_text = db.Column(db.JSON, nullable=True)

    #Foreign Key to link to the User (candidate) who owns the resume
    candidate_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)

    # Links ID to the recruiter who uploaded the resume to their talent pool.
    uploader_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)

    #Store the name and email found by the NLP service.
    extracted_name = db.Column(db.String(255), nullable=True)
    extracted_email = db.Column(db.String(255), nullable=True)

    # Distinguish between resumes from application vs the talent pool.
    source = db.Column(db.String(50), nullable=False, default='application')

    # Many-to-one relationship with User
    candidate = db.relationship('User', foreign_keys=[candidate_id], back_populates='resumes')

    uploader = db.relationship('User', foreign_keys=[uploader_id])

    def __repr__(self)->str:
        """String representation of the Resume object."""
        if self.candidate:
            return f"<Resume id='{self.id}' filename='{self.original_filename}' user='{self.candidate.username}'>"
        return f"<Resume id='{self.id}' filename='{self.original_filename}'>"