# Initializing the repository
1. Install dependencies: `poetry install`
2. Copy and populate the `.env` file: `cp .env.example .env`

# Running the server
You can start the server locally using
`poetry run python manage.py runserver`

In case certain environment variables are not set, export them to your terminal session beforehand.

# Running via Docker
`docker compose build && docker compose run`
This will build the docker image and run the container. It will use the environment variables
defined in the `.env` file.

# API endpoints
1. Request faucet funding:
`curl --location 'http://127.0.0.1:8000/faucet/fund' --form 'address="<YOUR_WALLET_ADDRESS>"'`

2. Get faucet stats:
`curl --location 'http://127.0.0.1:8000/faucet/stats'`