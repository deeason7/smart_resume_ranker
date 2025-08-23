# app/services/ranking_service.py
import os
import glob
import joblib
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util
from flask import current_app
from app.models import Job, Resume


class RankingService:
    """
    A sophisticated service that ranks candidates using a hybrid approach.
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the RankingService.

        Loads the heavyweight SentenceTransformer model immediately, as it does
        not depend on the app context. The trainable ranking model is "lazy-loaded"
        to prevent errors during worker startup.
        """
        self.sbert_model = SentenceTransformer(model_name)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.sbert_model.to(self.device)

        self.ranking_model = None
        self.model_loaded = False  # Flag to ensure we only load the model once per worker.

    def _load_latest_model(self):
        """
        Finds the most recently saved ML model from the instance folder and loads it.
        """
        self.model_loaded = True
        model_dir = os.path.join(current_app.instance_path, 'ml_models')
        if not os.path.exists(model_dir):
            print("INFO: ML model directory does not exist. Skipping model load.")
            return

        list_of_models = glob.glob(os.path.join(model_dir, "ranking_model_*.pkl"))
        if not list_of_models:
            print("INFO: No trained models found. Will use heuristic scoring.")
            return

        latest_model_path = max(list_of_models, key=os.path.getctime)
        try:
            self.ranking_model = joblib.load(latest_model_path)
            print(f"Successfully loaded trained ranking model: {os.path.basename(latest_model_path)}")
        except Exception as e:
            print(f"ERROR: Could not load model file {latest_model_path}: {e}")

    @staticmethod
    def _get_heuristic_score(features: dict) -> float:
        """
        Calculates a fallback score based on a weighted formula. This is used
        when no ML model has been trained yet (the "bootstrapped" model).
        """
        weights = {
            "overall_similarity": 0.4,
            "experience_similarity": 0.3,
            "skills_similarity": 0.3,
        }
        score = sum(features.get(key, 0) * weight for key, weight in weights.items())
        return round(score, 4)

    def _get_section_similarity(self, text1: str, text2: str) -> float:
        """A helper method to calculate the semantic cosine similarity between two texts."""
        if not text1 or not text2:
            return 0.0

        embedding1 = self.sbert_model.encode(text1, convert_to_tensor=True, device=self.device)
        embedding2 = self.sbert_model.encode(text2, convert_to_tensor=True, device=self.device)
        cosine_score = util.cos_sim(embedding1, embedding2)

        return round(float(cosine_score[0][0]), 4)

    def generate_feature_vector(self, job: Job, resume: Resume) -> dict:
        """
        Generates the multi-faceted feature vector for a given job-resume pair
        by comparing their semantic sections.
        """
        job_sections = job.sectioned_text or {}
        resume_sections = resume.sectioned_text or {}

        # Get the text from the most relevant sections, defaulting to empty strings
        job_experience_text = job_sections.get("RESPONSIBILITIES", "") or job_sections.get("EXPERIENCE", "")
        resume_experience_text = resume_sections.get("EXPERIENCE", "")
        job_skills_text = job_sections.get("SKILLS", "")
        resume_skills_text = resume_sections.get("SKILLS", "")

        feature_vector = {
            "overall_similarity": self._get_section_similarity(job.description, resume.extracted_text),
            "experience_similarity": self._get_section_similarity(job_experience_text, resume_experience_text),
            "skills_similarity": self._get_section_similarity(job_skills_text, resume_skills_text),
        }
        return feature_vector

    def predict_score(self, features: dict) -> float:
        """
        Predicts the final match score for a candidate. This is the main public method.
        """
        if not self.model_loaded:
            self._load_latest_model()

        if self.ranking_model:
            # If a trained model exists, use it for prediction.
            feature_df = pd.DataFrame([features])
            probability = self.ranking_model.predict_proba(feature_df)[:, 1]
            return round(float(probability[0]), 4)
        else:
            # Otherwise, fall back to our simple heuristic score.
            return self._get_heuristic_score(features)