# Smart Resume Ranker

An intelligent, end-to-end Applicant Tracking System (ATS) built with Flask and Python. This application uses a sophisticated NLP and machine learning pipeline to automatically rank candidate resumes against job descriptions, helping recruiters identify the most qualified applicants instantly.

The system features a self-improving ranking model that learns from recruiter feedback over time, becoming more accurate with every use.

---

##  Key Features

* **Role-Based Access Control:** Separate, secure workflows for **Recruiters** and **Candidates**.
* **Synchronous Processing Pipeline:** A clean, easy-to-run architecture where all data processing and ranking happen instantly upon user action.
* **Automated Candidate Profiling (NER):** Goes beyond keywords to automatically extract structured data from resumes, including:
    * Skills
    * Years of Experience
    * Education Level
* **Hybrid Ranking Model:** Ranks candidates using a powerful hybrid model that considers:
    * **Semantic Similarity:** Deep learning-based understanding of the overall context of the resume and job description.
    * **Structured Feature Matching:** A precise score based on the overlap of extracted skills and experience.
* **Self-Improving AI:** A standalone training script that uses recruiter feedback (`Accepted`/`Declined` statuses) to retrain the ranking model, allowing the system's accuracy to improve over time.
* **Data-Rich Dashboards:**
    * **For Recruiters:** View job postings, see ranked lists of applicants, visualize score distributions with charts, and review automatically generated candidate profiles.
    * **For Candidates:** View available jobs, apply with a resume, and track the status and match score of their applications.

---

##  Tech Stack & Architecture

This project is built with a modern, professional stack and follows best practices for structure and scalability.

* **Backend:**
    * **Framework:** Flask
    * **Database ORM:** Flask-SQLAlchemy
    * **Database:** SQLite (for development), easily configurable for PostgreSQL in production.
* **Machine Learning & NLP:**
    * **Core NLP:** `spaCy` (for Named Entity Recognition and document processing).
    * **Semantic Similarity:** `sentence-transformers` (utilizing pre-trained deep learning models).
    * **Ranking Model:** `XGBoost` / `LightGBM` (trained via a standalone script).
    * **Data Handling:** `pandas`, `scikit-learn`, `joblib`.
* **Frontend:**
    * **Templating:** Jinja2
    * **Styling:** Bootstrap 5
    * **Visualization:** Chart.js
* **Architecture:**
    * **Flask Application Factory Pattern:** For a clean and scalable app structure.
    * **Blueprint-based Routing:** Routes are organized by function (`public`, `auth`, `recruiter`, `candidate`).
    * **Service-Oriented Design:** NLP and Ranking logic are encapsulated in dedicated service classes.
    * **Standalone ML Training:** Model training is decoupled into a separate script (`train_model.py`) for maintainability.

---

##  Local Setup and Installation

Follow these steps to get the application running on your local machine.

**1. Clone the Repository**
```bash
git clone [https://github.com/YourUsername/smart-resume-ranker.git](https://github.com/YourUsername/smart-resume-ranker.git)
cd smart-resume-ranker
```

**2. Create and Activate Virtual Environment**
*This isolates the project's dependencies.*
```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

**3. Install Dependencies**
*Install all required packages from the `requirements.txt` file.*
```bash
pip install -r requirements.txt
```

**4. Download NLP Model**
*Download the necessary `spaCy` language model.*
```bash
python -m spacy download en_core_web_md
```

**5. Configure Environment Variables**
*Create a `.env` file for your secret key and database URL.*
```bash
# Copy the example file
cp .env.example .env
```
*Now, open the `.env` file and change the `SECRET_KEY` to your own random string.*

---

##  How to Use the Application

#### **1. Running the Web Application**

The web server provides the user interface for recruiters and candidates.

* **Start the server:**
    ```bash
    python main.py
    ```
* **Access the app:** Open your browser and go to `http://127.0.0.1:5000`.
* **Usage:**
    * Register separate accounts for a "Recruiter" and a "Candidate".
    * As the recruiter, post new jobs.
    * As the candidate, apply for jobs by uploading a resume. The match score is calculated and displayed instantly.
    * As the recruiter, view the ranked list of applicants for each job and update their status (e.g., "Accepted" or "Declined").

#### **2. Training the Machine Learning Model**

This is a separate, manual step you perform to make the AI smarter.

* **When to run:** After recruiters have reviewed some candidates and marked them as "Accepted" or "Declined."
* **Action:** Open a **new terminal window**, navigate to the project root, activate the virtual environment, and run:
    ```bash
    python train_model.py
    ```
* **Result:** This script will use the recruiter's feedback as labeled data to train a new, more accurate ranking model and save it. The web application will automatically find and start using this new model for all future rankings.

---

##  Future Improvements

* **Production Database:** Migrate from SQLite to PostgreSQL for better scalability and concurrency.
* **Asynchronous Processing:** For very high traffic, re-introduce a task queue like Celery and Redis to handle NLP processing in the background.
* **Admin Dashboard:** Implement a `Flask-Admin` interface for superuser management of all users, jobs, and applications.
