# Secure File Upload and Sharing Service

A full-stack web application built with **FastAPI**, **MongoDB**, and **HTML/CSS/JavaScript** that allows users to upload, share, delete, and manage files with support for public and private visibility. Users can register, log in, upload files, toggle file visibility (public/private), and share files with other users.

## Features

- User registration and login with JWT authentication
- Upload files with option to mark as public or private
- View your uploaded files with search functionality
- File access is strictly scoped to owners or shared users
- Public files can be downloaded without authentication
- Download, delete, and share files with other registered users
- Public Notes Board displaying all public files from all users
- Toggle file visibility between public and private
- Async backend using FastAPI and Motor (async MongoDB driver)
- Frontend with vanilla JavaScript and HTML

## Technologies Used

- Backend: FastAPI, MongoDB, Uvicorn, Motor (Async MongoDB driver), JWT
- Frontend: HTML/CSS/JavaScript

## Requirements

- Python 3.10+
- MongoDB server running locally or remotely
- See `requirements.txt` for full dependency list
- Project done using WSL2, can be used in Windows by modifying the commands

## Installation

1. Clone the repository

   ```bash
   git clone https://github.com/yourusername/secure-file-upload-and-sharing-service.git
   cd secure-file-upload-and-sharing-service

2. Create and activate a virtual environment

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies

   ```bash
   pip install -r requirements.txt

4. Configure environment variables
   Create a .env file in the project root and add to your configuration

5. Start MongoDB in another terminal using your local mongodb_data folder as the database path (can use different folders if you wish)

   ```bash
   mongod --dbpath ./mongodb_data

6. Start the FastAPI server with Uvicorn, then open in your browser (http://localhost:8000)
   
   ```bash
   uvicorn app.main:app --reload

## Usage
- Register a new user or login with existing credentials
- Upload files via the dashboard, choose if you want it to be private or public
- View all the files that you have uploaded (you can't see other people's files)
- See all public files on the Public Notes Board

## License
This project is licensed under the MIT License
   

