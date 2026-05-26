from flask import Flask, render_template_string, request, redirect, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))
app.permanent_session_lifetime = timedelta(minutes=30)

# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="hema@8019",
        database="hospital1_db"
    )

# ─────────────────────────────────────────────
# SHARED BASE STYLE
# ─────────────────────────────────────────────
BASE_STYLE = """
<style>
  *{margin:0;padding:0;box-sizing:border-box;font-family:Arial;}
  body{background:#f0f4f8;}
  nav{background:#023e8a;padding:15px 30px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:999;}
  nav h1{color:white;font-size:20px;}
  nav div a{color:#90e0ef;text-decoration:none;font-size:14px;margin-left:15px;}
  nav div a:hover{color:white;}
  .container{max-width:1200px;margin:50px auto;padding:20px;}
  .center-card{display:flex;justify-content:center;align-items:center;min-height:100vh;}
  .card{background:white;padding:40px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.1);width:420px;}
  .card .logo{text-align:center;font-size:40px;margin-bottom:10px;}
  .card h2{text-align:center;color:#023e8a;margin-bottom:25px;font-size:26px;}
  label{font-size:13px;color:#555;display:block;margin-top:12px;margin-bottom:4px;}
  input{width:100%;padding:12px;border:1px solid #ccc;border-radius:6px;font-size:15px;}
  input:focus{border-color:#0077b6;outline:none;}
  .btn-primary{display:block;width:100%;padding:13px;background:#0077b6;color:white;border:none;cursor:pointer;font-size:16px;border-radius:6px;margin-top:18px;text-align:center;text-decoration:none;}
  .btn-primary:hover{background:#023e8a;}
  .links{text-align:center;margin-top:15px;font-size:13px;}
  .links a{color:#0077b6;text-decoration:none;}
  .links a:hover{text-decoration:underline;}
  .error{background:#ffe0e0;color:red;padding:10px;border-radius:5px;margin-bottom:12px;text-align:center;font-size:14px;}
  table{width:100%;border-collapse:collapse;background:white;border-radius:10px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin-bottom:30px;}
  thead{background:#023e8a;color:white;}
  th,td{padding:12px 15px;text-align:left;font-size:14px;}
  tbody tr:nth-child(even){background:#f8f9fa;}
  tbody tr:hover{background:#e8f4fd;}
  .badge{padding:4px 10px;border-radius:20px;font-size:12px;font-weight:bold;}
  .badge-pending{background:#fff3cd;color:#856404;}
  .badge-approved{background:#d1e7dd;color:#0a3622;}
  .badge-completed{background:#cfe2ff;color:#084298;}
  .badge-cancelled{background:#f8d7da;color:#842029;}
  .action-btn{padding:5px 11px;border:none;border-radius:4px;cursor:pointer;font-size:12px;font-weight:bold;text-decoration:none;margin-right:4px;display:inline-block;}
  .btn-approve{background:#28a745;color:white;}
  .btn-complete{background:#0077b6;color:white;}
  .btn-cancel{background:#dc3545;color:white;}
  .section-card{background:white;border-radius:10px;padding:25px;box-shadow:0 2px 12px rgba(0,0,0,0.08);margin-bottom:30px;}
  h2.section-title{color:#023e8a;margin-bottom:15px;font-size:22px;}
  .grid{display:flex;flex-wrap:wrap;gap:20px;justify-content:center;}
  .doctor-card{background:white;border-radius:12px;padding:25px;width:230px;text-align:center;box-shadow:0 4px 15px rgba(0,0,0,0.08);transition:transform 0.2s;}
  .doctor-card:hover{transform:translateY(-5px);}
  .avatar{width:65px;height:65px;background:#e8f4fd;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:30px;margin:0 auto 12px;}
  .doctor-card h3{color:#023e8a;font-size:16px;margin-bottom:4px;}
  .doctor-card .spec{color:#0077b6;font-size:13px;font-weight:bold;margin-bottom:8px;}
  .doctor-card .info{font-size:12px;color:#555;margin:3px 0;}
  .stat-grid{display:flex;flex-wrap:wrap;gap:20px;justify-content:center;}
  .stat-card{background:white;border-radius:12px;padding:30px;min-width:200px;text-align:center;box-shadow:0 4px 15px rgba(0,0,0,0.08);}
  .stat-card h3{color:#0077b6;margin-bottom:8px;font-size:16px;}
  .stat-card p{font-size:40px;font-weight:bold;color:#023e8a;}
  .page-title{text-align:center;color:#023e8a;font-size:30px;margin-bottom:30px;}
  footer{text-align:center;background:#001d3d;color:white;padding:15px;font-size:14px;}
  .search-bar{display:flex;gap:10px;margin-bottom:18px;}
  .search-bar input{padding:10px 14px;font-size:14px;width:280px;}
  .search-bar button,.search-bar a{padding:10px 18px;border:none;border-radius:6px;cursor:pointer;font-size:14px;text-decoration:none;}
  .search-bar button{background:#0077b6;color:white;}
  .search-bar a{background:#6c757d;color:white;}
</style>
"""

