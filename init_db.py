from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()


def create_default_admin():
    # Check if admin user already exists
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="test@test.com",
            password_hash=generate_password_hash("test123"),
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created.")
    else:
        print("Admin user already exists.")


with app.app_context():
    db.create_all()
    print("Database initialized.")
    create_default_admin()
