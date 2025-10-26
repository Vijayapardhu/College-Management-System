# 👋 Beginner's Guide to EduVision

**For team members new to programming - Start here!**

**[← Back to README](README.md)** | **[Next: Developer Guide →](DEVELOPER_GUIDE.md)**

---

## 🤔 What is This Project?

EduVision is a **website** for managing colleges. Think of it like:
- A college office that's online
- Stores all student, teacher, and course information
- Anyone can access it from their browser

---

## 📁 What Are These Folders?

```
College-Management-System/
│
├── main_app/               👈 THE MAIN CODE IS HERE
│   ├── templates/          👈 HTML pages (what you see in browser)
│   ├── static/             👈 CSS, images, JavaScript
│   ├── models.py           👈 Database structure (tables)
│   ├── views.py            👈 What happens when you click
│   └── urls.py             👈 Website addresses (routes)
│
├── media/                  👈 User uploaded files
├── requirements.txt        👈 List of software needed
└── manage.py              👈 Command to run the project
```

---

## 🌐 How Websites Work (Simple Explanation)

### Step 1: User Types Address
```
http://127.0.0.1:8000/student/home/
```

### Step 2: Django Finds the Route
In `urls.py`:
```python
path("student/home/", student_views.student_home)
```

### Step 3: Function Runs
In `student_views.py`:
```python
def student_home(request):
    # Get student data from database
    # Show HTML page
```

### Step 4: HTML Page Shows
File: `templates/student_template/home_content.html`
```html
<h1>Welcome, Student!</h1>
```

### Step 5: User Sees Page in Browser!

---

## 🗂️ Understanding the Database

Think of database like **Excel sheets**:

**Students Table:**
| Name | Roll Number | Course |
|------|-------------|--------|
| John | 2021001 | B.Tech |
| Mary | 2021002 | M.Tech |

**Attendance Table:**
| Student | Date | Present? |
|---------|------|----------|
| John | 2025-01-15 | Yes |
| John | 2025-01-16 | No |

---

## 🎨 Understanding HTML Pages

### HTML = Structure
```html
<h1>Student Dashboard</h1>
<p>Welcome to your dashboard!</p>
```

### CSS = Style (Colors, Fonts)
```css
h1 {
    color: blue;
    font-size: 24px;
}
```

### JavaScript = Interactivity
```javascript
button.onclick = function() {
    alert("Button clicked!");
}
```

---

## 🔑 5 User Types Explained

### 1. Student
- **Can do**: View attendance, see results, submit assignments
- **Login**: student@example.com
- **Dashboard**: `/student/home/`

### 2. Faculty/Staff
- **Can do**: Mark attendance, enter marks, upload materials
- **Login**: staff@example.com
- **Dashboard**: `/staff/home/`

### 3. HOD/Admin
- **Can do**: Everything! Manage all users, see reports
- **Login**: admin@example.com
- **Dashboard**: `/admin/home/`

### 4. Management
- **Can do**: Manage hostel, transport, library, fees
- **Login**: management@example.com
- **Dashboard**: `/management/home/`

### 5. Parent
- **Can do**: See child's attendance, results, fees
- **Login**: parent@example.com
- **Dashboard**: `/parent/home/`

---

## 🛠️ How to Run the Project

### Step 1: Open Terminal/Command Prompt

**Windows**: Press `Win + R`, type `cmd`, press Enter  
**Mac**: Press `Cmd + Space`, type `terminal`, press Enter

### Step 2: Go to Project Folder

```bash
cd College-Management-System
```

### Step 3: Run the Server

```bash
python manage.py runserver
```

### Step 4: Open Browser

Go to: `http://127.0.0.1:8000/`

### Step 5: Login

Use the email and password you created!

---

## 📝 How to Make Small Changes

### Change Text on a Page

1. **Find the HTML file** in `main_app/templates/`
2. **Example**: Change "Welcome" to "Hello"

```html
<!-- Before -->
<h1>Welcome to Dashboard</h1>

<!-- After -->
<h1>Hello Dashboard</h1>
```

3. **Refresh browser** - Changes appear!

### Change Colors

1. **Find the CSS** in the `<style>` section or `static/css/`
2. **Example**: Change background color

