'''
stemmer.py
@author: Eric Walker
CS 322 Fall '15 Carleton College
Porter Stemmer implementation
(read more at http://tartarus.org/~martin/PorterStemmer/def.txt)
'''
import re

vowels=r'[aeiou]+'
consonants=r'[b-df-hj-np-tv-z]+'

'''
measure gives the 'measure' of a word, rather the number of vowel consonant clusters
@param word: the word to be measured
@return: the measure of the word as defined in the paper above
'''
def measure(word):
    key = word
    #convert all y's that are preceded by a consonant with an e for counting purposes
    key = re.sub(r'(?P<c>[b-df-hj-np-tv-xz])y', r'\g<c>e', key)
    key = re.sub(vowels, 'V', key)
    key = re.sub(consonants, 'C', key)
    return len(re.findall('VC', key))

'''
hasVowel is a helper function for seeing if there is a vowel in a word or not
@param word: the word to be checked for vowels
@return: true if a vowel is found, false if not
'''
def hasVowel(word):
    key = word
    #convert all y's that are preceded by a consonant with an e for structural purposes
    key = re.sub(r'(?P<c>[b-df-hj-np-tv-xz])y', r'\g<c>e', key)
    key = re.sub(vowels, 'V', key)
    return len(re.findall('V', key))>0

'''
staro, or *o is from the paper, it tells if the word ends with cvc (consonant, vowel, consonant)
    the second consonant can't be x, w, or y
@param word: the word to be checked for the *o condition
@return: true if the pattern cvc is found at the end of the word, false if not
'''
def staro(word):
    key = word
    #convert all y's that are preceded by a consonant with an e for counting purposes
    key = re.sub(r'(?P<c>[b-df-hj-np-tv-xz])y', r'\g<c>e', key)
    key = re.sub(r'[aeiou]', 'V', key)
    return len(re.findall(r'[b-df-hj-np-tv-z]V[b-df-hj-np-tvz]\b', key))>0

