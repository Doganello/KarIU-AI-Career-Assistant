from app.database.base import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
from datetime import datetime

class Vacancy(db.Model):
    __tablename__ = "vacancies"

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200))
    company     = db.Column(db.String(200))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    salary_from = db.Column(db.Integer)
    salary_to   = db.Column(db.Integer)
    city        = db.Column(db.String(100))
    work_format = db.Column(db.String(50))    # remote | office | hybrid
    industry    = db.Column(db.String(100))
    source      = db.Column(db.String(50))    # kariu | enbek | hh | rabota
    source_url  = db.Column(db.String(500))
    published_at = db.Column(db.DateTime)
    parsed_at    = db.Column(db.DateTime, default=datetime.utcnow)
    is_active    = db.Column(db.Boolean, default=True)