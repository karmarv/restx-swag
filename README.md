# RESTX-Swagger Application
Swagger enabled Flask RESTX web services template project

#### Environment Setup
- Installation via Miniconda v24.3.0 - https://docs.conda.io/projects/miniconda/en/latest/
    ```
    conda env remove -n restx
    conda create -n restx python=3.10
    conda activate restx
    ```
- Clone the current codebase `git clone https://github.com/karmarv/restx-swag.git && cd restx-swag`
- Install pre-requisite packages -  `pip install -r requirements.txt`
- Download additional data [TODO]

#### Flask Server 
- Server configuration in [.flaskenv](./.flaskenv) and [config.py](./src/rest/services/config.py) file
- *Launch Flask Server*: `cd src/rest && flask run`
    - App instance at http://127.0.0.1:5000/
- *Test*: `cd src/rest && pytest`
- *Data*: `./data/data_samples.csv`

#### Service URLs
Check the [Flask-RESTPlus & SwaggerUI](https://flask-restplus.readthedocs.io/en/stable/) documentation for more details
- Swagger Descriptor (http://localhost:5000/swagger.json)
- Secured data access workflow using JWT authentication
    - Register a user
        ```bash
        curl -X 'POST' 'http://127.0.0.1:5000/auth/register' -H 'Content-Type: application/json' -d '{ "username": "admin", "password": "Admin@12345"}'
        ```
        ```log
        {"id":2,"password_hash":"scrypt:32768:8:1$RCRIvF3Iuovw5yQ1$1ab8976a30feaeeb7a0e253ac80c8c81aee61d91764c51b52e2c54201750aa28f4cabd540c7de082ea20319eed51908c69bb6caf8db37844379efc65e7507aa4","refresh_tokens":[],"username":"admin"}
        ```
    - Login to obtain access token
        ```bash
        curl -X 'POST' 'http://127.0.0.1:5000/auth/login' -H 'Content-Type: application/json' -d '{ "username": "admin", "password": "Admin@12345" }'
        ```
        ```log
        {"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjIsImV4cCI6MTcxMzQzMTUyNiwiaWF0IjoxNzEzMzk1NTI2fQ.wUasFppUnKQrwbDacYOiadYlRHb8I09CMyrhEWUQHs4","refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjIsImV4cCI6MTcxNTk4NzUyNiwiaWF0IjoxNzEzMzk1NTI2fQ.bsoW1TcYr_gXjbjSuYImg7DD_RyL3kYMDc8ujeZE694"}
        ```
    - Access protected resources using token
        ```bash 
         curl -X 'GET' 'http://127.0.0.1:5000/auth/protected' -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjIsImV4cCI6MTcxMzQzMTUyNiwiaWF0IjoxNzEzMzk1NTI2fQ.wUasFppUnKQrwbDacYOiadYlRHb8I09CMyrhEWUQHs4"
        ```
        ```log
        {"level":"protected","uid":2}
        ```

These datasets can be consumed by [Highcharts](https://www.highcharts.com/demo) or any other application. 

> Swagger UI

[![Swagger UI](./data/swagger-screenshot.png)](./data/swagger-screenshot.png?raw=true "Swagger UI")