'''
stem returns the stem of a word, following the steps described in the Porter paper
@param word: the word to be 'stemmed'
@return: the stem of the word
'''
def stem(word):
    stem=word
    ''' -----Step 1----- '''
    ''' Plurals and past participles '''
    #step 1a
    stem = re.sub(r'sses\b', 'ss', stem, 1)
    stem = re.sub(r'ies\b', 'i', stem, 1)
    stem = re.sub(r'ss\b', 'ss', stem, 1)
    stem = re.sub(r'(?P<l>[^s])s\b', r'\g<l>', stem, 1)
    #step 1b
    if measure(re.sub(r'eed\b', '', stem)) > 0:
        stem = re.sub(r'eed\b', 'ee', stem)
    conditional = stem
    if hasVowel(re.sub(r'ed\b', '', stem)):
        stem = re.sub(r'ed\b', '', stem)
    if hasVowel(re.sub(r'ing\b', '', stem)):
        stem = re.sub(r'ing\b', '', stem)
    if conditional != stem:
        stem = re.sub(r'at\b', 'ate', stem)
        stem = re.sub(r'bl\b', 'ble', stem)
        stem = re.sub(r'iz\b', 'ize', stem)
        stem = re.sub(r'(?P<d>[b-df-hjkmnp-rtv-y])(?P=d)\b', r'\g<d>', stem)
        if measure(stem)==1 and staro(stem):
            stem = re.sub(r'(?P<w>.*)', r'\g<w>e', stem)
    #step 1c
    if hasVowel(re.sub(r'y\b', '', stem)):
        stem = re.sub(r'y\b', 'i', stem)
        
    ''' -----Step 2----- '''
    suffix2 = {r'ational\b':'ate', r'tional\b':'tion', r'enci\b':'ence', r'anci\b':'ance',
               r'izer\b':'ize', r'abli\b':'able', r'alli\b':'al', r'entli\b':'ent', r'eli\b':'e',
               r'ousli\b':'ous', r'ization\b':'ize', r'ation\b':'ate', r'ator\b':'ate',
               r'alism\b':'al', r'iveness\b':'ive', r'fulness\b':'ful', r'ousness\b':'ous',
               r'aliti\b':'al', r'iviti\b':'ive', r'biliti\b':'ble'}
    for k,v in suffix2.items():
        if measure(re.sub(k, '', stem)) > 0:
            stem = re.sub(k, v, stem)
    
    ''' -----Step 3----- '''
    suffix3 = {r'icate\b':'ic', r'ative\b':'', r'alize\b':'al', r'iciti\b':'ic', 
               r'ful\b':'', r'ness\b':''}
    for k,v in suffix3.items():
        if measure(re.sub(k, '', stem)) > 0:
            stem = re.sub(k, v, stem)
    
    ''' -----Step 4----- '''
    suffix4 = {r'al\b':r'', r'ance\b':r'', r'ence\b':r'', r'er\b':r'', r'ic\b':r'', r'able\b':r'', 
               r'ible\b':r'', r'ant\b':r'', r'ement\b':r'', r'ment\b':r'', r'ent\b':r'', 
               r'(?P<l>[st])?ion\b':r'\g<l>', r'ou\b':r'', r'ism\b':r'', r'ate\b':r'', 
               r'iti\b':r'', r'ous\b':r'', r'ive\b':r'', r'ize\b':r''}
    for k,v in suffix4.items():
        if measure(re.sub(k, '', stem)) > 1:
            #need this print statement so Python doesn't skip to the short ones first
            #otherwise we get things like adjustm instead of adjust from adjustment
            print ('',end='')
            stem = re.sub(k, v, stem)
    
    ''' -----Step 5----- '''
    #step 5a
    if measure(re.sub(r'e\b', '', stem)) > 1:
        stem = re.sub(r'e\b', '', stem)
    if measure(re.sub(r'e\b', '', stem)) == 1 and not staro(re.sub(r'e\b', '', stem)):
        stem = re.sub(r'e\b', '', stem)
    #step 5b
    if measure(re.sub(r'l\b', '', stem))>1:
        stem = re.sub(r'll\b', 'l', stem)
    
    return stem

'''
This main is for testing purposes. It has all the words that are in the document, and
all of them work. They are organized by 'step' of the stemmer. tester is for testing 
particular words, such as 'adjustment', that cause annoying problems because of python
trying to optimize things too much and not being predictable like some other languages.
'''
def main():
    words1 = ['caresses', 'ponies', 'ties', 'caress', 'cats', 'feed', 'agreed',
             'plaster', 'bled', 'motor', 'sing', 'conflated', 'troubled', 
             'sized', 'hopping', 'tanned', 'falling', 'hissing', 'fizzed',
             'failing', 'filing', 'fixing', 'happy', 'sky']
    words2 = ['relational', 'conditional', 'rational', 'valenci', 'hesitanci',
              'digitizer', 'conformabli', 'radicalli', 'differentli', 'vileli',
              'analogousli', 'vietnamization', 'predication', 'operator',
              'feudalism', 'decisiveness', 'hopefulness', 'callousness', 'formaliti',
              'sensitiviti', 'sensibiliti']
    words3 = ['triplicate', 'formative', 'formalize', 'electricity', 'electrical', 
              'hopeful', 'goodness']
    words4 = ['revival', 'allowance', 'inference', 'airliner', 'gyroscopic', 
               'adjustable', 'defensible', 'irritant', 'replacement', 'adjustment',
               'dependent', 'adoption', 'homologou', 'communism', 'activate', 
               'angulariti', 'homologous', 'effective', 'bowdlerize']
    words5 = ['probate', 'rate', 'cease', 'controlling', 'rolling']
    tester = ['adjustment']
    for word in words5:
        print(stem(word))

if __name__ == '__main__':
    main()