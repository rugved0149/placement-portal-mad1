from flask import Flask, render_template, redirect, url_for, request, flash
from config import Config
from extensions import db, login_manager
from models import User, Student, Company, PlacementDrive, Application
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)

# DATABASE + ADMIN CREATION
with app.app_context():
    if not os.path.exists("instance"):
        os.makedirs("instance")

    db.create_all()

    # Create default admin if not exists
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        admin_user = User(
            username="admin",
            email="admin@placement.com",
            password_hash=generate_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin created.")

# USER LOADER
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ROUTES
@app.route("/")
def home():
    return redirect(url_for("login"))

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):

            if not user.is_active:
                flash("Account is deactivated or blacklisted.")
                return redirect(url_for("login"))

            login_user(user)

            # Role-based redirect
            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))

            elif user.role == "company":
                company = Company.query.filter_by(user_id=user.id).first()

                if not company or company.approval_status != "Approved":
                    flash("Company not approved by admin yet.")
                    logout_user()
                    return redirect(url_for("login"))

                return redirect(url_for("company_dashboard"))

            elif user.role == "student":
                return redirect(url_for("student_dashboard"))

        flash("Invalid credentials")

    return render_template("login.html")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form.get("role")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if role not in ["student", "company"]:
            flash("Invalid role selected.")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=role,
            is_active=True
        )

        db.session.add(new_user)
        db.session.commit()

        # Create profile
        if role == "student":
            student = Student(
                user_id=new_user.id,
                full_name="",
                contact="",
                department="",
                cgpa=0.0
            )
            db.session.add(student)

        elif role == "company":
            company = Company(
                user_id=new_user.id,
                company_name=username,
                hr_contact="",
                website="",
                approval_status="Pending"
            )
            db.session.add(company)

        db.session.commit()

        flash("Registration successful. Await approval if company.")
        return redirect(url_for("login"))

    return render_template("register.html")

# LOGOUT
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ADMIN ROUTES
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    # Blacklist enforcement
    if not current_user.is_active:
        logout_user()
        return redirect(url_for("login"))

    # Role enforcement
    if current_user.role != "admin":
        return "Unauthorized", 403

    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()

    return render_template(
        "admin/dashboard.html",
        total_students=total_students,
        total_companies=total_companies,
        total_drives=total_drives,
        total_applications=total_applications
    )


@app.route("/admin/students")
@login_required
def admin_students():
    if current_user.role != "admin":
        return "Unauthorized", 403

    students = Student.query.all()
    return render_template("admin/students.html", students=students)

@app.route("/admin/search_students", methods=["GET", "POST"])
@login_required
def search_students():
    if current_user.role != "admin":
        return "Unauthorized", 403

    query = request.form.get("query", "")

    students = Student.query.filter(
        Student.full_name.contains(query)
    ).all()

    return render_template("admin/students.html", students=students)

@app.route("/admin/companies")
@login_required
def admin_companies():
    if current_user.role != "admin":
        return "Unauthorized", 403

    companies = Company.query.all()
    return render_template("admin/companies.html", companies=companies)

@app.route("/admin/search_companies", methods=["GET", "POST"])
@login_required
def search_companies():
    if current_user.role != "admin":
        return "Unauthorized", 403

    query = request.form.get("query", "")

    companies = Company.query.filter(
        Company.company_name.contains(query)
    ).all()

    return render_template("admin/companies.html", companies=companies)

@app.route("/admin/drives")
@login_required
def admin_drives():
    if current_user.role != "admin":
        return "Unauthorized", 403

    drives = PlacementDrive.query.all()
    return render_template("admin/drives.html", drives=drives)

@app.route("/admin/approve_drive/<int:drive_id>")
@login_required
def approve_drive(drive_id):
    if current_user.role != "admin":
        return "Unauthorized", 403

    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "Approved"
    db.session.commit()

    flash("Drive approved.")
    return redirect(url_for("admin_drives"))

@app.route("/admin/reject_drive/<int:drive_id>")
@login_required
def reject_drive(drive_id):
    if current_user.role != "admin":
        return "Unauthorized", 403

    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "Rejected"
    db.session.commit()

    flash("Drive rejected.")
    return redirect(url_for("admin_drives"))

@app.route("/admin/approve_company/<int:company_id>")
@login_required
def approve_company(company_id):
    if current_user.role != "admin":
        return "Unauthorized", 403

    company = Company.query.get_or_404(company_id)
    company.approval_status = "Approved"
    db.session.commit()

    flash("Company approved successfully.")
    return redirect(url_for("admin_companies"))

@app.route("/admin/reject_company/<int:company_id>")
@login_required
def reject_company(company_id):
    if current_user.role != "admin":
        return "Unauthorized", 403

    company = Company.query.get_or_404(company_id)
    company.approval_status = "Rejected"
    db.session.commit()

    flash("Company rejected.")
    return redirect(url_for("admin_companies"))

@app.route("/admin/toggle_user/<int:user_id>")
@login_required
def toggle_user(user_id):
    if current_user.role != "admin":
        return "Unauthorized", 403

    user = User.query.get_or_404(user_id)

    if user.role != "admin":
        user.is_active = not user.is_active
        db.session.commit()

    return redirect(request.referrer)

@app.route("/admin/applications")
@login_required
def admin_applications():
    if current_user.role != "admin":
        return "Unauthorized", 403

    applications = Application.query.all()
    return render_template("admin/applications.html", applications=applications)

# COMPANY ROUTES
@app.route("/company/dashboard")
@login_required
def company_dashboard():

    if not current_user.is_active:
        logout_user()
        return redirect(url_for("login"))


    if current_user.role != "company":
        return "Unauthorized", 403

    company = Company.query.filter_by(user_id=current_user.id).first()
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()

    return render_template(
        "company/dashboard.html",
        company=company,
        drives=drives
    )

