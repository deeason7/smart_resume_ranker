#app/shared_services.py
"""
This module initializes and provides shared, singleton instances of the application's core services.
"""
from app.services.nlp_service import NLPService
from app.services.ranking_service import RankingService

#Create single, shared instances of the services for the entire app
nlp_service = NLPService()
ranking_service = RankingService()

