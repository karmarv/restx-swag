# REST Webservices
A Flask RESTX API with Swagger, JWT and SQLAlchemy integration

#### Environment
- Setup the requisite package on OS - Refer [README.ENV.md](./README.ENV.md#os-packages)
- Setup docker services - Refer [README.ENV.md](./README.ENV.md#docker-services)
- Clone the current codebase `git clone https://github.com/karmarv/restx-swag.git && cd restx-swag`
- Install pre-requisite packages -  `pip install -r requirements.txt`

#### Services
- Server configuration in [.flaskenv](./.flaskenv) and [config.py](./src/rest/services/config.py) file
- **(A.) Start Flask API**: `bash deploy_api.bash`
    - (1.) Secured API instance at http://127.0.0.1:5000/api/v1
    - (2.) Unsecured backend Job services at http://127.0.0.1:5001/api/v1
  - *Stop or Shutdown*: `bash deploy_api.bash stop`
      - Shutdown all flask instances on this server
- **(B.) Start Worker Processes**: `bash deploy_worker.bash 1`

## 1. App Webservice - [./src/rest/](./src/rest/)
Check the secured API instance at http://127.0.0.1:5000/api/v1
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
- Swagger UI based access
    - Documentation UI for webservices
        - [![Swagger UI](./data/assets/swagger-screenshot-jwt.png)](./data/assets/swagger-screenshot-jwt.png?raw=true "Swagger UI")

    - **Authorization**: Login and obtain the Bearer token to be filled in `Authorize` field on right top swagger documentation
        - [![Auth](./data/assets/swagger-auth-bearer-jwt.png)](./data/assets/swagger-auth-bearer-jwt.png?raw=true "Swagger UI")
    - Access the protected API from the test interface 
        - [![Auth](./data/assets/swagger-auth-access.png)](./data/assets/swagger-auth-access.png?raw=true "Swagger UI")


## 2. Job/Analytics Webservice - [./src/job/](./src/job/)
Check the unsecured backend Job services at http://127.0.0.1:5001/api/v1

- Job management services [IN-PROGRESS]
    - List all jobs: `curl -X 'GET' 'http://127.0.0.1:5001/api/v1/jobs/async' -H 'accept: application/json'`
        ```log
        [{"id": "job11", "job": {"name": "build an API", "type": "MBSP", "data": null}}, {"id": "job22", "job": {"name": "?????", "type": "Count", "data": "http://1.bp.blogspot.com/--M8WrSToFoo/VTVRut6u-2I/AAAAAAAAB8o/dVHTtpXitSs/s1600/URL.png"}}, {"id": "task3", "job": {"name": "profit!", "type": "Count", "data": null}}]
        ```

- Swagger UI based access
    - Documentation UI for Job management services
        - [![Swagger UI](./data/assets/swagger-jobs-services.png)](./data/assets/swagger-obs-services.png?raw=true "Swagger UI")

---

> References
- [Flask-RESTPlus & SwaggerUI](https://flask-restplus.readthedocs.io/en/stable/) documentation for more details
- [Flask Restx JWT authentication](https://github.com/blohinn/flask-restplus-full-todo-example-with-jwt/blob/develop/app/v1/resources/auth.py)
- These datasets can be consumed by [Highcharts](https://www.highcharts.com/demo) or any other application.
- A simple Redis Task queue https://realpython.com/flask-by-example-implementing-a-redis-task-queue/
