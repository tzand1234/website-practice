# Flask Application: Meal Management System
This is a Flask-based web application that manages meal participation and meal reporting. The application enables users to log in, sign up as a cook, participate in meals, report meals, and manage meal-related data. The application uses SQLite for database management, Flask-Mail for email functionalities, and Flask-Login for user authentication.

# Features:
User Authentication: Secure login system via email with a one-time token.
Meal Management: Users can sign up as a cook, report meals, and track participants.
Meal Reporting: Cook can report meal details, including meal photo uploads.
User Dashboard: Displays meal data and user activity.
Email Notifications: Send login link via email.
Technologies:
Flask
Flask-Login
Flask-Mail
SQLAlchemy (for database management)
SQLite
HTML/Jinja2 templates
Python (for backend logic)
Requirements:
Python 3.x
Flask
Flask-Login
Flask-Mail
SQLAlchemy
PostgreSQL / SQLite
Installation Instructions:
Clone the repository:

bash
Copy code
git clone <repository-url>
cd <repository-folder>
Create a virtual environment:

bash
Copy code
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Set up the database: This application uses SQLite for database management. Ensure that the appropriate configurations are in place.

Run the application:

bash
Copy code
python app.py
The app will be available at http://localhost:5000.

# Configuration:
SECRET_KEY: Used for session management and CSRF protection. Generated with secrets.token_hex(16).
DATABASE URI: Set up the PostgreSQL URI in postgresqlite.get_uri().
Email Configuration:
Mail server: smtp.ethereal.email
Username: maude.cronin@ethereal.email
Password: jvdfFNjXEFexHnRDFH
Routes and Functionality:
/
Method: GET, POST
Description: Displays the login page and handles login form submission. Sends an email with a unique token to log in.
/auth/<username>/<token>
Method: GET
Description: Authenticates the user with a valid token and redirects to the dashboard.
/dashboard
Method: GET
Description: Displays the user dashboard with meal and user data for the day.
/form/<int:meal_id>
Method: GET, POST
Description: Displays the form for meal reporting. Allows cooks to upload photos and update meal details.
/participate/<int:meal_id>
Method: GET
Description: Allows users to participate or unparticipate in a meal.
/participate/<int:meal_id>/cook
Method: GET, POST
Description: Allows a user to sign up as the cook for a meal.
/logout
Method: GET
Description: Logs out the user and redirects to the login page.
Security:
Login tokens are stored in the database and are valid for a limited time.
User passwords are not stored directly in the database (handled by Flask-Login).
User sessions are managed securely with Flask's session system.
Troubleshooting:
Ensure that the database is set up correctly and that all required tables are created.
If email functionality is not working, verify the email server settings in the configuration.
If there are issues with file uploads, make sure that the UPLOAD_FOLDER exists and is writable.