# ─────────────────────────────────────────────
# HTML TEMPLATES (all inline)
# ─────────────────────────────────────────────

INDEX_HTML = """<!DOCTYPE html><html><head><title>Hospital Management System</title>""" + BASE_STYLE + """
<style>
  html{scroll-behavior:smooth;}
  nav.top{width:100%;background:#023e8a;padding:15px 0;position:fixed;top:0;z-index:1000;display:block;}
  nav.top ul{list-style:none;display:flex;justify-content:center;flex-wrap:wrap;}
  nav.top ul li{margin:0 15px;}
  nav.top ul li a{color:white;text-decoration:none;font-size:16px;font-weight:bold;}
  nav.top ul li a:hover{color:#90e0ef;}
  #home{height:100vh;background:url('https://images.unsplash.com/photo-1586773860418-d37222d8fce3?q=80&w=2070&auto=format&fit=crop') no-repeat center center/cover;display:flex;justify-content:center;align-items:center;text-align:center;color:white;}
  .overlay{background:rgba(0,0,0,0.6);padding:50px;border-radius:10px;}
  .overlay h1{font-size:48px;margin-bottom:15px;}
  .overlay p{font-size:20px;margin-bottom:20px;}
  .hero-btn{background:#00b4d8;color:white;padding:13px 28px;text-decoration:none;border-radius:6px;font-size:17px;}
  .hero-btn:hover{background:#0077b6;}
  section.content{padding:90px 50px 60px;}
  .about-text{text-align:center;font-size:18px;line-height:1.9;color:#444;}
  .doc-grid{display:flex;gap:20px;justify-content:center;flex-wrap:wrap;}
  .doc-card{width:230px;background:white;padding:20px;border-radius:10px;box-shadow:0 0 10px lightgray;text-align:center;}
  .doc-card h3{margin-top:10px;color:#0077b6;}
  .appt-form,.auth-form{width:400px;margin:auto;background:white;padding:30px;border-radius:10px;box-shadow:0 0 10px lightgray;}
  .appt-form input,.auth-form input{width:100%;padding:12px;margin:8px 0;border:1px solid #ccc;border-radius:5px;font-size:15px;}
  .appt-form button,.auth-form button{width:100%;padding:13px;background:#0077b6;color:white;border:none;cursor:pointer;font-size:16px;border-radius:5px;margin-top:8px;}
  .appt-form button:hover,.auth-form button:hover{background:#023e8a;}
  .report-grid{display:flex;justify-content:center;gap:20px;flex-wrap:wrap;}
  .rcard{width:210px;background:white;padding:28px;text-align:center;border-radius:10px;box-shadow:0 0 10px lightgray;}
  .rcard h3{color:#0077b6;margin-bottom:8px;font-size:15px;}
  .rcard p{font-size:36px;font-weight:bold;color:#023e8a;}
  #contact{background:#023e8a;color:white;text-align:center;padding:60px 20px;}
  #contact h2{color:white;margin-bottom:15px;font-size:30px;}
  #contact p{font-size:17px;margin:6px 0;}
  .nav-hint{text-align:center;margin-top:12px;font-size:13px;}
  .nav-hint a{color:#0077b6;text-decoration:none;}
</style>
</head>
<body>
<nav class="top">
  <ul>
    <li><a href="#home">Home</a></li>
    <li><a href="#about">About</a></li>
    <li><a href="#doctors">Doctors</a></li>
    <li><a href="#appointment">Appointment</a></li>
    <li><a href="#login">Login</a></li>
    <li><a href="#register">Register</a></li>
    <li><a href="#reports">Reports</a></li>
    <li><a href="#contact">Contact</a></li>
  </ul>
</nav>

<section id="home">
  <div class="overlay">
    <h1>Hospital Management System</h1>
    <p>Your Health, Our Priority</p>
    <a href="#appointment" class="hero-btn">Book Appointment</a>
  </div>
</section>

<section id="about" class="content">
  <h2 class="page-title">About Us</h2>
  <p class="about-text">We provide quality healthcare services with expert doctors,<br>modern equipment and better patient care.</p>
</section>

<section id="doctors" class="content" style="background:#eaf4fb;">
  <h2 class="page-title">Our Doctors</h2>
  <div class="doc-grid">
    <div class="doc-card"><div style="font-size:36px;">&#128104;&#8205;&#9877;&#65039;</div><h3>Dr. John</h3><p>Cardiologist</p></div>
    <div class="doc-card"><div style="font-size:36px;">&#128105;&#8205;&#9877;&#65039;</div><h3>Dr. Priya</h3><p>Neurologist</p></div>
    <div class="doc-card"><div style="font-size:36px;">&#128104;&#8205;&#9877;&#65039;</div><h3>Dr. Arjun</h3><p>Orthopedic</p></div>
  </div>
</section>

<section id="appointment" class="content">
  <h2 class="page-title">Book Appointment</h2>
  <form class="appt-form" action="/appointment" method="POST">
    <input type="text" name="patient_name"    placeholder="Patient Name"   required>
    <input type="text" name="doctor_name"     placeholder="Doctor Name"    required>
    <input type="date" name="appointment_date"                              required>
    <button type="submit">Book Appointment</button>
  </form>
</section>

<section id="login" class="content" style="background:#eaf4fb;">
  <h2 class="page-title">Login</h2>
  <form class="auth-form" action="/login" method="POST">
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <input type="email"    name="email"    placeholder="Enter Email"    required>
    <input type="password" name="password" placeholder="Enter Password" required>
    <button type="submit">Login</button>
    <div class="nav-hint"><a href="#register">No account? Register</a></div>
  </form>
</section>

<section id="register" class="content">
  <h2 class="page-title">Register</h2>
  <form class="auth-form" action="/register" method="POST">
    <input type="text"     name="name"     placeholder="Full Name"     required>
    <input type="email"    name="email"    placeholder="Email"         required>
    <input type="text"     name="phone"    placeholder="Phone Number"  required>
    <input type="password" name="password" placeholder="Password"      required>
    <button type="submit">Register</button>
    <div class="nav-hint"><a href="#login">Have an account? Login</a></div>
  </form>
</section>

<section id="reports" class="content" style="background:#eaf4fb;">
  <h2 class="page-title">Hospital Reports</h2>
  <div class="report-grid">
    <div class="rcard"><h3>Total Patients</h3><p>{{ total_patients }}</p></div>
    <div class="rcard"><h3>Total Doctors</h3><p>{{ total_doctors }}</p></div>
    <div class="rcard"><h3>Total Appointments</h3><p>{{ total_appointments }}</p></div>
    <div class="rcard"><h3>Approved Appointments</h3><p>{{ approved_appointments }}</p></div>
  </div>
</section>

<section id="contact">
  <h2>Contact Us</h2>
  <p>Email: hospital@gmail.com</p>
  <p>Phone: +91 9876543210</p>
  <p>Location: Andhra Pradesh, India</p>
</section>

<footer><p>Hospital Management System &copy; 2026</p></footer>
</body></html>"""

