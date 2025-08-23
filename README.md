# Smart Resume Ranker

An intelligent, end-to-end web application built with Flask and Python. The system uses a sophisticated NLP pipeline to analyze, score, and rank candidate resumes against job descriptions, providing recruiters with instant, data-driven insights.

## Key Features

-   **Role-Based User System**: Secure, distinct workflows for **Recruiters** and **Candidates**.
-   **Dynamic NLP Pipeline**: A multi-stage pipeline using **spaCy** that performs deep analysis on documents to extract:
    -   Years of Professional Experience
    -   Highest Education Level
    -   Key Skills and Proficiencies
-   **Semantic Candidate Ranking**: A sophisticated `RankingService` that uses **Sentence-Transformers** to understand the contextual similarity between resumes and job descriptions.
-   **Data-Rich Recruiter Dashboard**: Recruiters can post jobs, view applicants for each role, and see a ranked list of the most qualified candidates.
-   **Immediate Candidate Feedback**: Candidates see their initial match score immediately after applying and can track the status of all their applications.

## Tech Stack & Architecture

-   **Backend**: Flask, Flask-SQLAlchemy, Werkzeug
-   **Database**: SQLite
-   **NLP & Machine Learning**:
    -   **Core NLP**: spaCy
    -   **Embeddings**: sentence-transformers, PyTorch
    -   **ML Stack**: scikit-learn, pandas, joblib
-   **Frontend**: Jinja2, HTML, Bootstrap 5
-   **Architecture**:
    -   **Flask Application Factory Pattern** for a modular and testable structure.
    -   **Blueprint-based Routing** organized by function (public, auth, recruiter, candidate).
    -   **Service-Oriented Design** (`NLPService`, `RankingService`) to encapsulate complex logic.

---

## Local Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/deeason7/smart_resume_ranker
cd smart_resume_ranker
