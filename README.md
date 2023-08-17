## Dcarbon Project

This is Python Project for Dcarbon.
Map Route integration and Straighten image and text extraction using OpenCV - Python

## Installation

To install and run this project locally, follow these steps:

1. Clone the repository: `git clone  https://github.com/Ajaykj684/Dcarbon_project.git`
2. Change into the project directory: `cd project`
3. Install virtual environment: `pip install virtualenv`
4. Intialize virtualenv: `virtualenv venv`
5. Activate virtualenv: `venv\Scripts\activate`
6. Install the project dependencies: `pip install -r requirements.txt`
7. create a file name `.env` and add required values for database and map api key.
8. making migrations for Database: `python manage.py makemigrations`
9. Migrate For reflecting it on db: `python manage.py migrate`
7. Start: `python manage.py runserver`