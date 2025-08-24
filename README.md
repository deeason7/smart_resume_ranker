# Smart Resume Ranker

An intelligent, end-to-end web application built with Flask and Python. The system uses a sophisticated, multi-stage NLP pipeline and a self-improving machine learning model to analyze, score, and rank candidate resumes against job descriptions, providing recruiters with instant, data-driven insights.



---
## Key Features

-   **Role-Based User System**: Secure, distinct workflows for **Recruiters** and **Candidates**.

-   **Intelligent NLP Pipeline**: A multi-stage pipeline using **spaCy** that performs deep analysis on documents to extract:
    -   **Structured Data**: Years of experience, education level, and key skills.
    -   **Stylistic Analysis**: Calculates text readability using the Flesch reading ease score.
    -   **Behavioral Analysis**: Generates an "accomplishment score" by identifying and counting unique action verbs (e.g., *managed*, *developed*, *launched*).

-   **Hybrid Ranking Model**: Ranks candidates using a powerful hybrid model that considers:
    -   **Semantic Similarity**: Deep learning-based understanding of the context via **Sentence-Transformers**.
    -   **Structured Feature Matching**: A precise score based on the overlap of extracted data points, including the new stylistic and behavioral metrics.

-   **Self-Improving AI Loop**:
    -   Recruiter feedback (`Accepted` / `Declined` statuses) is collected as labeled training data.
    -   A standalone training script (`train_model.py`) uses this data to train an advanced **XGBoost** model with automated hyperparameter tuning.
    -   The application automatically loads and uses the newest, smartest model for all future rankings.

-   **Data-Rich Recruiter Dashboard (XAI)**:
    -   View job postings with at-a-glance applicant counts.
    -   See a ranked list of all candidates for a job, with scores color-coded for clarity.
    -   Visualize applicant score distributions with an interactive **Chart.js** bar graph.
    -   Review a detailed, AI-generated "Candidate Profile" for each applicant, with helpful tooltips explaining the advanced metrics to build user trust (Explainable AI).
    -   Matching skills between the resume and job description are automatically highlighted.

-   **Immediate Candidate Feedback**: Candidates see their initial match score immediately after applying and can track the status of all their applications.

---
## Tech Stack & Architecture

-   **Backend**: Flask, Flask-SQLAlchemy, Werkzeug
-   **Database**: SQLite
-   **Machine Learning**:
    -   **Core NLP**: spaCy, textstat
    -   **Embeddings**: sentence-transformers, PyTorch
    -   **Modeling**: XGBoost, scikit-learn, pandas
-   **Frontend**: Jinja2, HTML, Bootstrap 5, Chart.js
-   **Architecture**:
    -   **Flask Application Factory Pattern** for a modular structure.
    -   **Blueprint-based Routing** organized by function.
    -   **Singleton Service Architecture** (`shared_services.py`) to ensure resource-intensive models are loaded only once.
    -   **Decoupled Model Training** via a standalone Python script.

---
## Local Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository
```bash
git clone [https://github.com/deeason7/smart_resume_ranker](https://github.com/deeason7/smart_resume_ranker)
cd smart_resume_ranker
