function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.id) {
            localStorage.setItem("user", JSON.stringify(data));
            window.location.href = "dashboard.html";
        } else {
            alert("Login Failed");
        }
    });
}
// Check if user is logged in
function getUser() {
    return JSON.parse(localStorage.getItem("user"));
}

// Logout function
function logout() {
    localStorage.removeItem("user");
    window.location.href = "index.html";
}

// Load Dashboard Data
function loadDashboard() {
    const user = getUser();
    if (!user) {
        window.location.href = "index.html";
        return;
    }

    document.getElementById("username").textContent = user.username;

    fetch(`http://127.0.0.1:5000/my_courses/${user.id}`)
    .then(response => response.json())
    .then(data => {
        const courseList = document.getElementById("enrolled-courses");
        courseList.innerHTML = "";
        data.forEach(course => {
            const li = document.createElement("li");
            li.textContent = course.course_id;
            courseList.appendChild(li);
        });
    });

    fetch("http://127.0.0.1:5000/courses")
    .then(response => response.json())
    .then(data => {
        const courseList = document.getElementById("available-courses");
        courseList.innerHTML = "";
        data.forEach(course => {
            const li = document.createElement("li");
            li.textContent = `${course.id} - ${course.name}`;
            li.onclick = () => enrollCourse(course.id);
            courseList.appendChild(li);
        });
    });
}

// Enroll in a course
function enrollCourse(courseId) {
    const user = getUser();
    fetch("http://127.0.0.1:5000/enroll", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ student_id: user.id, course_id: courseId })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        loadDashboard();
    });
}
// Load available courses for enrollment
function loadAvailableCourses() {
    fetch("http://127.0.0.1:5000/courses")
    .then(response => response.json())
    .then(data => {
        const courseList = document.getElementById("course-list");
        courseList.innerHTML = "";
        data.forEach(course => {
            const li = document.createElement("li");
            li.textContent = `${course.id} - ${course.name}`;
            li.onclick = () => enrollCourse(course.id);
            courseList.appendChild(li);
        });
    });
}

// Load Admin Panel Data
function loadAdminPanel() {
    fetch("http://127.0.0.1:5000/users")
    .then(response => response.json())
    .then(data => {
        const userList = document.getElementById("user-list");
        userList.innerHTML = "";
        data.forEach(user => {
            const li = document.createElement("li");
            li.textContent = `${user.id} - ${user.username} (${user.role})`;
            userList.appendChild(li);
        });
    });
}

// Add a new course (Admin Only)
function addCourse() {
    const name = document.getElementById("course-name").value;
    const instructor = document.getElementById("course-instructor").value;

    fetch("http://127.0.0.1:5000/add_course", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, instructor })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        loadAdminPanel();
    });
}
// Get stored user data
function getUser() {
    return JSON.parse(localStorage.getItem("user"));
}

// Send token with request
function fetchWithAuth(url, options = {}) {
    const user = getUser();
    if (!user) {
        window.location.href = "index.html";
        return;
    }

    if (!options.headers) options.headers = {};
    options.headers["Authorization"] = "Bearer " + user.access_token;

    return fetch(url, options);
}

// Enroll in a course (Student Only)
function enrollCourse(courseId) {
    fetchWithAuth("http://127.0.0.1:5000/enroll", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ course_id: courseId })
    })
    .then(response => response.json())
    .then(data => alert(data.message));
}

// Add Course (Admin Only)
function addCourse() {
    const name = document.getElementById("course-name").value;
    const instructor = document.getElementById("course-instructor").value;

    fetchWithAuth("http://127.0.0.1:5000/add_course", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, instructor })
    })
    .then(response => response.json())
    .then(data => alert(data.message));
}
