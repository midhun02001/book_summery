from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
import heapq  
import re
import nltk
nltk.download('punkt')
nltk.download('stopwords')

stemmer = PorterStemmer()

class Summarizer(object):
    def __init__(self, text):
        self.__text        = text
        self.__stop_words  = stopwords.words('english')
        self.__sentence    = sent_tokenize(text)
        self.__f_text      = self.create_formatted_text()
        self.__word_freq   = self.calc_word_frequencies()

    def get_length(self):  # Fixed typo here
        return len(self.__sentence)

    def create_formatted_text(self):
        '''
            Removes digits, spaces, and special symbols from sentences
            :return: list of formatted text tokenized as words
        '''
        formatted_article_text = re.sub(r'\[[0-9]*\]', ' ', self.__text)            # Remove digits 
        formatted_article_text = re.sub('[^a-zA-Z]', ' ', formatted_article_text)  # Remove special symbols
        formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)        # Remove extra spaces
        return formatted_article_text.split(' ')

    def calc_word_frequencies(self):
        '''
            Calculates weighted word frequencies
            :return: dict of weighted word frequencies
        '''
        word_frequencies = {}
        for word in self.__f_text:
            word = word.lower()
            if word not in self.__stop_words:
                if word in word_frequencies:
                    word_frequencies[word] += 1
                else:
                    word_frequencies[word] = 1

        # Calculate weighted frequencies
        max_frequency = max(word_frequencies.values(), default=1)  # Prevent division by zero
        for word in word_frequencies.keys():
            word_frequencies[word] = word_frequencies[word] / max_frequency  # Adjusted to be a fraction

        return word_frequencies

    def get_summary(self, number_of_sentences=5):
        '''
            Generates summary based on weighted word frequencies
            :param number_of_sentences: total number of sentences to return in summary
            :return: string of summary
        '''
        sentence_value = {}
        for sentence in self.__sentence:
            for word in self.__word_freq.keys():
                if word in word_tokenize(sentence.lower()):
                    if sentence in sentence_value:
                        sentence_value[sentence] += self.__word_freq.get(word)
                    else:
                        sentence_value[sentence] = self.__word_freq.get(word, 0)
        
        summary_sentences = heapq.nlargest(number_of_sentences, sentence_value, key=sentence_value.get)
        summary = ' '.join(summary_sentences)
        return summary

if __name__ == '__main__':
    summarizer = Summarizer('So, keep working. Keep striving. Never give up. Fall down seven times, get up eight. Ease is a greater threat to progress than hardship. So, keep moving, keep growing, keep learning. See you at work.')
    print('Summary:', summarizer.get_summary(4)) 
