# AffordPhysio API: Telehealth Management System
## License
[![License: DJANGO](https://img.shields.io/badge/License-Django-brightgreen.svg)](https://www.djangoproject.com/trademarks/)

The telehealth management system bridges the gap between physiotherapists and patients. It allows the patients to book appointments, view services provided and engage in a self-screening process.

# Project Setup/Installation Instructions:
## Dependencies:
* Python
* Django
* python-dotenv

# Installation Steps:
1. Clone the repository from GitHub
  ```
  bash
  ```
  
  ```
  git clone https://github.com/Dennis-Mugo/affordphysio_api.git
  ```


2. Navigate to project folder
    ```
    bash
    ```
    ```
    cd affordphysio_api
    ```


3. Install dependencies:
    ```
    bash
    ```
    ```
    pip install -r requirements.txt
    ```

---
# Usage Instructions
## How to run

1. Ensure you are in the project directory

   
2. Run the Django application in the terminal
   ```
    bash
   ```
    ```
    python manage.py runserver
    ```


3. Open a web browser and go to http://127.0.0.1:8000/ to view the application.

## Project Structure:

### Overview:

The project consists of the following main components:
- *app.py:* Main application entry point.
- *templates/*: HTML templates for rendering web pages.
- *static/*: Static files (e.g., CSS, images) used in the application.

### Key Files:
- *app.py*: Flask application setup and routes.
- *forms.py*: Defines SQLAlchemy forms for registration, login and appointments
- *models.py*: Defines SQLAlchemy models for pets, owners, appointments, etc.
- *forms.py*: WTForms used for form validation and rendering.
- *templates/*: Contains HTML templates using Jinja2 templating engine.
- *static/*: CSS, images, and other static assets.
