## Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

Make sure you have the following installed:

- Python 3.x
- Pip (Python package installer)

### Installation

1. Clone the repository:

   ```bash
   git clonehttps://github.com/akashdarekar3112/BPO-Project.git
   ```

2. Navigate to the project directory:

    ```bash
    cd BPO-Project
    ```

3. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    ```

    ```bash
    source venv/bin/activate      # On Linux/Mac
    ```
    
    OR

    ```bash
    .\venv\Scripts\activate       # On Windows
    ```

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```
5. start dokcer

     ```bash
    docker-compose up -d
    ```

### Database Setup

6. Perform initial migrations:

    ```bash
    python manage.py makemigrations
    ```

    ```bash
    python manage.py migrate
    ```


### Running the Server

7. Start the development server:

    ```bash
    python manage.py runserver
    ```

    The server will run at http://localhost:8000/.

### Swagger Documentation

Explore the API using Swagger documentation:

    http://localhost:8000/swagger/
