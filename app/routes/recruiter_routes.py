# app/routes/recruiter_routes.py
import os
import sys
import subprocess
from flask import (Blueprint, render_template, session, redirect,
                   url_for, flash, request, current_app)
from werkzeug.utils import secure_filename

from app.models import Job, Application, Resume
from app.services.shared_services import nlp_service,ranking_service
from app.utils.nlp_utils import preprocess_text, extract_text_from_file
from app.helpers import login_required
from app.extensions import db

recruiter_bp = Blueprint('recruiter', __name__, url_prefix='/recruiter')

@recruiter_bp.route('/dashboard')
@login_required(role="recruiter")
def dashboard():
    """Displays the main dashboard for the logged-in recruiter."""
    recruiter_id = session['user_id']
    jobs = Job.query.filter_by(uploader_id=recruiter_id).order_by(Job.date_created.desc()).all()
    return render_template('dashboard.html', jobs=jobs)

@recruiter_bp.route('/post-job', methods=['GET', 'POST'])
@login_required(role="recruiter")
def post_job():
    """Handles the creation of a new job posting."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        if not title or not description:
            flash('Title and description are required.', 'danger')
            return redirect(url_for('recruiter.post_job'))

        sectioned_data = nlp_service.process_document(description)
        # Use the imported function to clean text before database entry
        processed_job_text = preprocess_text(description)

        new_job = Job(
            title=title, description=description,
            processed_description=processed_job_text,
            sectioned_text=sectioned_data, uploader_id=session['user_id']
        )
        db.session.add(new_job)
        db.session.commit()

        flash('Your new job has been posted successfully!', 'success')
        return redirect(url_for('recruiter.dashboard'))

    return render_template('post_job.html')

@recruiter_bp.route('/job/<job_id>/ranking')
@login_required(role="recruiter")
def job_ranking(job_id):
    """Displays the ranked list of candidates for a specific job."""
    job = Job.query.get_or_404(job_id)
    if job.uploader_id != session['user_id']:
        return "<h1>Forbidden</h1>", 403

    applications = Application.query.filter_by(job_id=job_id) \
        .order_by(Application.final_score.desc().nulls_last()).all()

    chart_labels = [f"# {i+1} {app.candidate.username}" for i, app in enumerate(applications)]
    chart_scores = [app.final_score or 0 for app in applications]

    # Find passive candidates
    passive_candidates = ranking_service.find_matches_in_pool(job, recruiter_id=session['user_id'])

    return render_template(
        'job_ranking.html',
        job=job,
        applications=applications,
        chart_labels=chart_labels,
        chart_scores=chart_scores,
        passive_candidates=passive_candidates
    )

@recruiter_bp.route('/application/<application_id>/update-status', methods=['POST'])
@login_required(role="recruiter")
def update_status(application_id):
    """Handles updating the status of a specific application."""
    application = Application.query.get_or_404(application_id)
    if application.job.uploader_id != session['user_id']:
        return "<h1>Forbidden</h1>", 403

    new_status = request.form.get('status')
    if new_status in ['Submitted', 'In Review', 'Accepted', 'Declined']:
        application.status = new_status
        db.session.commit()
        flash(f"Status for {application.candidate.username} updated.", 'success')
    else:
        flash("Invalid status selected.", 'danger')

    return redirect(url_for('recruiter.job_ranking', job_id=application.job_id))

@recruiter_bp.route('/retrain-model')
@login_required(role="recruiter")
def trigger_retraining():
    """Triggers the model training script as a background process."""
    python_executable = sys.executable
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    script_path = os.path.join(project_root, 'train_model.py')

    if not os.path.exists(script_path):
        flash("Training script not found!", "danger")
        return redirect(url_for('recruiter.dashboard'))

    subprocess.Popen([python_executable, script_path])
    flash("Model retraining started in the background.", 'info')
    return redirect(url_for('recruiter.dashboard'))

@recruiter_bp.route('/talent-pool', methods=['GET', 'POST'])
@login_required(role="recruiter")
def talent_pool():
    """Handles viewing and uploading resumes to the recruiter's private talent pool."""
    recruiter_id = session['user_id']

    if request.method == 'POST':
        files = request.files.getlist('resumes')
        if not files or files[0].filename == '':
            flash('No files selected for upload.', 'danger')
            return redirect(url_for('recruiter.talent_pool'))

        for file in files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.instance_path, 'uploads/resumes', filename)
            file.save(file_path)

            text = extract_text_from_file(file_path, filename)
            if not text:
                flash(f'Could not process {filename}. It may be empty or corrupted.', 'warning')
                continue

            #Process and extract all data
            processed_data = nlp_service.process_document(text)

            new_resume = Resume(
                original_filename=filename,
                extracted_text=text,
                sectioned_text=processed_data,
                extracted_name=processed_data.get('extracted_name'),
                extracted_email=processed_data.get('extracted_email'),
                source='talent_pool',
                uploader_id=recruiter_id # Associate the resume with the recruiter
            )
            db.session.add(new_resume)

        db.session.commit()
        flash(f'{len(files)} resumes successfully added to the talent pool.', 'success')
        return redirect(url_for('recruiter.talent_pool'))

    # For GET request, display all resumes in the pool
    pool_resumes = Resume.query.filter_by(
        source='talent_pool',
        uploader_id=recruiter_id  # Filter by the recruiter's ID
    ).order_by(Resume.date_uploaded.desc()).all()

    return render_template('talent_pool.html', resumes=pool_resumes)