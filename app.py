from flask import Flask, render_template, redirect, url_for, flash, request, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Question
from forms import RegistrationForm, LoginForm, QuestionForm, AssessmentForm
import random
from wtforms import RadioField
from wtforms.validators import DataRequired
from flask_migrate import Migrate
import uuid


app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'student_login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Student Registration
@app.route('/register', methods=['GET', 'POST'])
def student_register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            full_name=form.full_name.data,
            fathers_name=form.fathers_name.data,
            address=form.address.data,
            student_class=form.student_class.data,
            contact_number=form.contact_number.data,
            role='student'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('student_login'))
    return render_template('student_register.html', form=form)

# Student Login
@app.route('/login', methods=['GET', 'POST'])
def student_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, role='student').first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('student_dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('student_login.html', form=form)

# Student Dashboard
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return redirect(url_for('admin_dashboard'))
    return render_template('student_dashboard.html')

# Assessment
@app.route('/assessment', methods=['GET', 'POST'])
@login_required
def assessment():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if current_user.attempted:
        flash('You have already taken the assessment.', 'info')
        return redirect(url_for('result'))
    
    # Get all questions and select 10 random ones
    all_questions = Question.query.all()
    if len(all_questions) < 10:
        flash('Not enough questions available. Contact admin.', 'danger')
        return redirect(url_for('student_dashboard'))
    
    selected_questions = random.sample(all_questions, 10)
    
    # Create dynamic form
    class DynamicAssessmentForm(AssessmentForm):
        pass
    
    for i, question in enumerate(selected_questions):
        choices = [
            ('A', question.option_a),
            ('B', question.option_b),
            ('C', question.option_c),
            ('D', question.option_d)
        ]
        setattr(DynamicAssessmentForm, f'question_{question.id}', 
                RadioField(question.text, choices=choices, validators=[DataRequired()]))
    
    form = DynamicAssessmentForm()
    
    if form.validate_on_submit():
        score = 0
        for question in selected_questions:
            selected_answer = getattr(form, f'question_{question.id}').data
            if selected_answer == question.correct_answer:
                score += 1
        
        # Update user record
        current_user.marks = score
        current_user.passed = score >= 7  # Pass mark is 7/10
        current_user.attempted = True
        if current_user.passed and not current_user.result_id:
            current_user.result_id = str(uuid.uuid4())
        db.session.commit()
        
        return redirect(url_for('result'))
    
    return render_template('assessment.html', form=form, questions=selected_questions)

# Result page
@app.route('/result')
@login_required
def result():
    if current_user.role != 'student':
        return redirect(url_for('admin_dashboard'))
    
    if not current_user.attempted:
        flash('You need to take the assessment first.', 'warning')
        return redirect(url_for('assessment'))
    
    return render_template('result.html')


@app.route('/result/download')
@login_required
def download_result():
    if current_user.role != 'student' or not current_user.passed:
        flash("You are not eligible to download the result.", "danger")
        return redirect(url_for('student_dashboard'))
    
    result_text = f"""
    Result ID: {current_user.result_id}
    Name: {current_user.full_name}
    Marks: {current_user.marks}/10
    Status: Passed
    
    Congratulations on passing the Urdu class assessment!
    """
    response = make_response(result_text)
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = 'attachment; filename=result_{current_user.result_id}.txt'
    return response



# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = User.query.filter_by(username=form.username.data, role='admin').first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials.', 'danger')
    return render_template('admin_login.html', form=form)

# Admin Dashboard
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('student_login'))
    
    students = User.query.filter_by(role='student').all()
    questions = Question.query.all()
    
    # Statistics
    total_students = len(students)
    attempted_students = len([s for s in students if s.attempted])
    passed_students = len([s for s in students if s.passed])
    
    stats = {
        'total_students': total_students,
        'attempted_students': attempted_students,
        'passed_students': passed_students,
        'total_questions': len(questions)
    }
    
    return render_template('admin_dashboard.html', 
                         students=students, 
                         questions=questions, 
                         stats=stats)

# Add Question
@app.route('/admin/question/add', methods=['GET', 'POST'])
@login_required
def add_question():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('student_login'))
    
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(
            text=form.text.data,
            option_a=form.option_a.data,
            option_b=form.option_b.data,
            option_c=form.option_c.data,
            option_d=form.option_d.data,
            correct_answer=form.correct_answer.data
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('question_form.html', form=form, title='Add Question')

# Edit Question
@app.route('/admin/question/edit/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('student_login'))
    
    question = Question.query.get_or_404(question_id)
    form = QuestionForm(obj=question)
    
    if form.validate_on_submit():
        question.text = form.text.data
        question.option_a = form.option_a.data
        question.option_b = form.option_b.data
        question.option_c = form.option_c.data
        question.option_d = form.option_d.data
        question.correct_answer = form.correct_answer.data
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('question_form.html', form=form, title='Edit Question')

# Delete Question
@app.route('/admin/question/delete/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('student_login'))
    
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)