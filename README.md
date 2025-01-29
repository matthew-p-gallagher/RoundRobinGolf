# 🏌️ RoundRobinGolf

A Flask web application for tracking a new golf scoring system. Basic working version - still WIP to sure up login system and improve UX before adding other score formats.

## Getting Started

### Prerequisites

-   Python 3.8 or higher
-   pip (Python package manager)
-   SQLite3

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/RoundRobinGolf.git
    cd RoundRobinGolf
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On Unix or MacOS
    source venv/bin/activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Create instance/config.py with your configuration:

    ```python
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///roundrobingolf.db'
    ```

5. Initialize the database:

    ```bash
    python init_db.py
    ```

6. Run the application:
    ```bash
    flask run
    ```

## Project Structure

```
RoundRobinGolf/
├── app/                    # Application package
│   ├── blueprints/        # Route blueprints
│   ├── static/            # Static files (CSS, JS)
│   ├── templates/         # HTML templates
│   ├── models.py          # Database models
│   └── __init__.py        # App initialization
├── instance/              # Instance-specific config
├── tests/                 # Test suite
├── requirements.txt       # Project dependencies
└── init_db.py            # Database initialization
```

## Database Models

-   **User**: Manages user accounts and authentication
-   **Match**: Represents a golf match session
-   **Player**: Stores player information and scores
-   **Hole**: Tracks individual hole information
-   **PointsTable**: Maintains match statistics
-   **HoleMatch**: Records individual hole matches between players

## Development

-   Run tests: `pytest`
-   Format code: `black .`
-   Lint code: `flake8`
