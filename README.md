# BLOG API

An API developed using FastAPI and MongoDB Atlas

## FILES AND FOLDERS

### templates

Directory to store email templates.

### routes

Directory for storing routes to all models used

### .env

Used to store sensitive data such as passwords and configurations to act as a layeer of abstraction hence improving security

### main.py

Main file for running FastAPI. Links all the routes

### dbconn.py

Creates a connection to MongoDB Atlas which is the main project DB

### utils.py

Contains functions to be reused by the different routes

1. Pagination

### models.py

Contains all the project models

### send_email.py

For sending emails such as for account activations.