```css
/* Before */
.card {
    background: white;
}

/* After */
.card {
    background: lightblue;
}
```

3. **Refresh browser** - New colors!

---

## 🧩 Common Files Explained

### `models.py` - Database Tables
```python
class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
```
This creates a **Students table** in database.

### `views.py` - What Happens When User Clicks
```python
def show_students(request):
    students = Student.objects.all()  # Get all students
    return render(request, 'students.html')
```

### `urls.py` - Website Addresses
```python
path("students/", views.show_students)
```
When user goes to `/students/`, run `show_students` function.

### `templates/` - HTML Pages
```html
<h1>All Students</h1>
{% for student in students %}
    <p>{{ student.name }}</p>
{% endfor %}
```

---

## 🎯 Learning Path for Team

### Week 1: Learn Basics
- **HTML**: How to create pages
- **CSS**: How to style pages
- **Resources**: W3Schools, MDN Web Docs

### Week 2: Understand Python
- **Variables, Functions, Loops**
- **Resources**: Python.org tutorials

### Week 3: Learn Django Basics
- **Models, Views, Templates**
- **Resources**: Django official tutorial

### Week 4: Explore This Project
- **Look at existing pages**
- **Make small changes**
- **Ask questions!**

---

## 💡 Tips for Beginners

1. **Don't Panic!** - Everyone starts somewhere
2. **Read Error Messages** - They tell you what's wrong
3. **Make Small Changes** - Test often
4. **Ask Questions** - Team is here to help
5. **Use Google** - Most errors are already solved online

---

## 🔍 Common Terms Explained

| Term | Meaning |
|------|---------|
| **Django** | Framework to build websites with Python |
| **Model** | A database table (like Excel sheet) |
| **View** | Function that runs when page loads |
| **Template** | HTML file that user sees |
| **URL** | Web address like /student/home/ |
| **Migration** | Creating/updating database tables |
| **Static files** | CSS, JavaScript, images |
| **Media files** | User uploaded files |

---

## 🚨 What NOT to Touch (For Now)

- ❌ Don't delete `manage.py`
- ❌ Don't change `settings.py` without guidance
- ❌ Don't modify `urls.py` without understanding
- ❌ Don't delete migration files
- ❌ Don't push to `main` branch without review

---

## ✅ Safe Things to Try

- ✅ Edit HTML text in templates
- ✅ Change CSS colors
- ✅ Add new HTML elements
- ✅ Read and understand code
- ✅ Ask team for help

---

## 📖 Helpful Resources

### Learn HTML
- [W3Schools HTML](https://www.w3schools.com/html/)
- [MDN HTML Guide](https://developer.mozilla.org/en-US/docs/Web/HTML)

### Learn CSS
- [W3Schools CSS](https://www.w3schools.com/css/)
- [CSS Tricks](https://css-tricks.com/)

### Learn Python
- [Python.org Tutorial](https://docs.python.org/3/tutorial/)
- [Learn Python](https://www.learnpython.org/)

### Learn Django
- [Django Official Tutorial](https://docs.djangoproject.com/en/4.2/intro/tutorial01/)
- [Django for Beginners](https://djangoforbeginners.com/)

---

## 🤝 Getting Help

1. **Read error messages carefully**
2. **Google the error** (copy-paste)
3. **Ask team member** who developed it
4. **Check Django documentation**
5. **Use ChatGPT** for explanations

---

## 🎯 First Tasks for Beginners

### Task 1: Run the Project
```bash
python manage.py runserver
```
Open browser, see it working!

### Task 2: Find Your Role's Dashboard
- Student? Go to `/student/home/`
- Staff? Go to `/staff/home/`

### Task 3: Find the HTML File
- Look in `main_app/templates/student_template/home_content.html`

### Task 4: Change Welcome Text
- Edit the `<h1>` tag
- Save file
- Refresh browser
- See your change!

---

## 🎉 You Can Do This!

Remember:
- Everyone was a beginner once
- Learning takes time
- Mistakes are how we learn
- The team is here to help

---

**[← Back to README](README.md)** | **[Next: Developer Guide →](DEVELOPER_GUIDE.md)**

