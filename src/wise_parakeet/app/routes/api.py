'''
Spam email classification API endpoints
'''

API_VERSION = 1

from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/version', methods=['GET'])
def version():
    '''
    Gets the current API version

    Returns a JSON response like so:

    `{version: version_num}`
    '''

    return {'version':API_VERSION}

@bp.route('/classify', methods=['POST'])
def classify():
    return {'spam':1}