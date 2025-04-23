import os
from flask import Flask
from wise_parakeet.app import database
from dotenv import load_dotenv

load_dotenv() # load configuration environment variables

def create_app():
    '''
    Create an instance of the Flask app
    '''
    
    app = Flask(__name__)
    app.static_url_path = os.path.join(app.root_path, 'static') # point to custom static folder

    app.config['DATABASE'] = os.path.join(
        app.root_path, 
        os.getenv('DATABASE')
        )
    
    with app.app_context():
        schema = open(os.path.join(app.root_path, os.getenv('DATABASE_SCHEMA'))).read()
        database.init_db(schema)

    @app.route('/')
    def index():
        res = app.send_static_file('html/index.html') # see https://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
        
        return res
    
    @app.route('/about')
    def about():
        res = app.send_static_file('html/about.html')

        return res
    
    from .routes import api
    app.register_blueprint(api.bp)
    
    return app