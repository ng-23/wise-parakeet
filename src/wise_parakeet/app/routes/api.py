'''
Spam email classification API endpoints
'''

API_VERSION = 1

import numpy as np
from flask import Blueprint, request
from wise_parakeet.app import database
from wise_parakeet.ai import utils

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/version', methods=['GET'])
def version():
    '''
    Gets the current API version

    Returns a JSON response like so:

    `{version: version_num}`
    '''

    return {'version': API_VERSION}

@bp.route('/classify', methods=['POST'])
def classify():
    # connect to database
    db_conn = database.get_db_conn()
    cursor = db_conn.cursor()

    # load model from database
    cursor = cursor.execute('SELECT * FROM models ORDER BY created_at DESC')
    model_data = [dict(record) for record in cursor.fetchall()][0] # get the most recently trained model's data
    model = utils.load_from_pickle(model_data['pkl_pth'])

    # load vocab from database
    cursor = cursor.execute(
        '''
        SELECT * FROM model_vocabs 
        JOIN vocabs on vocabs.id = model_vocabs.vocab_id 
        WHERE model_vocabs.model_id = ?
        ''',
        (model_data['id'],)
    )
    vocab_data = dict(cursor.fetchone())
    vocab = utils.load_from_pickle(vocab_data['pkl_pth']) # should be a dict mapping word to none (so feature order is maintained)

    cursor.close()

    # get email data from json request body
    email_data = request.json

    # process email data
    if 'subject' in email_data and 'content' in email_data:
        email = (email_data['subject'] + ' ' + email_data['content']).lower()
        vocab_word_counts = utils.get_vocab_word_counts(email, vocab.keys(), language='english')

        y_pred_proba = model.predict_proba(np.array(list(vocab_word_counts.values())).reshape(1,-1))[:, -1] # see https://stackoverflow.com/questions/56717542/how-to-make-prediction-with-single-sample-in-sklearn-model-predict
        y_pred = (y_pred_proba >= model_data['threshold']).astype(int)
        
        return {'spam': int(y_pred[0])}

    else:
        return {'msg': 'Error - missing subject and/or content in JSON body'}, 400
    