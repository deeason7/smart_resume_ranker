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
    Ranks candidates using a hybrid approach of semantic similarity and ML
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the RankingService, loading the SentenceTransformer model.
        """
        self.sbert_model = SentenceTransformer(model_name)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.sbert_model.to(self.device)
        self.ranking_model = None
        self.model_loaded = False

    def _load_latest_model(self):
        """
        Finds and loads the most recently saved ML model.
        """
        self.model_loaded = True
        model_dir = os.path.join(current_app.instance_path, 'ml_models')
        if not os.path.exists(model_dir):
            print("INFO: ML model directory does not exist. Skipping model load.")
            return

        list_of_models = glob.glob(os.path.join(model_dir, "ranking_model_*.pkl"))
        if not list_of_models:
            print("INFO: No trained models found. Using heuristic scoring.")
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
            "skills_similarity": 0.2,
            "accomplishment_score": 0.1,
        }
        # accomplishment_score is weighted and added. Normalize it by a factor of 10
        score = (features.get("accomplishment_score", 0) / 10) * weights["accomplishment_score"]

        # Add similarity score
        score += sum(features.get(key, 0) * weight for key, weight in weights.items() if 'similarity' in key)

        return min(round(score, 4), 1.0) # Ensure score does not exceed 1.0

    def _get_section_similarity(self, text1: str, text2: str) -> float:
        """Calculates semantic cosine similarity between two texts."""
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
            "accomplishment_score": resume_sections.get("accomplishment_score", 0),
            "readability_score": resume_sections.get("readability_score", 0),
        }
        return feature_vector

    def predict_score(self, features: dict) -> float:
        """
        Predicts a final match score for a candidate.
        """
        if not self.model_loaded:
            self._load_latest_model()

        if self.ranking_model:
            feature_df = pd.DataFrame([features])
            probability = self.ranking_model.predict_proba(feature_df)[:, 1]
            return round(float(probability[0]), 4)
        else:
            return self._get_heuristic_score(features)