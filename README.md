# wise-parakeet
Basic web app for spam email classification.

## Setup
1. Clone the repository and change into its directory
2. Run `poetry install` to install necessary dependenices. Be sure to install Poetry first.
3. Run `flask --app src/wise_parakeet/app/run run --debug` to launch the Flask app in debug mode. **Do not use this in a production environment!**
4. Open your browser and go to `localhost:5000` or `127.0.0.1:5000`. You should see the home page :)