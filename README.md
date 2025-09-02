# Flask Web Portal - Setup Instructions

## Installation Steps

1. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Database and Create Admin:**
   ```bash
   python
   >>> from app import app, db, User
   >>> with app.app_context():
   ...     db.create_all()
   ...     admin = User(username='admin', role='admin')
   ...     admin.set_password('admin123')  # Change this password!
   ...     db.session.add(admin)
   ...     db.session.commit()
   ...     print("Admin created successfully!")
   >>> exit()
   ```

4. **Run the Application:**
   ```bash
   python app.py
   ```

5. **Access the Application:**
   - Open browser and go to: http://localhost:5000
   - Student Registration: http://localhost:5000/register
   - Student Login: http://localhost:5000/login
   - Admin Login: http://localhost:5000/admin/login (username: admin, password: admin123)

## File Structure

```
flask_portal/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── models.py                 # Database models
├── forms.py                  # WTF Forms
├── requirements.txt          # Python dependencies
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── index.html           # Home page
│   ├── student_register.html # Student registration
│   ├── student_login.html    # Student login
│   ├── student_dashboard.html # Student dashboard
│   ├── assessment.html       # Assessment page
│   ├── result.html          # Results page
│   ├── admin_login.html     # Admin login
│   ├── admin_dashboard.html  # Admin dashboard
│   └── question_form.html    # Question add/edit form
└── static/
    └── style.css            # Custom CSS styles
```

## Features

### For Students:
- Registration with unique username
- One-time login and assessment
- Random 10 questions from question bank
- Pass/fail based on 6/10 threshold
- View results and eligibility status

### For Admins:
- Separate admin login
- Add/Edit/Delete questions
- View all student results
- Monitor assessment statistics
- CRUD operations on question bank

## Security Features:
- Password hashing using Werkzeug
- CSRF protection with Flask-WTF
- Session management with Flask-Login
- Role-based access control
- Input validation and sanitization

## Database Schema:
- **Users table:** id, username, password_hash, role, passed, marks, attempted, created_at
- **Questions table:** id, text, option_a, option_b, option_c, option_d, correct_answer, created_at

## Default Admin Credentials:
- Username: admin
- Password: admin123
- **IMPORTANT:** Change the admin password after first login!

## Customization:
- Modify pass threshold in app.py (currently 6/10)
- Change number of assessment questions (currently 10)
- Update styling in static/style.css
- Add more question types or features as needed