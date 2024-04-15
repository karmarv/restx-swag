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

These datasets can be consumed by [Highcharts](https://www.highcharts.com/demo) or any other application. 

> Swagger UI

[![Swagger UI](./data/swagger-screenshot.png)](./data/swagger-screenshot.png?raw=true "Swagger UI")