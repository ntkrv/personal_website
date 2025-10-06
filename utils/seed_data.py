import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from extensions import db
from models import Project, Certificate

app = create_app()

PROJECTS = [
    {
        "title": "My Personal Website Portfolio",
        "short_description": "Portfolio website built with Flask and Tailwind CSS to showcase projects and skills.",
        "long_description": (
            "This is my personal portfolio website designed to present my skills, experience, and projects in a professional way. "
            "The website is built using Flask for the backend and Tailwind CSS + JavaScript for interactivity. "
            "It features an admin panel for dynamic content management and incorporates DevOps automation to simplify deployment, updates, and monitoring."
        ),
        "image_path": "https://images.unsplash.com/photo-1621839673705-6617adf9e890?q=80",
        "stack": "Flask, HTML, Tailwind CSS, JavaScript, DevOps, SQLite, Git",
        "link_type": "github",
        "git_link": "https://github.com/ntkrv/personal_website",
    },
    {
        "title": "Power BI Dashboards Portfolio",
        "short_description": "A collection of interactive dashboards built in Power BI, showcasing business insights and trend analysis.",
        "long_description": (
            "This portfolio contains my BI dashboards designed in Power BI, covering demand planning, logistics, and business reporting. "
            "The dashboards highlight my ability to transform raw data into actionable insights with clean, interactive visualizations."
        ),
        "image_path": "https://images.unsplash.com/photo-1666875753105-c63a6f3bdc86?q=80",
        "stack": "Power BI, Excel, DAX, SQL",
        "link_type": "gdrive",
        "git_link": "https://drive.google.com/drive/folders/1xoM9KNpCi4QqlTmSNGTaHtbdsRVDbevV?usp=sharing",
    },
    {
        "title": "Python Report Automation",
        "short_description": "Automated reporting system to optimize data processing and save time.",
        "long_description": (
            "A Python-based project for optimizing report generation. "
            "It includes automated data extraction, cleaning, and transformation pipelines, followed by report creation in Excel/CSV format. "
            "This solution significantly reduced manual workload and improved reporting efficiency."
        ),
        "image_path": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=2426&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "stack": "Python, Pandas, NumPy, Excel, SQL",
        "link_type": "github",
        "git_link": "https://github.com/ntkrv/report-automation",
    },
]

CERTIFICATES = [
    {
        "title": "Python Basic",
        "issuer": "Hillel IT School",
        "link": "https://certificate.ithillel.ua/ru/view/53638263",
    },
    {
        "title": "Python Pro",
        "issuer": "Hillel IT School",
        "link": "https://certificate.ithillel.ua/ru/view/73097786",
    },
    {
        "title": "Data Visualization",
        "issuer": "Udemy",
        "link": "https://udemy.com/certificate/data-visualization",
    },
]


def seed():
    with app.app_context():
        print("Seeding database...")

        Project.query.delete()
        Certificate.query.delete()

        for p in PROJECTS:
            db.session.add(Project(**p))

        for c in CERTIFICATES:
            db.session.add(Certificate(**c))

        db.session.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    seed()
