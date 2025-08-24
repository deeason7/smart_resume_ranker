# app/routes/candidate_routes.py
# This file handles all pages and logic specific to the 'candidate' role
import os
from flask import (Blueprint, render_template, session, redirect,
                   url_for, flash, request, current_app)
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from app.models import Job, Resume, Application
from app.services.shared_services import nlp_service, ranking_service
from app.utils.nlp_utils import extract_text_from_file
from app.helpers import login_required
from app.extensions import db

candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')

@candidate_bp.route('/jobs')
@login_required()
def job_list():
    """
    Displays all available job postings, with an optional search filter.
    The search is case-insensitive and checks both the job title and description.
    """
    # Get the search term from the Url query parameters (e.g./ jobs?search = analyst)
    search_term  = request.args.get('search', '').strip()

    # Start with a base query for all jobs
    query = Job.query

    # If a search term is provided, add a filter to the query
    if search_term:
        # Create a case-insensitive search pattern
        search_pattern = f"%{search_term}%"
        # Filter jobs where the title OR the description contains the search term
        query = query.filter(
            or_(
                Job.title.ilike(search_pattern),
                Job.description.ilike(search_pattern)
            )
        )

    # Execute the final query, ordering by the most recent jobs
    jobs = query.order_by(Job.date_created.desc()).all()

    # Pass the search term back to the template to display it in the search box
    return render_template('job_list.html', jobs=jobs, search_term=search_term)


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

@candidate_bp.route('/job/<job_id>')
@login_required() # Any logged-in user can view the job details
def job_detail(job_id):
    """Displays the full details for a single job posting."""
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)