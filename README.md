# EduCatalyst
> **A Django-Based Smart Learning & Student Innovation Platform**
> Built with Django 5.x, Tailwind CSS, Space Physics Canvas, and PostgreSQL-ready architecture.

---

## 🌟 Executive Summary
**EduCatalyst** is a modern Learning Management System (LMS) tightly coupled with an active **Innovation Hub**. Traditional e-learning platforms stop at course completion; EduCatalyst completes the **Learn → Apply → Innovate** cycle by allowing learners to formulate original project solutions, link them to studied courses, gather peer votes, and advance through faculty mentor review stages.

---

## 🎨 Theme & Styling (Tailwind CSS)
The user interface is designed using **Tailwind CSS** with a custom CSS variable design system supporting automatic **Light & Dark modes**:

```css
:root {
  --primary: #3b82f6;
  --card: #ffffff;
  --background: #ffffff;
  --foreground: #333333;
  --accent: #e0f2fe;
  --border: #e5e7eb;
  --muted: #f9fafb;
}

.dark {
  --primary: #3b82f6;
  --card: #262626;
  --background: #171717;
  --foreground: #e5e5e5;
  --accent: #1e3a8a;
  --border: #404040;
  --muted: #1f1f1f;
}
```

- **Theme Toggle:** Switch easily between light and dark modes with persistent `localStorage` preference.
- **Responsive Layout:** Optimized for mobile phones, tablets, and desktop workstations.

---

## 🚀 Key Modules & Capabilities

### 1. 👥 Role-Based Authentication (`apps.accounts`)
- Custom `User` model with 3 role tiers: **Student**, **Teacher**, and **Admin**.
- One-to-One extended profile tables: `StudentProfile` (institution, class, bio, photo) and `TeacherProfile` (department, qualification, bio).
- Security Mixins: `StudentRequiredMixin`, `TeacherRequiredMixin`, `AdminRequiredMixin`.

### 2. 📚 Course & Curriculum Management (`apps.courses`)
- Hierarchical structure: **Categories → Courses → Modules → Lessons**.
- Rich lesson delivery: text/markdown notes, external video URLs, and downloadable PDF attachments.
- Automated progress tracking (`LessonProgress`) calculating real-time percentage completion per student.
- Instructor Studio to draft, edit, and publish courses.

### 3. 📝 Assessment Engine (`apps.assessments`)
- **Quizzes:** Timed assessments with interactive countdown timers, radio button choices, and **instant automated scoring**.
- **Assignments:** Instructors set deadlines and max marks; students upload solution files; faculty grade and provide constructive feedback.

### 4. 💡 Innovation Hub (`apps.innovation`) *(Core Differentiator)*
- Students pitch original solutions to real-world problems.
- Ideas can be optionally linked to related courses.
- **Community Validation:** 1 upvote per student with live leaderboard rankings.
- **Faculty Mentorship Pipeline:** Ideas move through `Submitted` ➔ `Under Review` ➔ `Approved` ➔ `In Progress` ➔ `Completed`.
- Collaborative comment threads for peer feedback.

### 5. 💬 Discussion Forums (`apps.discussions`)
- Course-specific discussion boards where learners ask questions and teachers answer outside classroom hours.

### 6. 🔔 Event Notifications (`apps.notifications`)
- Django signals automatically trigger in-app alerts on events such as assignment grading, idea status updates, and peer comments.
- Dynamic unread badge in the navigation bar.

### 7. 📊 Interactive Dashboards (`apps.dashboard`)
- **Student Dashboard:** Track enrolled courses, completion progress bars, recent quiz scores, and submitted idea portfolios.
- **Teacher Dashboard:** Monitor learner count, pending assignment submissions to grade, and ideas awaiting mentor review.
- **Admin Dashboard:** Platform-wide metrics with **Chart.js** bar visualizations.

---

## 🛠️ Quickstart Guide

### 1. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration (`.env`)
The `.env` file at the root holds environment configurations:
```ini
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

#### Switching to PostgreSQL:
When your PostgreSQL service is running:
1. Create the database: `createdb educatalyst`
2. Update `.env`:
   ```ini
   DB_NAME=educatalyst
   DB_USER=postgres
   DB_PASSWORD=your_postgres_password
   DB_HOST=localhost
   DB_PORT=5432
   ```
3. Run `python manage.py migrate`

### 4. Run Migrations & Seed Sample Data
```bash
python manage.py migrate
python seed_data.py
```

### 5. Launch Development Server
```bash
python manage.py runserver
```
Visit **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

---

## 🔑 Pre-Configured Demo Accounts

| Role | Username | Password | Notes |
|------|----------|----------|-------|
| **Admin** | `admin` | `admin123` | Full Django Admin & System Dashboard access |
| **Teacher** | `dr_sarah` | `teacher123` | Instructor Studio, Course author, Assignment grader, Mentor |
| **Student 1** | `alex_coder` | `student123` | Enrolled in Django course, author of "Smart Vision Attendance" |
| **Student 2** | `priya_sharma` | `student123` | Enrolled in Django course, author of "AgriSense IoT" |

---

## 🧪 Running the Automated Test Suite
To run all unit and integration tests across apps:
```bash
python manage.py test apps.accounts apps.courses apps.innovation
```

---

## 📂 Project Architecture

```
CA3/
├── manage.py
├── requirements.txt
├── .env
├── seed_data.py
├── config/
│   ├── settings/
│   │   ├── base.py       # Core configuration & Tailwind theme packs
│   │   ├── dev.py        # Development environment (SQLite / Dev Postgres)
│   │   └── prod.py       # Production environment (PostgreSQL & SSL headers)
│   ├── urls.py           # Root routing
│   └── wsgi.py
├── apps/
│   ├── accounts/         # Custom User, Role models, Mixins, Auth views
│   ├── courses/          # Categories, Courses, Modules, Lessons, Progress
│   ├── assessments/      # Quizzes, Questions, Auto-grading, Assignments
│   ├── innovation/       # Innovation Hub, Ideas, Leaderboard, Mentorship
│   ├── discussions/      # Course forum threads and replies
│   ├── notifications/    # Signals & notification alerts
│   └── dashboard/        # Role-based dashboards (Student, Teacher, Admin)
├── templates/
│   ├── base.html         # Base layout with Tailwind CDN, icons, dark mode
│   ├── home.html         # Hero landing page & innovation cycle
│   ├── partials/         # Navbar, footer, alert messages
│   ├── accounts/
│   ├── courses/
│   ├── assessments/
│   ├── innovation/
│   ├── discussions/
│   ├── notifications/
│   └── dashboard/
└── static/
    ├── css/
    │   └── theme.css     # Custom blue & dark mode CSS variable palette
    └── js/
        └── main.js       # Dark mode toggling & alert dismissals
```