LOGIN_HTML = """<!DOCTYPE html><html><head><title>Login</title>""" + BASE_STYLE + """</head>
<body>
<div class="center-card">
  <div class="card">
    <div class="logo">&#127973;</div>
    <h2>Patient Login</h2>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form action="/login" method="POST">
      <label>Email</label>
      <input type="email" name="email" placeholder="Enter email" required>
      <label>Password</label>
      <input type="password" name="password" placeholder="Enter password" required>
      <button type="submit" class="btn-primary">Login</button>
    </form>
    <div class="links">
      <p>No account? <a href="/register">Register here</a></p>
      <p style="margin-top:8px;"><a href="/">Back to Home</a></p>
    </div>
  </div>
</div>
</body></html>"""

REGISTER_HTML = """<!DOCTYPE html><html><head><title>Register</title>""" + BASE_STYLE + """</head>
<body>
<div class="center-card">
  <div class="card">
    <div class="logo">&#127973;</div>
    <h2>Patient Register</h2>
    <form action="/register" method="POST">
      <label>Full Name</label>
      <input type="text" name="name" placeholder="Enter full name" required>
      <label>Email</label>
      <input type="email" name="email" placeholder="Enter email" required>
      <label>Phone</label>
      <input type="text" name="phone" placeholder="Phone number" required>
      <label>Password</label>
      <input type="password" name="password" placeholder="Create password" required>
      <button type="submit" class="btn-primary">Register</button>
    </form>
    <div class="links">
      <p>Have an account? <a href="/login">Login here</a></p>
      <p style="margin-top:8px;"><a href="/">Back to Home</a></p>
    </div>
  </div>
</div>
</body></html>"""

