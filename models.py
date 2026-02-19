from datetime import datetime
from extensions import db
from flask_login import UserMixin


# ======================
# USER TABLE
# ======================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ======================
# STUDENT TABLE
# ======================

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    contact = db.Column(db.String(15))
    department = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    resume_path = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="student", uselist=False)

    applications = db.relationship(
        "Application",
        back_populates="student",
        cascade="all, delete-orphan"
    )


# ======================
# COMPANY TABLE
# ======================

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    hr_contact = db.Column(db.String(150))
    website = db.Column(db.String(200))
    location = db.Column(db.String(150))
    description = db.Column(db.Text)
    approval_status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="company", uselist=False)

    drives = db.relationship(
        "PlacementDrive",
        back_populates="company",
        cascade="all, delete-orphan"
    )


# ======================
# PLACEMENT DRIVE TABLE
# ======================

class PlacementDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text)
    eligibility = db.Column(db.Text)
    salary = db.Column(db.String(100))
    location = db.Column(db.String(100))
    deadline = db.Column(db.Date)
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship(
        "Company",
        back_populates="drives"
    )

    applications = db.relationship(
        "Application",
        back_populates="drive",
        cascade="all, delete-orphan"
    )


# ======================
# APPLICATION TABLE
# ======================

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Applied")

    student = db.relationship(
        "Student",
        back_populates="applications"
    )

    drive = db.relationship(
        "PlacementDrive",
        back_populates="applications"
    )

    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),
    )
