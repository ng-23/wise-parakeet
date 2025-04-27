import sys
import os
import pandas as pd
from string import punctuation
from nltk.tokenize import word_tokenize
from tqdm import tqdm

def get_vocab_word_counts(txt:str, vocab:set[str], language:str='english'):
    '''
    Gets the count of each vocabulary word in `vocab` that occurs in `txt`
    '''

    words = word_tokenize(txt, language=language)

    counts = {vocab_word: 0 for vocab_word in vocab}

    for word in words:
        if word in vocab:
            if word in counts:
                counts[word] += 1
            else:
                counts[word] = 1

    return counts

def get_random_rows(df:pd.DataFrame, ratio:float, seed:int=777):
    if ratio < 0 or ratio > 1:
        raise ValueError('Ratio must be between 0 and 1, inclusive')
    
    return df.sample(frac=ratio, random_state=seed).reset_index(drop=True)

class EnronBagOfWords():
    '''
    Constructs a Bag of Words (BoW) based on Enron spam emails dataset

    See https://github.com/MWiechmann/enron_spam_data for more details about dataset
    '''

    def __init__(self, emails:pd.DataFrame, stop_words:set[str]|None=None, language:str='english', min_word_len:int=2, max_vocab_len:int=5000, verbose=False):
        # configuration attributes
        self.stop_words = stop_words
        self.language = language
        self.min_word_len = min_word_len
        self.max_vocab_len = max_vocab_len
        self.verbose = verbose

        # data attributes
        self.emails = self._preprocessing(emails)
        self.vocab = self._build_vocab()
        self.bow = self._build_bow()

    def _nlp_pipeline(self, emails):
        res = []
        
        for content in tqdm(emails, desc='Preprocessing', total=len(emails)):
            content = content.lower()

            tokens = word_tokenize(content)
            tokens = [token for token in tokens if not token.isnumeric()]
            if self.stop_words is not None:
                tokens = [token for token in tokens if token not in self.stop_words]

            content = ' '.join(tokens)

            content = content.translate(str.maketrans('', '', punctuation)) # see https://stackoverflow.com/questions/3939361/remove-specific-characters-from-a-string-in-python/47030484#47030484

            res.append(content)

        return res

    def _preprocessing(self, emails:pd.DataFrame):
        '''
        Performs basic NLP preprocessing on emails
        - drops unnecessary columns
        - combines subject + content
        - converts all words to lowercase
        - removes stop words (the, a, an, etc.)
        - removes all numbers
        - removes all punctuation (?, !, etc.)
        '''

        temp = sys.stdout
        if not self.verbose:
            sys.stdout = open(os.devnull, 'w')

        # drop unnecessary columns
        emails.drop('Message ID', axis=1, inplace=True)
        emails.drop('Date', axis=1, inplace=True)

        # replace null subject/contents with empty string
        emails = emails.fillna('')

        # combine email subject + content
        # see https://stackoverflow.com/questions/19377969/combine-two-columns-of-text-in-pandas-dataframe
        emails['Message'] = emails['Subject'] + ' ' + emails['Message']
        emails.drop('Subject', axis=1, inplace=True)

        emails['Message'] = self._nlp_pipeline(emails['Message'])

        sys.stdout = temp

        return emails

    def _build_vocab(self) -> set[str]:
        '''
        Builds a (unique) vocabulary of words across all emails
        '''

        temp = sys.stdout
        if not self.verbose:
            sys.stdout = open(os.devnull, 'w')

        vocab = set()
        
        contents = self.emails['Message']
        for content in tqdm(contents, desc='Building vocabulary'):
            words = word_tokenize(content, language=self.language)
            for word in words:
                if len(vocab) >= self.max_vocab_len:
                    break

                if word not in vocab and len(word) > self.min_word_len:
                    vocab.add(word)

        print(f'Words in vocabulary: {len(vocab)}')

        sys.stdout = temp

        return vocab

    def _build_bow(self):
        '''
        Creates BoW where each numerical email ID is mapped to a vector `v`
        where `v[i]` is the count for the ith word in overall vocabulary
        '''

        temp = sys.stdout
        if not self.verbose:
            sys.stdout = open(os.devnull, 'w')

        bow = {'email_id': [], 'is_spam':[]}

        for word in self.vocab:
            bow[word] = []

        contents = self.emails['Message']
        for i, content in tqdm(enumerate(contents), desc='Building BoW', total=len(contents)):
            bow['email_id'].append(i)
            bow['is_spam'].append(1 if self.emails.loc[(self.emails['Message'] == content)]['Spam/Ham'].values[0] == 'spam' else 0)
            word_counts = get_vocab_word_counts(content, self.vocab, language=self.language)
            for word, count in word_counts.items():
                bow[word].append(count)

        df = pd.DataFrame.from_dict(bow)
        df.set_index('email_id', inplace=True)

        sys.stdout = temp

        return df    
    