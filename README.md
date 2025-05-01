# BPO Project Backend

## Getting Started

There are two ways to run this project: using Docker (recommended) or traditional setup.

### Option 1: Docker Setup (Recommended)

#### Prerequisites
- Docker
- Docker Compose

#### Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/akashdarekar3112/BPO-Project.git
   ```

2. Navigate to the project directory:
   ```bash
   cd BPO-Project
   ```

3. Build and start the Docker containers:
   ```bash
   docker-compose up --build
   ```

4. In a new terminal, run the migrations:
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

5. Create a superuser (admin):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

The application will be available at:
- API: http://localhost:8000/
- Admin Interface: http://localhost:8000/admin/
- API Documentation: http://localhost:8000/api/docs/

To stop the containers:
```bash
docker-compose down
```

### Option 2: Traditional Setup

#### Prerequisites
- Python 3.8+
- PostgreSQL
- Pip (Python package installer)

#### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/akashdarekar3112/BPO-Project.git
   ```

2. Navigate to the project directory:
   ```bash
   cd BPO-Project
   ```

3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Linux/Mac
   # OR
   .\venv\Scripts\activate      # On Windows
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a .env file in the root directory and add your environment variables:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   POSTGRES_DB=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_password
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```

6. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

8. Start the development server:
   ```bash
   python manage.py runserver
   ```

The server will run at http://localhost:8000/

### API Documentation

Explore the API using Swagger documentation at:
```
http://localhost:8000/api/docs/
```

### Environment Variables

The following environment variables are required:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_HOST`: Database host
- `POSTGRES_PORT`: Database port
- `SENDGRID_API_KEY`: SendGrid API key for email
- `STRIPE_PUBLISHABLE_KEY`: Stripe publishable key
- `STRIPE_SECRET_KEY`: Stripe secret key
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook secret
