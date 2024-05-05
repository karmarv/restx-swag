# A Flask RESTX API with Swagger, JWT and SQLAlchemy integration

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

#### Webservices Server 
- Server configuration in [.flaskenv](./.flaskenv) and [config.py](./src/rest/services/config.py) file
- *Start Flask API*: `bash deploy_api.bash`
    - Secured API instance at http://127.0.0.1:5000/api/v1
    - Unsecured backend Job services at http://127.0.0.1:5001/api/v1
- *Stop or Shutdown*: `bash deploy_api.bash stop`
    - Shutdown all flask instances on this server

#### Service URLs
Check the [Flask-RESTPlus & SwaggerUI](https://flask-restplus.readthedocs.io/en/stable/) documentation for more details
- Swagger Descriptor (http://localhost:5000/api/v1/swagger.json)
- Secured data access workflow using JWT authentication
    - Register a user
        ```bash
        curl -X 'POST' 'http://127.0.0.1:5000/api/v1/auth/register' -H 'Content-Type: application/json' -d '{ "username": "admin", "password": "Admin@123"}'
        ```
        ```log
        {"id":4,"password_hash":"[Hidden]","refresh_tokens":[],"username":"admin"}
        ```
    - Login to obtain access token
        ```bash
        curl -X 'POST' 'http://127.0.0.1:5000/api/v1/auth/login' -H 'Content-Type: application/json' -d '{ "username": "admin", "password": "Admin@123" }'
        ```
        ```log
        {"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjQsImV4cCI6MTcxNDk2NTM1NiwiaWF0IjoxNzE0OTI5MzU2fQ.XNJ2UHbDGsLp5QyR5-Wm61nlWXYNXov4Pfrfmph-Z9o","refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjQsImV4cCI6MTcxNzUyMTM1NiwiaWF0IjoxNzE0OTI5MzU2fQ.xQ7UYjPPEDdLY-F5V_9kQoPcohYmDMk_VSEt-0A8uy8"}
        ```
    - Access protected resources using token
        ```bash 
        curl -X 'GET' 'http://127.0.0.1:5000/api/v1/auth/protected' -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjQsImV4cCI6MTcxNDk2NTM1NiwiaWF0IjoxNzE0OTI5MzU2fQ.XNJ2UHbDGsLp5QyR5-Wm61nlWXYNXov4Pfrfmph-Z9o"
        ```
        ```log
        {"level":"protected","uid":4}
        ```

These datasets can be consumed by [Highcharts](https://www.highcharts.com/demo) or any other application. 

---

## Swagger
- Documentation UI for webservices
    - [![Swagger UI](./data/assets/swagger-screenshot-jwt.png)](./data/assets/swagger-screenshot-jwt.png?raw=true "Swagger UI")

- **Authorization**: Login and obtain the Bearer token to be filled in `Authorize` field on right top swagger documentation
    - [![Authh](./data/assets/swagger-auth-bearer-jwt.png)](./data/assets/swagger-auth-bearer-jwt.png?raw=true "Swagger UI")
- Access the protected API from the test interface 
    - [![Authh](./data/assets/swagger-auth-access.png)](./data/assets/swagger-auth-access.png?raw=true "Swagger UI")


---

> Reference: https://github.com/blohinn/flask-restplus-full-todo-example-with-jwt/blob/develop/app/v1/resources/auth.py