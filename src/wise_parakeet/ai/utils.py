import sys
import os
import pandas as pd
from string import punctuation
from nltk.tokenize import word_tokenize

def remove_punctuation(txt:str):
    '''
    Removes all punctuation characters from `txt`
    '''

    return txt.translate(str.maketrans('', '', punctuation)) # see https://stackoverflow.com/questions/3939361/remove-specific-characters-from-a-string-in-python/47030484#47030484

def remove_stop_words(txt:str, stop_words:set[str], language:str='english'):
    '''
    Removes all stop words from `txt`
    '''

    words = word_tokenize(txt, language=language)
    return ' '.join([word for word in words if word not in stop_words])

def remove_numbers(txt:str, language:str='english'):
    '''
    Removes all numerical values from `txt`
    '''

    words = word_tokenize(txt, language=language)

    return ' '.join([word for word in words if not word.isnumeric()])

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

class EnronBagOfWords():
    '''
    Constructs a Bag of Words (BoW) based on Enron spam emails dataset

    See https://github.com/MWiechmann/enron_spam_data for more details about dataset
    '''

    def __init__(self, emails:pd.DataFrame, stop_words:set[str]|None=None, language:str='english', min_word_len:int=2, verbose=False):
        # configuration attributes
        self.stop_words = stop_words
        self.language = language
        self.min_word_len = min_word_len
        self.verbose = verbose

        # data attributes
        self.emails = self._preprocessing(emails)
        self.vocab = self._build_vocab()
        self.bow = self._build_bow()
        
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
        
        print('Preprocessing emails...')

        # drop unnecessary columns
        print('Dropping unnecessary columns...')
        emails.drop('Message ID', axis=1, inplace=True)
        emails.drop('Date', axis=1, inplace=True)

        # replace null subject/contents with empty string
        emails = emails.fillna('')

        # combine email subject + content
        # see https://stackoverflow.com/questions/19377969/combine-two-columns-of-text-in-pandas-dataframe
        print('Combining subject and content...')
        emails['Message'] = emails['Subject'] + ' ' + emails['Message']
        emails.drop('Subject', axis=1, inplace=True)

        # convert contents to lowercase
        print('Converting to lowercase...')
        emails['Message'] = emails['Message'].apply(lambda record: record.lower())

        # remove all stop words
        if self.stop_words is not None:
            print('Removing stop words...')
            emails['Message'] = emails['Message'].apply(lambda record: remove_stop_words(record, self.stop_words, language=self.language))

        # remove all numbers
        print('Removing numbers...')
        emails['Message'] = emails['Message'].apply(lambda record: remove_numbers(record, language=self.language))

        # remove all punctuation
        print('Removing punctuation...')
        emails['Message'] = emails['Message'].apply(lambda record: remove_punctuation(record))

        print('Finished preprocessing!')

        sys.stdout = temp

        return emails

    def _build_vocab(self) -> set[str]:
        '''
        Builds a (unique) vocabulary of words across all emails
        '''

        temp = sys.stdout
        if not self.verbose:
            sys.stdout = open(os.devnull, 'w')

        print('Building vocabulary...')

        vocab = set()
        
        contents = self.emails['Message']
        for content in contents:
            words = word_tokenize(content, language=self.language)
            vocab = vocab | set([word for word in words if len(word) > self.min_word_len])

        print('Finished building vocabulary!')

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

        print('Building BoW...')

        bow = {'email_id': []}

        # add word counts (features)
        for word in self.vocab:
            bow[word] = []

        contents = self.emails['Message']
        for i, content in enumerate(contents):
            bow['email_id'].append(i)
            word_counts = get_vocab_word_counts(content, self.vocab, language=self.language)
            for word, count in word_counts.items():
                bow[word].append(count)

        df = pd.DataFrame.from_dict(bow)
        df.set_index('email_id', inplace=True)
        df['spam'] = self.emails['Spam/Ham'].apply(lambda record: 1 if record == 'spam' else 0)

        print('Finished building BoW!')

        sys.stdout = temp

        return df

if __name__ == '__main__':
    import nltk
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
    #nltk.download('punkt_tab')
    #nltk.download('stopwords')

    emails = pd.read_csv('/home/noahg/COSC356/project3/wise-parakeet/src/wise_parakeet/ai/data/enron_spam_data.csv', nrows=3)
    enron_bow = EnronBagOfWords(emails, stop_words=stop_words, language='english', min_word_len=2, verbose=True)
    print(enron_bow.bow)