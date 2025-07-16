import os

class Config:
    SECRET_KEY = 'hafez-fal-secret-key'
    DATABASE_PATH = 'database/hafez.db'
    UPLOAD_FOLDER = 'static/audio'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # AI API settings
    GROQ_API_KEY = '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'
    AI_TIMEOUT = 25
    AI_MAX_TOKENS = 300
    AI_TEMPERATURE = 0.7
