# Instructions

## Run the application locally 
* `source .venv/bin/activate`
* `pip install -r requirements.txt`
* 
* `uvicorn main:app --reload`
* `docker run --name local-mysql -e MYSQL_ROOT_PASSWORD=mysecretpassword -e MYSQL_DATABASE=jokedb -p 3306:3306 -d mysql:8


## IaC
* `vagrant up --provider=virtualbox`