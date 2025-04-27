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
    X = emails_bow.drop('is_spam', axis='columns')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=args.test_ratio, random_state=args.seed, stratify=y)
    print(f'Training emails: {len(X_train)}')
    print(f'Testing emails: {len(X_test)}')

    print('Fitting model...')
    model = MultinomialNB()
    model.fit(X_train, y_train)

    print('Testing model...')
    y_pred_proba = model.predict_proba(X_test)[:, -1]
    y_pred = (y_pred_proba >= args.threshold).astype(int)
    print(f'Accuracy: {accuracy_score(y_test, y_pred)}')

    output_dir = args.output_dir
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    print('Saving model...')
    # see https://scikit-learn.org/stable/model_persistence.html
    model_pkl_pth = os.path.join(output_dir, 'mnb.pkl')
    with open(model_pkl_pth, 'wb') as f:
        dump(model, f, protocol=5)

    if args.output_db:
        print(f'Saving to SQLite database {os.path.abspath(args.output_db)}')
        db_conn = sqlite3.connect(args.output_db, detect_types=sqlite3.PARSE_DECLTYPES)
        db_conn.row_factory = sqlite3.Row
        cursor = db_conn.cursor()
        created_at = int(datetime.now(tz=timezone.utc).timestamp())
        cursor = cursor.execute(
            'INSERT INTO models (created_at,typ,threshold,path_to) VALUES (?,?,?,?)',
            (created_at, 'mnb', args.threshold, os.path.abspath(model_pkl_pth))
            )
        db_conn.commit()
        cursor.close()
        db_conn.close()

if __name__ == '__main__':
    parser = get_args_parser()
    args = parser.parse_args()
    main(args)