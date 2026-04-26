from app.database.base import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

class Experience(db.Model):
    __tablename__ = "experiences"

    id           = db.Column(db.Integer, primary_key=True)
    graduate_id  = db.Column(db.Integer, db.ForeignKey("graduates.id"))
    company      = db.Column(db.String(200))
    position     = db.Column(db.String(200))
    description  = db.Column(db.Text)
    start_date   = db.Column(db.Date)
    end_date     = db.Column(db.Date)          # NULL = по сей день
    is_internship = db.Column(db.Boolean, default=False)