DASHBOARD_HTML = """<!DOCTYPE html><html><head><title>Dashboard</title>""" + BASE_STYLE + """
<style>
  .dash-grid{display:flex;flex-wrap:wrap;gap:20px;margin-top:25px;}
  .dash-card{flex:1;min-width:200px;background:white;padding:28px;border-radius:12px;box-shadow:0 4px 15px rgba(0,0,0,0.08);text-align:center;text-decoration:none;color:inherit;transition:transform 0.2s;}
  .dash-card:hover{transform:translateY(-5px);}
  .dash-card .icon{font-size:40px;margin-bottom:10px;}
  .dash-card h3{color:#023e8a;font-size:17px;}
  .dash-card p{color:#555;font-size:13px;margin-top:5px;}
  .welcome-box{background:white;padding:28px;border-radius:12px;box-shadow:0 4px 15px rgba(0,0,0,0.08);}
  .welcome-box h2{color:#023e8a;font-size:24px;margin-bottom:6px;}
</style>
</head>
<body>
<nav>
  <h1>&#127973; Hospital Dashboard</h1>
  <div>
    <span style="color:white;font-size:14px;">&#128100; {{ user }}</span>
    <a href="/logout">Logout</a>
  </div>
</nav>
<div class="container">
  <div class="welcome-box">
    <h2>Hello, {{ user }}!</h2>
    <p style="color:#555;">Welcome to the Hospital Management System.</p>
  </div>
  <div class="dash-grid">
    <a href="/appointment" class="dash-card"><div class="icon">&#128197;</div><h3>Book Appointment</h3><p>Schedule a new appointment</p></a>
    <a href="/doctors"     class="dash-card"><div class="icon">&#128104;&#8205;&#9877;&#65039;</div><h3>View Doctors</h3><p>See available doctors</p></a>
    <a href="/reports"     class="dash-card"><div class="icon">&#128202;</div><h3>Reports</h3><p>Hospital statistics</p></a>
    <a href="/admin"       class="dash-card"><div class="icon">&#128295;</div><h3>Admin Panel</h3><p>Manage patients &amp; appointments</p></a>
  </div>
</div>
</body></html>"""

