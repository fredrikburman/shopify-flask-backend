What is this stuff?
===================
This is a Flask/Python boilerplate Shopify backend app that you can use to kick start the development of your next Shopify App. Checkout [this blog post](https://www.tigersandtacos.dev/posts/create-a-shopify-backend-service-in-python-flask/) for more information on what it does and how you can get it up and running.

The features:
- Handle app installs from merchants
- Subscribe and act on webhooks (especially the order/paid hook), each order triggers a usage charge on the merchants account.
- Endpoint to receive merchant profile updates from your Shopify app
- A starter for the Shopify admin page
- Database migrations
- Unit tests
- Setup recurring and usage charge billing for your app (coming soon)
- Examples for how to interact with other services (coming soon)


## Installation
The app is dockerized and listening to port 5000, on Mac / Linux, to launch the service simply type `make run`

## Create the database 
When you run the service the database should be created in the first run, if not execute the following commands.

First connect to the docker container
`docker exec -it <name of taco-api container> bash`

Then initialize the database models and apply the migrations
`flask db init`

`flask db migrate -m "Initial migration."`

`flask db upgrade`

## Launching the service 
Navigate to the backend directory of the application and execute `make run`

## Running tests
All unit tests are located in the tests directory, to run them simply navigate to the backend 
directory of the application and execute: `make test`

## For more details
Checkout the blog posts over at [Tigers and Tacos](https://tigersandtacos.dev)
