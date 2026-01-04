## Arcade Backend

## Overview
Arcade is a peer-to-peer learning platform that enables users to create, publish, and learn from courses developed by other users.
It is built with Django and provides a solid backend foundation for an online learning management system.

The platform allows learners to browse courses while administrators manage educational content through a secure admin interface.
Arcade is designed to be simple, scalable, and extensible, making it suitable for future feature expansion.

## Planned Features

User authentication and authorization

Course creation with content approval workflow

Video-based learning support

Course ratings and recommendations

Comments and threaded replies

Study groups and learning sessions

## Implemented Features

User authentication and authorization

Admin dashboard for content management

Course management (create, update, delete)

Course listing displayed on the homepage

SQLite database integration

## Tech Stack

Backend: Python, Django

API: Django REST Framework

Database: SQLite (development), PostgreSQL (planned for production)

Version Control: Git & GitHub

## Project Structure

arcade-backend/
├── backend/
│   ├── accounts/     # Custom user model & authentication
│   ├── courses/      # Course management application
│   ├── groups/       # User roles and group management
│   ├── config/       # Project settings and configuration
│   ├── templates/    # HTML templates
│   ├── db.sqlite3
│   └── manage.py
│
├── docs/             # Project documentation
├── README.md
└── requirements.txt

## Project Status

This project is under active development.
Some features are still in progress, and minor bugs may be present. These are expected as part of the development lifecycle.
