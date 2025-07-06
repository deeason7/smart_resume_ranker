# app/routes/candidate_routes.py
# This file handles all pages and logic specific to the 'candidate' role
import os
from flask import (Blueprint, render_template, session, redirect,
                   url_for, flash, request, current_app)
from werkzeug.utils import secure_filename

from app.models import Job, Resume, Application
from app.services.nlp_service import NLPService
from app.services.ranking_service import RankingService
from app.utils.nlp_utils import extract_text_from_file
from app.helpers import login_required
from app.extensions import db

candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')

# Initialize services needed for these routes
nlp_service = NLPService()
ranking_service = RankingService()


@candidate_bp.route('/jobs')
@login_required()
def job_list():
    """Displays all available job postings for candidates."""
    jobs = Job.query.order_by(Job.date_created.desc()).all()
    return render_template('job_list.html', jobs=jobs)


@candidate_bp.route('/apply/<job_id>', methods=['GET', 'POST'])
@login_required(role="candidate")
def apply_for_job(job_id):
    """Handles the full application process, including resume upload and instant ranking."""
    job = Job.query.get_or_404(job_id)
    candidate_id = session['user_id']

    if Application.query.filter_by(job_id=job.id, candidate_id=candidate_id).first():
        flash('You have already applied for this job.', 'info')
        return redirect(url_for('candidate.job_list'))

    if request.method == 'POST':
        if 'resume' not in request.files or request.files['resume'].filename == '':
            flash('No resume file selected.', 'danger')
            return redirect(request.url)

        file = request.files['resume']
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.instance_path, 'uploads/resumes', filename)
        file.save(file_path)

        extracted_text = extract_text_from_file(file_path, filename)
        if not extracted_text:
            flash('Could not read the uploaded file. Please try another.', 'danger')
            return redirect(request.url)

        sectioned_resume_data = nlp_service.process_document(extracted_text)

        resume = Resume.query.filter_by(candidate_id=candidate_id).first()
        if resume:
            resume.extracted_text = extracted_text
            resume.sectioned_text = sectioned_resume_data
        else:
            resume = Resume(
                extracted_text=extracted_text, sectioned_text=sectioned_resume_data,
                candidate_id=candidate_id, original_filename=filename
            )
            db.session.add(resume)

        db.session.flush()

        feature_vector = ranking_service.generate_feature_vector(job, resume)
        final_score = ranking_service.predict_score(feature_vector)

        new_application = Application(
            job_id=job.id, candidate_id=candidate_id, resume_id=resume.id,
            feature_scores=feature_vector, final_score=final_score
        )
        db.session.add(new_application)
        db.session.commit()

        score_percent = int(final_score * 100)
        flash(f'Application submitted! Your initial match score is {score_percent}%.', 'success')
        return redirect(url_for('candidate.my_applications'))

    return render_template('apply_for_job.html', job=job)


@candidate_bp.route('/my-applications')
@login_required(role="candidate")
def my_applications():
    """Displays a list of all jobs a candidate has applied for."""
    applications = Application.query.filter_by(candidate_id=session['user_id']) \
        .order_by(Application.date_applied.desc()).all()
    return render_template('my_applications.html', applications=applications)