APPOINTMENT_HTML = """<!DOCTYPE html><html><head><title>Book Appointment</title>""" + BASE_STYLE + """</head>
<body>
<div class="center-card">
  <div class="card">
    <div class="logo">&#128197;</div>
    <h2>Book Appointment</h2>
    <form action="/appointment" method="POST">
      <label>Patient Name</label>
      <input type="text" name="patient_name" placeholder="Patient name" required>
      <label>Doctor Name</label>
      <input type="text" name="doctor_name" placeholder="Doctor name" required>
      <label>Date</label>
      <input type="date" name="appointment_date" required>
      <button type="submit" class="btn-primary">Book Appointment</button>
    </form>
    <div class="links"><a href="/dashboard">Back to Dashboard</a></div>
  </div>
</div>
</body></html>"""

ADD_DOCTORS_HTML = """<!DOCTYPE html><html><head><title>Add Doctor</title>""" + BASE_STYLE + """</head>
<body>
<div class="center-card">
  <div class="card">
    <div class="logo">&#128104;&#8205;&#9877;&#65039;</div>
    <h2>Add Doctor</h2>
    <form action="/add_doctors" method="POST">
      <label>Full Name</label>
      <input type="text"  name="name"           placeholder="Doctor's full name"  required>
      <label>Specialization</label>
      <input type="text"  name="specialization" placeholder="e.g. Cardiologist"   required>
      <label>Phone</label>
      <input type="text"  name="phone"          placeholder="Phone number"        required>
      <label>Email</label>
      <input type="email" name="email"          placeholder="Doctor's email"      required>
      <button type="submit" class="btn-primary">Add Doctor</button>
    </form>
    <div class="links"><a href="/admin">Back to Admin</a></div>
  </div>
</div>
</body></html>"""

VIEW_DOCTORS_HTML = """<!DOCTYPE html><html><head><title>Doctors</title>""" + BASE_STYLE + """</head>
<body>
<nav>
  <h1>&#127973; Hospital Management</h1>
  <div>
    <a href="/add_doctors">+ Add Doctor</a>
    <a href="/admin">Admin</a>
    <a href="/dashboard">Dashboard</a>
    <a href="/logout">Logout</a>
  </div>
</nav>
<div class="container">
  <h2 class="page-title">Our Doctors</h2>
  <div class="grid">
    {% for d in doctors %}
    <div class="doctor-card">
      <div class="avatar">&#128104;&#8205;&#9877;&#65039;</div>
      <h3>{{ d[1] }}</h3>
      <p class="spec">{{ d[2] }}</p>
      <p class="info">&#128222; {{ d[3] }}</p>
      <p class="info">&#9993;&#65039; {{ d[4] }}</p>
    </div>
    {% else %}
    <p style="color:#999;font-size:18px;text-align:center;width:100%;">No doctors added yet.</p>
    {% endfor %}
  </div>
</div>
</body></html>"""

