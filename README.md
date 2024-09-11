# AffordPhysio API: Telehealth Management System
## License
[![License: DJANGO](https://img.shields.io/badge/License-Django-brightgreen.svg)](https://www.djangoproject.com/trademarks/)

The telehealth management system bridges the gap between physiotherapists and patients. It allows the patients to book appointments, view services provided and engage in a self-screening process.

## Useful Commands

Log into the database

```shell
psql -U amref -p 5434 -d afford_physio
```
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

The project consists of the following main django apps:
- *api/* Main application entry point.
- *app_admin/*: Contains routes for admin module
- *app_manager/*: Contains routes for manager module
- *app_physio/*: Contains routes for physiotherapist module
- *patient/*: Contains routes for patient module

### Key Files:
- *views.py*: Defines all the views for respective module
- *urls.py*: Defines all the routes for respective module
- *models.py*: Defines all Django models for respective module
- *admin.py*: Registers the models to enable viewing on the django admin interface.
- *serializers.py*: Serializes data to fit model format.

## Acknowledgements

 - [Markdown Cheatsheet](https://github.com/tchapi/markdown-cheatsheet/blob/master/README.md)

## Contact Us

For support,question or contribution email dennismthairu@gmail.com or create an issue in this repository. This is the fastest way to reach us.
