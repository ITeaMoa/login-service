# Django Authentication Service

This repository contains a Django-based authentication service that integrates with AWS Cognito for user management. It provides functionality for user signup, signin, and token management (including refresh tokens) using JSON Web Tokens (JWT).

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [License](#license)

## Features

- User signup with email, password, nickname, and full name.
- User signin with JWT authentication.
- Token refresh functionality using refresh tokens.
- Integration with AWS Cognito for secure user management.
- Simple and extendable Django framework.

## Requirements

- Python 3.6 or higher
- Django 3.2 or higher
- Boto3 (for AWS Cognito integration)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. **Create a virtual environment:**
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows use `venv\Scripts\activate`
  ```
  
3. **Install the required packages:**
  ```bash
  pip install -r requirements.txt
  ```

## Configuration
1. **Set up AWS Cognito:**
- Create a User Pool in AWS Cognito.
- Create an App Client in your User Pool (ensure to enable refresh token functionality).
- Note the User Pool ID and App Client ID.

2. **Environment Variables:** Create a `.env` file in the root directory of the project with the following content:

  ```
  AWS_REGION=your_aws_region
  AWS_CLIENT_ID=your_cognito_app_client_id
  Replace your_aws_region and your_cognito_app_client_id with your actual AWS settings.
  ```

3. **Database Migration:** Run the following command to set up your database:

  ```bash
  python manage.py migrate
  ```

## Usage
1. **Run the server:**

```bash
python manage.py runserver
```
2. **Access the API:** The server will be running at `http://127.0.0.1:8000/`. You can use tools like Postman to interact with the API.


## API Endpoints
- **Signup**
  - Endpoint: `/auth/signup/`
  - Method: POST
  - Request Body:
    ```json
    {
        "username": "your_username",
        "password": "your_password",
        "email": "your_email",
        "nickname": "your_nickname",
        "full_name": "Your Full Name"
    }
    ```
  
- **Signin**
  - Endpoint: `/auth/signin/`
  - Method: POST
  - Request Body:
    ```json
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```

- **Signup confirm**
  - Endpoint: `auth/verify`
  - Method: POST
  - Request Body:
    ```json
    {
        "user_name": "your_user_name",
        "verification_code": "your_verification_code"
    }
    ```

- **Token Refresh**
  - Endpoint: `/auth/refresh/`
  - Method: POST
  - Request Body:
    ```json
    {
        "refresh_token": "your_refresh_token"
    }
    ```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

This format should meet your requirements. Let me know if you need any further adjustments!



