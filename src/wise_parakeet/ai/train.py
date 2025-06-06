import argparse
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def get_args_parser():
    parser = argparse.ArgumentParser(
        prog='Multinomial Naive Bayes Spam Email Classifier Training Script',
        description='Trains an MNB classifier on a spam emails BoW dataset' ,
        add_help=True, 
    )

    parser.add_argument(
        'emails_dataset',
        metavar='emails-dataset',
        type=str,
        help='Filepath to CSV of spam emails data. Expects integer feature counts, a binary label column called "is_spam", and a numerical ID column called "email_id".',
    ) 

    parser.add_argument(
        '--test-ratio',
        type=float,
        default=0.4,
        help='Ratio of data to set aside for testing',
    )

    parser.add_argument(
        '--threshold',
        type=float,
        default=0.5,
        help='Probability threshold for classification. Anything >= threshold will be classified as spam - anything < as ham.'
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=777,
        help='Controls randomness',
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='',
        help='Filepath to directory to save results to',
    )

    parser.add_argument(
        '--output-db',
        type=str,
        default='',
        help='Filepath to SQLite database to save model info to if loading from a downstream app. See wise_parakeet/app/data/schema.sql for expected database schema.',
    )

    return parser

def main(args:argparse.Namespace):
    import os
    import sqlite3
    from datetime import datetime, timezone
    from pickle import dump

    print('Loading emails...')
    emails_bow = pd.read_csv(args.emails_dataset)
    print(f'Number of emails: {len(emails_bow)}')

    y = emails_bow['is_spam']
    X = emails_bow.drop(['email_id','is_spam'], axis='columns')
    X_train, X_test, y_train, y_test = train_test_split(
        X.to_numpy(), # see https://stackoverflow.com/questions/69326639/sklearn-warning-valid-feature-names-in-version-1-0
        y.to_numpy(), 
        test_size=args.test_ratio, 
        random_state=args.seed, 
        stratify=y,
        )
    print(f'Training emails: {len(X_train)}')
    print(f'Testing emails: {len(X_test)}')

    print('Fitting model...')
    model = MultinomialNB()
    model.fit(X_train, y_train)

    print('Testing model...')
    y_pred_proba = model.predict_proba(X_test)[:, -1]
    y_pred = (y_pred_proba >= args.threshold).astype(int)
    print(f'Accuracy: {accuracy_score(y_test, y_pred)}')

    created_at = int(datetime.now(tz=timezone.utc).timestamp())
    output_dir = os.path.join(args.output_dir, str(created_at))
    os.makedirs(output_dir, exist_ok=True)

    print('Saving model...')
    # see https://scikit-learn.org/stable/model_persistence.html
    model_pkl_pth = os.path.join(output_dir, 'mnb.pkl')
    with open(model_pkl_pth, 'wb') as f:
        dump(model, f, protocol=5)

    print('Saving vocab...')
    vocab_pkl_pth = os.path.join(output_dir, 'vocab.pkl')
    with open(vocab_pkl_pth, 'wb') as f:
        dump({col:None for col in X.columns}, f, protocol=5) # use dict to maintain order

    if args.output_db:
        print(f'Saving to SQLite database {os.path.abspath(args.output_db)}')
        db_conn = sqlite3.connect(args.output_db, detect_types=sqlite3.PARSE_DECLTYPES)
        db_conn.row_factory = sqlite3.Row
        cursor = db_conn.cursor()

        # save model data
        cursor = cursor.execute(
            'INSERT INTO models (created_at,typ,threshold,pkl_pth) VALUES (?,?,?,?)',
            (created_at, 'mnb', args.threshold, os.path.abspath(model_pkl_pth))
        )
        db_conn.commit()
        model_id = cursor.lastrowid

        # save vocab data
        # TODO: ideally we could just get this from the model itself after unpickling (no need for more tables then) - is that possible?
        cursor = cursor.execute(
            'INSERT INTO vocabs (created_at,pkl_pth) VALUES (?,?)',
            (created_at, os.path.abspath(vocab_pkl_pth)),
        )
        db_conn.commit()
        vocab_id = cursor.lastrowid

        # junction table
        cursor = cursor.execute(
            'INSERT INTO model_vocabs (model_id,vocab_id) VALUES (?,?)',
            (model_id, vocab_id)
        )
        db_conn.commit()
        
        # terminate connection to sqlite database
        cursor.close()
        db_conn.close()

if __name__ == '__main__':
    parser = get_args_parser()
    args = parser.parse_args()
    main(args)