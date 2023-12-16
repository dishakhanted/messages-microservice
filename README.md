# Messages Microservice

This is a project that implements a REST web service for messages using FastAPI and Python. The project allows users to send and receive messages, as well as view their profile information.

## Features

- FastAPI framework for creating REST web service endpoints
- Jinja2 templates for rendering HTML pages
- Pydantic models for validating and serializing data
- PostgreSQL database for storing user and message data
- Uvicorn server for running the web service
- Cloud SQL for hosting the database in the cloud

## Endpoints

The project provides the following endpoints:

- `/` : Redirects to the static index page
- `/api` : Redirects to the FastAPI documentation
- `/profile/{userID}` : Renders an HTML page with the profile information of the user with the given userID
- `/api/users` : Returns a list of users that match the given query parameters
- `/api/users/{userID}` : Returns a user based on userID
- `/api/users/newUser` : Creates a new user
- `/api/messages` : Returns a list of messages that match the given query parameters
- `/api/messages/{userID}` : Returns a list of messages sent or received by the user with the given userID
- `/api/messages/{userID}/newMessage` : Creates a new message from the user with the given userID to another user
- `/api/messages/{userID}/{messageThreadID}` : Returns a list of messages in the message thread with the given messageThreadID
- `/api/messages/newMessage` : Updates or deletes an existing message

## Installation

To run the project locally, you need to have Python 3.8 or higher installed. You also need to have PostgreSQL installed and create a database named `message` with a user named `message` and a password `message`. Alternatively, you can change the database configuration in the code to suit your preferences.

To install the required dependencies, run the following command in the project directory:

```bash
pip install -r requirements.txt
```
To run the web service, run the following command in the project directory:

```
python3 main.py
```

To run the project in the cloud, you need to have a Google Cloud Platform account and create a Cloud SQL instance with a PostgreSQL database named `message` with a user named `message` and a password `message`. You also need to create an App Engine service and deploy the project using app.yaml provided in the project directory.

## License

This project is licensed under the MIT License - see the LICENSE file for details.