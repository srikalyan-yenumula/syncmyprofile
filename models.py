from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    target_role = db.Column(db.String(200))
    suggestion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class ProfileAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    linkedin_name = db.Column(db.String(200), nullable=False)
    job_role = db.Column(db.String(200), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    analysis_result = db.Column(db.Text, nullable=False)
