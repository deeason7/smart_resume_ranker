# app/models/application.py
from datetime import datetime, timezone
from app.extensions import db
import uuid

class Application(db.Model):
    """
    Represents the link between a candidate, a job, and a specific resume.
    """
    __tablename__ = 'application'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date_applied = db.Column(db.DateTime, default= datetime.now(timezone.utc))

    # Foreign keys
    job_id = db.Column(db.String(36), db.ForeignKey('job.id'), nullable=False)
    candidate_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    resume_id = db.Column(db.String(36), db.ForeignKey('resume.id'), nullable=False)

    status = db.Column(db.String(50), nullable=False, default='Submitted')

    feature_scores = db.Column(db.JSON, nullable=True)

    # This will hold the final score from our ML model later
    final_score = db.Column(db.Float, nullable=True)

    # Relationships
    job = db.relationship('Job', back_populates='applications')
    candidate = db.relationship('User')
    resume = db.relationship('Resume')

    def __init__(self, job_id, candidate_id, resume_id, feature_scores=None, final_score=None, **kwargs):
        """
        Custom constructor for creating Application instances.
        """
        super().__init__(**kwargs)
        self.id = str(uuid.uuid4())
        self.job_id = job_id
        self.candidate_id = candidate_id
        self.resume_id = resume_id
        self.feature_scores = feature_scores
        self.final_score = final_score

    def __repr__(self) -> str:
        """String representation of the Application object."""
        return f"<Application id='{self.id}' job_id='{self.job_id}' candidate_id='{self.candidate_id}'>"