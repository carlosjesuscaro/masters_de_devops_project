# Instructions

## Run the application locally

* From the project's root folder:

  * `source .venv/bin/activate`
  * `pip install -r requirements.txt`
* Running the application from `./jokes_api/src/`

  * `docker run --name local-mysql -e MYSQL_ROOT_PASSWORD=mysecretpassword -e MYSQL_DATABASE=jokedb -p 3306:3306 -d mysql:8`
  * `uvicorn main:app --reload`
* Using the application

  * [Browser - Main Page] - http://localhost:8000/
  * [Browser - Checking application health] - http://localhost:8000/health
  * [Terminal] - Pulling jokes from https://official-joke-api.appspot.com/random_joke by using the application `curl -X POST "http://localhost:8000/jokes/collect?count=5"`
  * [Terminal] - Pulling jokes that have been stored in the database `curl -X GET http://localhost:8000/jokes | jq`
* Running the test from `./jokes_api/src/tests/`

  * `pytest -v`


## IaC: Vagrant & Ansible


## Kubernetes (Minikube)
