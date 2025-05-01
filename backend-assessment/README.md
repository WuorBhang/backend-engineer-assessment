# Auction API - Django REST Framework

## Setup Instructions

1. Clone the repository
2. Create and activate virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows


   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt

   ```

4. Run migrations:

   ```bash
   python manage.py migrate

   ```

5. Create superuser:

   ```bash
   python manage.py createsuperuser

   ```

6. Run development server:

   ```bash
   python manage.py runserver
   ```

## API Documentation

Access Swagger docs at `http://localhost:8000/swagger/` after starting server
