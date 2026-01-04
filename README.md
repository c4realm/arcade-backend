# Arcade Backend

Arcade is a peer-to-peer learning platform where users can create, publish, and learn from courses made by other users.
Arcade is a learning management platform built with Django that allows users to browse courses and administrators to manage educational content through a secure admin interface.
The goal of Arcade is to provide a simple, extensible foundation for an online learning platform.

## Project Status
This repository contains the initial planning and backend setup for the Arcade capstone project.

## Features (Planned)
- User authentication
- Course creation and approval
- Video-based learning
- Ratings and recommendations
- Comments and replies
- Study groups and learning sessions

## plemented Features
User authentication and authorization
Admin dashboard for managing content
Course management (create, update, delete courses)
Course listing displayed on the homepage

SQLite database integration
## Tech Stack
- Python
- Django
- Django REST Framework
- PostgreSQL 

Project Structure

arcade-backend/
│
├── backend/
│   ├── accounts/      # Custom user model & authentication
│   ├── courses/       # Course management app
│   ├── groups/        # User grouping & roles
│   ├── config/        # Project settings and configuration
│   ├── templates/     # HTML templates
│   ├── db.sqlite3
│   └── manage.py
│
├── docs/              # Project documentation
├── README.md
└── requirements.txt

