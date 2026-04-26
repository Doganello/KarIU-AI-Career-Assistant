from app.database.base import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

class Certificate(db.Model):
    __tablename__ = "certificates"

    id          = db.Column(db.Integer, primary_key=True)
    graduate_id = db.Column(db.Integer, db.ForeignKey("graduates.id"))
    title       = db.Column(db.String(200))
    issuer      = db.Column(db.String(200))
    issued_date = db.Column(db.Date)
    url         = db.Column(db.String(300))