ADMIN_HTML = """<!DOCTYPE html><html><head><title>Admin Panel</title>""" + BASE_STYLE + """</head>
<body>
<nav>
  <h1>&#127973; Admin Panel</h1>
  <div>
    <a href="/add_doctors">+ Add Doctor</a>
    <a href="/doctors">Doctors</a>
    <a href="/reports">Reports</a>
    <a href="/dashboard">Dashboard</a>
    <a href="/logout">Logout</a>
  </div>
</nav>
<div class="container">

  <div class="section-card">
    <h2 class="section-title">Patients</h2>
    <form method="GET" action="/admin">
      <div class="search-bar">
        <input type="text" name="search" placeholder="Search by name..." value="{{ search or '' }}">
        <button type="submit">Search</button>
        <a href="/admin">Clear</a>
      </div>
    </form>
    <table>
      <thead><tr><th>#</th><th>Name</th><th>Email</th><th>Phone</th></tr></thead>
      <tbody>
        {% for p in patients %}
        <tr><td>{{ p[0] }}</td><td>{{ p[1] }}</td><td>{{ p[2] }}</td><td>{{ p[3] }}</td></tr>
        {% else %}
        <tr><td colspan="4" style="text-align:center;color:#999;">No patients found.</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <div class="section-card">
    <h2 class="section-title">Appointments</h2>
    <table>
      <thead><tr><th>#</th><th>Patient</th><th>Doctor</th><th>Date</th><th>Status</th><th>Actions</th></tr></thead>
      <tbody>
        {% for a in appointments %}
        <tr>
          <td>{{ a[0] }}</td><td>{{ a[1] }}</td><td>{{ a[2] }}</td><td>{{ a[3] }}</td>
          <td>
            <span class="badge {% if a[4]=='Approved' %}badge-approved{% elif a[4]=='Completed' %}badge-completed{% elif a[4]=='Cancelled' %}badge-cancelled{% else %}badge-pending{% endif %}">{{ a[4] }}</span>
          </td>
          <td>
            {% if a[4]=='Pending' %}
              <a href="/approve/{{ a[0] }}"  class="action-btn btn-approve">Approve</a>
              <a href="/cancel/{{ a[0] }}"   class="action-btn btn-cancel">Cancel</a>
            {% elif a[4]=='Approved' %}
              <a href="/complete/{{ a[0] }}" class="action-btn btn-complete">Complete</a>
              <a href="/cancel/{{ a[0] }}"   class="action-btn btn-cancel">Cancel</a>
            {% else %}
              <span style="color:#999;font-size:13px;">No actions</span>
            {% endif %}
          </td>
        </tr>
        {% else %}
        <tr><td colspan="6" style="text-align:center;color:#999;">No appointments found.</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

</div>
</body></html>"""

REPORTS_HTML = """<!DOCTYPE html><html><head><title>Reports</title>""" + BASE_STYLE + """</head>
<body>
<nav>
  <h1>&#127973; Hospital Reports</h1>
  <div>
    <a href="/admin">Admin</a>
    <a href="/dashboard">Dashboard</a>
    <a href="/logout">Logout</a>
  </div>
</nav>
<div class="container">
  <h2 class="page-title">Hospital Statistics</h2>
  <div class="stat-grid">
    <div class="stat-card"><h3>Total Patients</h3><p>{{ total_patients }}</p></div>
    <div class="stat-card"><h3>Total Doctors</h3><p>{{ total_doctors }}</p></div>
    <div class="stat-card"><h3>Total Appointments</h3><p>{{ total_appointments }}</p></div>
    <div class="stat-card"><h3>Approved Appointments</h3><p>{{ approved_appointments }}</p></div>
  </div>
</div>
</body></html>"""


# ═══════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════

@app.route('/')
def home():
    db = get_db(); cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM patients");     total_patients = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM doctors");      total_doctors = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM appointments"); total_appointments = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE status='Approved'")
    approved_appointments = cursor.fetchone()[0]
    cursor.close(); db.close()
    return render_template_string(INDEX_HTML,
        total_patients=total_patients, total_doctors=total_doctors,
        total_appointments=total_appointments, approved_appointments=approved_appointments)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]; password = request.form["password"]
        db = get_db(); cursor = db.cursor()
        cursor.execute("SELECT * FROM patients WHERE email=%s", (email,))
        user = cursor.fetchone(); cursor.close(); db.close()
        if user and check_password_hash(user[4], password):
            session.permanent = True; session["user"] = email
            return redirect("/dashboard")
        return render_template_string(LOGIN_HTML, error="Invalid email or password")
    return render_template_string(LOGIN_HTML, error=None)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]; email = request.form["email"]
        phone = request.form["phone"]; password = generate_password_hash(request.form["password"])
        db = get_db(); cursor = db.cursor()
        cursor.execute("INSERT INTO patients(name, email, phone, password) VALUES(%s,%s,%s,%s)",
                       (name, email, phone, password))
        db.commit(); cursor.close(); db.close()
        return redirect("/login")
    return render_template_string(REGISTER_HTML)

