'''
Spam email classification API endpoints
'''

API_VERSION = 1

from flask import Blueprint, jsonify, make_response

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/version', methods=['GET'])
def version():
    '''
    Gets the current API version

    Returns a JSON response like so:

    `{version: version_num}`
    '''

    res = make_response(jsonify({'version':API_VERSION}))

    return res

@bp.route('/classify', methods=['POST'])
def classify():
    res = make_response(jsonify({'spam':1}))
    
    return res