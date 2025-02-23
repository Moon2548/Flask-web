# Flask Web Project

## Overview
This is a Flask-based web application with a structured backend for handling requests, user authentication, and database interactions.

## Features
- Flask-based web application
- Uses templates for dynamic HTML rendering
- Static files for styling (CSS)
- Database models for storing data
- Form handling for user input

## Project Structure
```
Flask-web/
│── instance/            # Instance-specific data, such as SQLite database files
│── static/css/         # CSS files for styling and UI enhancements
│── templates/          # HTML templates for rendering web pages
│── .gitignore          # Specifies files to ignore in Git
│── acl.py              # Access Control List (ACL) logic for authorization
│── forms.py            # Form handling for user authentication and input
│── models.py           # Database models defining table structures
│── noteapp.py          # Main Flask application file to start the server
│── poetry.lock         # Dependency lock file for Poetry
│── pyproject.toml      # Project configuration and dependency management for Poetry
```

## Installation and Setup
### Prerequisites
Ensure you have the following installed:
- Python (>=3.8)
- Poetry (for dependency management)

### Steps to Run
1. Clone the repository:
   ```sh
   git clone https://github.com/Moon2548/Flask-web.git
   cd Flask-web
   ```
2. Install dependencies using Poetry:
   ```sh
   poetry install
   ```
3. Run the application:
   ```sh
   poetry run python .\noteapp.py
   ```
4. Open your browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

## License
This project is licensed under the MIT License.
