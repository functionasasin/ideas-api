# Ideas API

## Description

This API allows users to submit ideas, view ideas, and upvote ideas. Admins can register, log in, and perform administrative actions such as deleting ideas. The API uses JWT authentication for admin routes.

## Installation

Steps to set up the API:

1. Clone this repository:

    ```bash
    git clone https://github.com/functionasasin/ideas-api.git
    ```

2. Navigate into the project directory:

    ```bash
    cd ideas-api
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up your .env file, it should look like this or you may change the variable names:

    ```env
    SECRET_KEY=<your_secret_key>
    DATABASE_URI=<your_database_uri>
    ```

5. In the terminal, run the app:

    ```bash
    uvicorn src.main:app --reload
    ```

## API Usage

### Wiki