@app.route("/company/create_drive", methods=["GET", "POST"])
@login_required
def create_drive():
    if company.approval_status != "Approved":
        return "Unauthorized", 403

    if not current_user.is_active:
        logout_user()
        return redirect(url_for("login"))

    if current_user.role != "company":
        return "Unauthorized", 403

    company = Company.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        new_drive = PlacementDrive(
            company_id=company.id,
            job_title=request.form.get("job_title"),
            job_description=request.form.get("job_description"),
            eligibility=request.form.get("eligibility"),
            salary=request.form.get("salary"),
            location=request.form.get("location"),
            deadline=datetime.strptime(
                request.form.get("deadline"),
                "%Y-%m-%d"
            ).date(),
            status="Pending"
        )

        db.session.add(new_drive)
        db.session.commit()

        flash("Drive created. Await admin approval.")
        return redirect(url_for("company_dashboard"))

    return render_template("company/create_drive.html")


@app.route("/company/close_drive/<int:drive_id>")
@login_required
def close_drive(drive_id):
    if current_user.role != "company":
        return "Unauthorized", 403

    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "Closed"
    db.session.commit()

    flash("Drive closed successfully.")
    return redirect(url_for("company_dashboard"))

@app.route("/company/applications/<int:drive_id>")
@login_required
def company_applications(drive_id):
    if current_user.role != "company":
        return "Unauthorized", 403

    company = Company.query.filter_by(user_id=current_user.id).first()
    drive = PlacementDrive.query.get_or_404(drive_id)

    # Ensure drive belongs to this company
    if drive.company_id != company.id:
        return "Unauthorized", 403

    applications = Application.query.filter_by(drive_id=drive.id).all()

    return render_template(
        "company/applications.html",
        drive=drive,
        applications=applications
    )

@app.route("/company/profile", methods=["GET", "POST"])
@login_required
def company_profile():
    if not current_user.is_active:
        logout_user()
        return redirect(url_for("login"))

    if current_user.role != "company":
        return "Unauthorized", 403

    company = Company.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        company.company_name = request.form.get("company_name")
        company.hr_contact = request.form.get("hr_contact")
        company.website = request.form.get("website")

        db.session.commit()
        flash("Company profile updated successfully.")
        return redirect(url_for("company_dashboard"))

    return render_template("company/profile.html", company=company)

@app.route("/company/update_application/<int:application_id>", methods=["POST"])
@login_required
def update_application(application_id):
    if not current_user.is_active:
        logout_user()
        return redirect(url_for("login"))

    if current_user.role != "company":
        return "Unauthorized", 403

    application = Application.query.get_or_404(application_id)

    drive = PlacementDrive.query.get(application.drive_id)
    company = Company.query.filter_by(user_id=current_user.id).first()

    # Ensure drive belongs to this company
    if drive.company_id != company.id:
        return "Unauthorized", 403

    new_status = request.form.get("status")

    if new_status in ["Shortlisted", "Selected", "Rejected"]:
        application.status = new_status
        db.session.commit()
        flash("Application updated.")

    return redirect(url_for("company_applications", drive_id=drive.id))

# STUDENT ROUTES (Placeholder)
@app.route("/student/apply/<int:drive_id>")
@login_required
def apply_drive(drive_id):
    if current_user.role != "student":
        return "Unauthorized", 403

    student = Student.query.filter_by(user_id=current_user.id).first()
    drive = PlacementDrive.query.get_or_404(drive_id)

    from datetime import datetime

    # Rule 1: Must be approved
    if drive.status != "Approved":
        flash("Drive not available.")
        return redirect(url_for("student_dashboard"))

    # Rule 2: Deadline check
    if drive.deadline < datetime.today().date():
        flash("Deadline passed.")
        return redirect(url_for("student_dashboard"))

    # Rule 3: Prevent duplicate
    existing = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive.id
    ).first()

    if existing:
        flash("Already applied.")
        return redirect(url_for("student_dashboard"))

    # Create application
    new_application = Application(
        student_id=student.id,
        drive_id=drive.id,
        status="Applied"
    )

    db.session.add(new_application)
    db.session.commit()

    flash("Applied successfully.")
    return redirect(url_for("student_dashboard"))

@app.route("/student/dashboard")
@login_required
def student_dashboard():
    if not current_user.is_active:
        
        logout_user()
        return redirect(url_for("login"))

    if current_user.role != "student":
        return "Unauthorized", 403

    student = Student.query.filter_by(user_id=current_user.id).first()

    approved_drives = (
        PlacementDrive.query
        .join(PlacementDrive.company)
        .join(Company.user)
        .filter(
            PlacementDrive.status == "Approved",
            User.is_active == True
        )
        .all()
    )

    applications = Application.query.filter_by(student_id=student.id).all()

    return render_template(
        "student/dashboard.html",
        student=student,
        approved_drives=approved_drives,
        applications=applications
    )

@app.route("/student/profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if current_user.role != "student":
        return "Unauthorized", 403

    student = Student.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        student.full_name = request.form.get("full_name")
        student.contact = request.form.get("contact")
        student.department = request.form.get("department")
        student.cgpa = float(request.form.get("cgpa"))

        # Handle resume upload
        file = request.files.get("resume")
        if file and file.filename != "":
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            student.resume_path = file.filename

        db.session.commit()
        flash("Profile updated successfully.")
        return redirect(url_for("student_dashboard"))

    return render_template("student/profile.html", student=student)
# RUN
if __name__ == "__main__":
    app.run(debug=True)