@app.route("/appointment", methods=["GET", "POST"])
def appointment():
    if request.method == "POST":
        db = get_db(); cursor = db.cursor()
        cursor.execute(
            "INSERT INTO appointments(patient_name, doctor_name, appointment_date, status) VALUES(%s,%s,%s,%s)",
            (request.form["patient_name"], request.form["doctor_name"], request.form["appointment_date"], "Pending"))
        db.commit(); cursor.close(); db.close()
        return redirect("/")
    return render_template_string(APPOINTMENT_HTML)

@app.route("/admin")
def admin():
    if "user" not in session: return redirect("/login")
    db = get_db(); cursor = db.cursor()
    search = request.args.get("search")
    if search:
        cursor.execute("SELECT * FROM patients WHERE name LIKE %s", ('%' + search + '%',))
    else:
        cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    cursor.execute("SELECT * FROM appointments")
    appointments = cursor.fetchall(); cursor.close(); db.close()
    return render_template_string(ADMIN_HTML, patients=patients, appointments=appointments, search=search)

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template_string(DASHBOARD_HTML, user=session["user"])
    return redirect("/login")

@app.route("/logout")
def logout():
    session.clear(); return redirect("/login")

@app.route("/add_doctors", methods=["GET", "POST"])
def add_doctors():
    if "user" not in session: return redirect("/login")
    if request.method == "POST":
        db = get_db(); cursor = db.cursor()
        cursor.execute("INSERT INTO doctors(name, specialization, phone, email) VALUES(%s,%s,%s,%s)",
            (request.form["name"], request.form["specialization"], request.form["phone"], request.form["email"]))
        db.commit(); cursor.close(); db.close()
        return redirect("/doctors")
    return render_template_string(ADD_DOCTORS_HTML)

@app.route("/doctors")
def doctors():
    db = get_db(); cursor = db.cursor()
    cursor.execute("SELECT * FROM doctors")
    all_doctors = cursor.fetchall(); cursor.close(); db.close()
    return render_template_string(VIEW_DOCTORS_HTML, doctors=all_doctors)

@app.route("/approve/<int:id>")
def approve(id):
    if "user" not in session: return redirect("/login")
    db = get_db(); cursor = db.cursor()
    cursor.execute("UPDATE appointments SET status='Approved' WHERE id=%s", (id,))
    db.commit(); cursor.close(); db.close(); return redirect("/admin")

@app.route("/complete/<int:id>")
def complete(id):
    if "user" not in session: return redirect("/login")
    db = get_db(); cursor = db.cursor()
    cursor.execute("UPDATE appointments SET status='Completed' WHERE id=%s", (id,))
    db.commit(); cursor.close(); db.close(); return redirect("/admin")

@app.route("/cancel/<int:id>")
def cancel(id):
    if "user" not in session: return redirect("/login")
    db = get_db(); cursor = db.cursor()
    cursor.execute("UPDATE appointments SET status='Cancelled' WHERE id=%s", (id,))
    db.commit(); cursor.close(); db.close(); return redirect("/admin")

@app.route("/reports")
def reports():
    if "user" not in session: return redirect("/login")
    db = get_db(); cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM patients");     total_patients = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM doctors");      total_doctors = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM appointments"); total_appointments = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE status='Approved'")
    approved_appointments = cursor.fetchone()[0]; cursor.close(); db.close()
    return render_template_string(REPORTS_HTML,
        total_patients=total_patients, total_doctors=total_doctors,
        total_appointments=total_appointments, approved_appointments=approved_appointments)


# ═══════════════════════════════════════════════
if __name__ == '__main__':
    debug_mode = os.environ.get("DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)