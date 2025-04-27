import argparse
from wise_parakeet.ai import utils

def get_args_parser():
    parser = argparse.ArgumentParser(
        prog='Enron Spam Emails Dataset Bag of Words Generator',
        description='Constructs a Bag of Words (BoW) based on Enron spam emails dataset. See https://github.com/MWiechmann/enron_spam_data for more details about dataset',
        add_help=True, 
    )

    parser.add_argument(
        'emails_dataset',
        metavar='emails-dataset',
        type=str,
        help='Filepath to CSV of spam emails data. See the link above for download and expected format.',
    )

    parser.add_argument(
        '--spam-keep-ratio',
        type=float,
        default=1.0,
        help='Ratio of spam emails to keep (randomly chosen). 0 <= ratio <= 1',
    )

    parser.add_argument(
        '--ham-keep-ratio',
        type=float,
        default=1.0,
        help='Ratio of non-spam emails to keep (randomly chosen). 0 <= ratio <= 1',
    )

    parser.add_argument(
        '--min-word-len', 
        type=int, 
        default=2, 
        help='Minimum length of words to include in vocabulary',
        )
    
    parser.add_argument(
        '--max-vocab-len',
        type=int,
        default=5000,
        help='Number of words to include in vocabulary',
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=777,
        help='Controls randomness',
    )

    parser.add_argument(
        '--get-nltk-punkt',
        action='store_true',
        help='If specified, download NLTK punkt_tab tokenizer',
    )
    
    parser.add_argument(
        '--get-nltk-stopwords',
        action='store_true',
        help='If specified, download NLTK stop words corpus',
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='If specified, display verbose outputs'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='',
        help='Filepath to directory to save results to',
    )

    return parser

def main(args:argparse.Namespace):
    import os
    import nltk
    import pandas as pd
    from nltk.corpus import stopwords

    if args.get_nltk_punkt:
        nltk.download('punkt_tab')
    if args.get_nltk_stopwords:
        nltk.download('stopwords')

    stop_words = set(stopwords.words('english'))

    emails = pd.read_csv(args.emails_dataset).groupby('Spam/Ham')
    spam_emails = utils.get_random_rows(emails.get_group('spam'), args.spam_keep_ratio, seed=args.seed)
    ham_emails = utils.get_random_rows(emails.get_group('ham'), args.ham_keep_ratio, seed=args.seed)
    emails = pd.concat([spam_emails, ham_emails], axis=0).reset_index(drop=True)

    enron_bow = utils.EnronBagOfWords(
        emails, 
        stop_words=stop_words, 
        language='english', 
        min_word_len=args.min_word_len,
        max_vocab_len=args.max_vocab_len, 
        verbose=args.verbose,
        )
    
    output_dir = args.output_dir
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    enron_bow.bow.to_csv(os.path.join(output_dir, 'enron_bow.csv'))

if __name__ == '__main__':
    parser = get_args_parser()
    args = parser.parse_args()
    main(args)