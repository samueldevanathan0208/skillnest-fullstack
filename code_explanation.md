# SkillNest Code Explanation: Signup & Login

This document explains how the **Login** and **Signup** pages of SkillNest work. We will break them down into three parts: **HTML** (the structure), **CSS** (the design), and **JavaScript** (the brain).

---

## 1. Login Page (`login.html`)

### 🏗️ HTML (The Structure)
- **Navbar**: The top section where you see the logo and links like "Home", "Courses", and "About".
- **Login Container**: A central box that holds the login header and the form.
- **Form**: This is the heart of the page. It contains:
    - An `<input>` for **Email**.
    - An `<input>` for **Password**.
    - A **Sign In** button to submit the info.
- **Social Buttons**: A placeholder section for logging in with Google.
- **Register Link**: A link that takes the user to the signup page if they don't have an account.

### 🎨 CSS (The Design)
The styles are located in `../css/login.css`.
- **Flexbox**: Used to center everything on the screen and align the login box next to the image.
- **Colors**: Uses a clean, professional palette with rounded buttons and soft shadows to make it look modern.
- **Responsive**: The layout adjusts so it looks good on both computers and mobile phones.

### 🧠 JavaScript (The Brain)
The script at the bottom of the file handles what happens when you click "Sign in":
1. **Prevent Default**: It stops the page from refreshing automatically.
2. **Collect Data**: It grabs the email and password you typed.
3. **API Call**: It sends this data to the backend server (using `apiFetch`).
4. **Token Storage**: If the password is correct, the server sends back a "token" (like a digital key). We save this key in `localStorage` so the website remembers you are logged in.
5. **Redirect**: It sends you to your `dashboard.html`.

---

## 2. Signup Page (`signup.html`)

### 🏗️ HTML (The Structure)
The signup page has more fields because we need more information from a new user:
- **Full Name**: So we know what to call you.
- **Email & Password**: For your account credentials.
- **Confirm Password**: To make sure you didn't make a typo.
- **Date of Birth**: Used to verify your age (must be 12+).
- **Phone & Gender**: Additional profile details.

### 🎨 CSS (The Design)
The styles are in `../css/signup.css`.
- It follows the same "look and feel" as the login page to keep the experience consistent.
- It uses a large image on the left to make the page visually appealing.

### 🧠 JavaScript (The Brain)
The logic here is a bit more complex to ensure data is correct before sending it:
1. **Age Validation**: It automatically calculates if you are at least 12 years old. If you're too young, it won't let you submit.
2. **Password Check**: It checks if the "Password" and "Confirm Password" fields match.
3. **Data Packaging**: It gathers all your info (Name, Email, DOB, etc.) into an object.
4. **Create User**: It sends this information to the server's `/create_user` endpoint.
5. **Success**: If everything is okay, it shows an alert "Signup successful!" and takes you to the Login page so you can sign in.

---

## 💡 Summary of How They Work Together
1. **Signup**: You tell the server who you are. The server saves your details in a database.
2. **Login**: You prove who you are by giving your email and password. The server checks the database, and if they match, it gives you a "token".
3. **Navigation**: As long as you have that "token" saved in your browser, you can access your dashboard and courses!
