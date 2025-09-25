# Fyyur Event Management (Extended)

This repository is based on the Udacity Backend Developer with Python Nanodegree project: [fyyur-event-management](https://github.com/udacity/cd0046-SQL-and-Data-Modeling-for-the-Web).

I am extending the project by designing the **conceptual, logical, and physical ERD**, and implementing the **SQLAlchemy database model** with constraints, indexes, and relationships for better normalization and data governance.

### Project Highlights & Key Features

- **Modular Architecture**: Code is separated into app.py (controllers), models.py (database models), and forms.py (form definitions).
- **Full CRUD & Soft Deletes**: Supports creating, reading, updating, and soft-deleting artists and venues.
- **Efficient Queries**: All database queries are optimized using SQLAlchemy's joinedload to prevent performance issues (N+1 problem).
- **Validation**: Includes custom server-side validation to ensure data integrity, such as preventing the creation of shows for deleted venues or artists.
- **Dynamic Search**: Features case-insensitive, partial-text search for both artists and venues.
- **Design Decisions**: The application was built with modern practices in mind, including flexible social media link handling and a focus on artist data privacy.

### Goals

- Build a production-ready schema aligned with industry best practices.
- Showcase structured project growth and planning for portfolio/review purposes.

### Design Decisions

This project was extended with several key design choices to better align with modern web development best practices and data privacy principles.

- **Artist Data Privacy:** The `Artist` model and corresponding forms intentionally do not capture location or phone number information. This decision adheres to data minimization principles (GDPR), avoiding the collection of sensitive personal data that is not essential to the application's core functionality.

- **Flexible Social Links:** The original `facebook_link` and `website_link` fields in the forms were replaced with a single, flexible `social_link` field. The backend detects the platform (Instagram, TikTok, X, etc.) from the provided URL. This makes the application more modern, user-friendly, and adaptable to future changes in social media trends.

---

## ERD Diagrams

<details>
<summary><strong>View ERD Diagrams</strong></summary>

- Conceptual ERD

![- Conceptual ERD](/docs/erd/1-conceptual-erd.png)

- Logical ERD

![- Logical ERD](/docs/erd/2-logical-erd.png)

- Physical ERD

![- - Physical ERD](/docs/erd/3-physical-erd.png)

</details>

## Tech Stack (Dependencies)

| Backend             | Frontend         | Database     |
| ------------------- | ---------------- | ------------ |
| Python 3.11 & Flask | HTML5 & CSS3     | PostgreSQL   |
| SQLAlchemy          | JavaScript (ES6) |              |
| Flask-Migrate       | Bootstrap 3      |              |
| Flask-WTF           |                  |              |

---

### Local Development Setup

To run this project locally, please follow these steps.

#### 1. Clone the Repository

```bash
git clone https://github.com/circobit/fyyur-event-management

cd fyyur-event-management
```

#### 2. Setup environment

Create and activate a Python virtual environment.

```bash
# Create the environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Activate it (Windows)
.\venv\Scripts\activate
```

#### 3. Install dependencies

Install all required Python and frontend packages.

```bash
# Install Python packages
pip install -r requirements.txt

# Install frontend packages (requires Node.js)
npm install
```

#### 4. Configure the database

1. Ensure you have PostgreSQL installed and running. If you don't have one, follow the instructions for your operating system.

**On macOS (using Homebrew):**

```bash
# Install PostgreSQL
brew install postgresql

# Start the PostgreSQL service
brew services start postgresql

# Create the database
createdb fyyur
```

**On Windows**

- Download the installer from the PostgreSQL official website -> https://www.postgresql.org/download/windows/
- Run the installer (accepting default settings is usually fine).
- After installation, open the SQL Shell (psql).
- Press Enter to accept the default server, database, port, and username. Enter the password you created during installation.
- Create the database by running:
```sql
CREATE DATABASE fyyur;
```

**On Linux**

```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Create the database
sudo -u postgres createdb fyyur
```

2. Open config.py and update the SQLALCHEMY_DATABASE_URI with your database credentials:

```python
# Example for a user named 'postgres' with no password
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost:5432/fyyur'
```

3. Run the database migrations to create all the necessary tables.

```bash
flask db upgrade
```

#### 5. Run the application

Use the Flask CLI to run the development server.

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

You can now access the application at `http://127.0.0.1:5000/`