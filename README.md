# wise-parakeet
Basic web app for spam email classification.

## About
Uses a scikit-learn Multinomial Naive Bayes classifier trained on Enron spam emails data to classify if emails are spam or not. Unseen emails can be submitted to the model for classification via web app.

## Setup
### 1. Get the Data
Go to https://github.com/MWiechmann/enron_spam_data to download the necessary dataset. Be sure to extract the files after downloading and take note of the file location.

### 2. Get the Code
1. Clone the repository and change into its directory
2. Run `poetry install` to install necessary dependenices. Be sure to install Poetry first.

### 3. Create Bag of Words from Emails
See the `get_enron_bow.py` script in `wise_parakeet/ai`. Run `python src/wise_parakeet/ai/get_enron_bow.py -h` from the terminal to see the script's optional and positional arguments. The output will be a CSV file - be sure to note its location on disk.

### 4. Launch the Flask App
1. Run `flask --app src/wise_parakeet/app/run run --debug` to launch the Flask app in debug mode. **Do not use this in a production environment!**
2. Open your browser and go to `localhost:5000` or `127.0.0.1:5000`. You should see the home page :)

Note - this will create a SQLite database on disk. See `.env` file for configuration details.

### 5. Train Multinomial Naive Bayes Classifier
See the `train.py` script in `wise_parakeet/ai`. Run `python src/wise_parakeet/ai/train.py -h` from the terminal to see the script's optional and positional arguments. Use the BoW CSV file generated in step 3. For the app to work properly, specify the `--output-dir` and `--output-db` optional arguments, and point `--output-db` to the SQLite database file generated in step 4.

### 6. Enter Email Data
Open your browser and go to the link in step 4. Enter the email subject and content in the corresponding inputs. If there's an error, an alert with pop up. Check the Flask debug logs in your terminal to see where and why things went wrong.
