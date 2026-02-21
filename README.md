# Placement Portal Application  
MAD-1 Project – IIT Madras BS Degree Program  

---

## 📖 Project Overview

The Placement Portal Application is a role-based web application designed to manage campus recruitment activities efficiently.

It enables structured interaction between:

- Admin (Institute Placement Cell)
- Companies
- Students

The system replaces manual spreadsheet-based placement tracking with a centralized, database-driven solution.

---

## 🎯 Objectives

- Manage company registrations and approvals
- Manage placement drive creation and approval
- Allow students to apply for approved drives
- Prevent duplicate applications
- Maintain complete placement history
- Enable admin-level monitoring and control
- Enforce role-based access control

---

## 🛠️ Tech Stack (As Per MAD-1 Requirements)

- Backend: Flask
- Frontend: Jinja2, HTML, CSS, Bootstrap
- Database: SQLite (Programmatically created)
- Authentication: Flask-Login
- ORM: Flask-SQLAlchemy

⚠️ No manual database creation used.  
⚠️ No JavaScript used for core functionality.

---

## 👥 User Roles & Functionalities

### 1️⃣ Admin (Institute Placement Cell)

- Pre-created superuser
- View dashboard statistics
- Approve / Reject company registrations
- Approve / Reject placement drives
- View all students, companies, drives, and applications
- Blacklist / Reactivate accounts
- Search students and companies
- Monitor complete placement history

---

### 2️⃣ Company

- Register and await admin approval
- Create and manage company profile
- Create placement drives (subject to approval)
- View applicants for drives
- Shortlist / Select / Reject applicants
- Close drives

---

### 3️⃣ Student

- Self-register and login
- Edit profile and upload resume
- View approved placement drives
- Apply for drives
- Track application status
- View placement history

---

## 🔒 Core System Rules Implemented

- Only approved companies can create drives
- Only approved drives are visible to students
- Duplicate applications prevented using database constraint
- Deadline validation enforced
- Blacklisted users cannot access the system
- Complete application history maintained
- Role-based route protection implemented

---

## 🗄️ Database Design

Main Tables:

- User
- Student
- Company
- PlacementDrive
- Application

Relationships:

- One User → One Student / Company
- One Company → Many Placement Drives
- One Student → Many Applications
- One Drive → Many Applications

Unique Constraint:

- Prevents multiple applications by same student for same drive

---

## ▶️ How to Run the Project Locally

### 1. Clone Repository

```bash
git clone <https://github.com/rugved0149/placement-portal-mad1>
cd placement-portal
2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4. Run Application
python app.py


Open in browser:

http://127.0.0.1:5000

Default Admin Credentials
Username: admin
Password: admin123

📊 Key Features Demonstrated

Role-based authentication

Dynamic dashboards

Approval workflow

Application lifecycle management

Resume upload

Blacklist enforcement

Clean Bootstrap UI

📹 Demo

Video demonstration link will be provided in the project report.

📄 Academic Note

This project was developed strictly according to the MAD-1 project guidelines:

SQLite only

Programmatic DB creation

Local execution

Role-based access control

Bootstrap UI

No JavaScript for core logic

👨‍💻 Author

Rugved Suryawanshi
IIT Madras BS Degree Program

---
## License

This project is licensed under the MIT License – see the LICENSE file for details.