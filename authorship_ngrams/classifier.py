'''
classifier.py
@author: Eric Walker
CS 322 Fall '15 Carleton College
Authorship classifier
'''
import urllib.request
import sys
import re
import math
from builtins import int

'''
tokenize takes in a block of text and tokenizes it, replacing ' between letters with
escape character '#', and denotes the start of sentences or lines with '@'
@param line: the line to be tokenized
@return: a list of words cleaned of punctuation, with escape characters for ' as part of words
    and denotes the starts of sentences with @
'''
def tokenize(block):
    words = re.sub(r',\n', '. ', block)
    words = re.sub(r'(\n)+', ' ', words)
    words = re.sub(r'\.\.+', '\.', words)
    words = re.sub(r'"', r' " ', words) #slightly improves devset results
    words = re.sub(r'(^|[\.?!] )([A-Z]|$)', r'\1@ \2', words)
    words = re.sub(r'([A-Za-z])\'([A-Za-z_])', r'\1#\2', words)
    words = re.split(r'[-\.,?!:;_()\[\]`\'/\t\n\r \x0b\x0c]+', words)
    return [word.strip() for word in words if word.strip() != '']

'''
openurls opens a list of authors and urls and stores the contents in a 
dictionary, which has keys of the author's names
@param urllist: the list of authors and urls for their corresponding files
@return: a dictionary of authors and lists of words associated with them
'''
def openurls(urllist):
    textlist = {}
    for line in urllist:
        url = line.split(',')[1]
        url = url.strip()
        webFile = urllib.request.urlopen(url)
        textlist[line.split(',')[0]] = (webFile.read().decode('UTF-8'))
        webFile.close()
    return textlist

'''
ngramify takes in a list of words and an n, then makes them into a list of phrases of n length
@param wordlist: the list of words to make ngrams from
@param n: the level to make ngrams from
@return: a list of ngrams
'''
def ngramify(wordlist, n):
    ngrams = []
    for i in range(len(wordlist)):
        for j in range(1,n):
            #initialize the dictionaries for each ngram
            if len(ngrams) < n-1:
                ngrams.append({})
            if i >= j-1:
                key = wordlist[i-j]
                for k in range(1,j):
                    key += ' ' +  wordlist[i-j+k]
                key = key.lower()
                if key not in ngrams[j-1]:
                    ngrams[j-1][key] = 1
                else:
                    ngrams[j-1][key] += 1
    return ngrams

'''
count returns the Good Turing smoothed counts of a set of words that has length > 1
@param langmodel: the language model to use for the counts
@param counts: the list of counts in the language model
@param words: list of words to apply count to
@return: the smoothed count of the n-gram words
'''
def count(langmodel, counts, words):
    if len(words) == 0:
        return 0
    x = len(words) - 1
    phrase = ' '.join(words)
    if phrase in langmodel[x]:
        c1 = langmodel[x][phrase]
    else:
        c1 = 0
    ''' if counts < 6, we use GT smoothing '''
    if c1 < 5:
        n1 = counts[x][c1]
        n2 = counts[x][c1+1]
        c1 = ((c1+1)*n2)/n1
    return c1

'''
findprob finds the probability of a set of words given a language model
@param langmodel: the language model to base calculations off of
@param testwords: the words to calculate the probability of
@param counts: the counts matrix associated with the language model
@param n: the n-gram we're using
@return: the log of the probability of testwords given the language model
'''
def findprob(langmodel, testwords, counts, n):
    total = 0
    if len(testwords) < n:
        n = len(testwords)
    for i in range(n-2, len(testwords)):
        countlist = []
        for j in range(1,n):
            countlist.append(testwords[i-(n-1-j)])
        a = count(langmodel, counts, countlist)
        b = count(langmodel, counts, countlist[1:])
        total += math.log10(a/b)
    return total

'''
sentencify is used for the -dev mode for breaking up sentences
@param wordlist: a list of words to break up into a list of sentences
@return: a list of sentences (starting and ending with the character '@')
'''
def sentencify(wordlist):
    sentences = []
    while '@' in wordlist[1:]:
        sentences.append(wordlist[:wordlist[1:].index('@')+1])
        sentences[-1].append('@')
        wordlist = wordlist[wordlist[1:].index('@')+1:]
    return sentences

'''
findcounts develops a count matrix for a language model (see comment inside it)
@param langmodel: the language model to make counts for
@param vocabsize: the number of words in the predetermined language
@return: a list of dictionaries that is the count matrix
'''
def findcounts(langmodel, vocabsize):
    '''Counts is the counts for counts of words for each n-gram
    that is... counts=[{0:123,1:131,2:3},{0:12,1:323,2:4}...]
                        ^unigram counts   ^bigram counts ...'''
    counts = []
    temp = []
    for m in langmodel:
        for val in m.values():
            temp.append(val)
        counts.append({})
        for i in range(6):
            counts[-1][i+1] = temp.count(i+1)
        
        #number of possible ngrams-number of ngrams seen
        counts[-1][0] = vocabsize**len(counts)-len(m)
    return counts

'''
getwordlist takes in a list of words and tokenizes and checks if they're in 
the predetermined dictionary
@param wordfile: the file of words to tokenize
@param dictionary: the dictionary dict to check words against
@return: a list of tokenized words
'''
def getwordlist(wordfile, dictionary):
    wordlist = tokenize(wordfile)
    for i in range(len(wordlist)):
        if wordlist[i][0].lower() not in dictionary:
            wordlist[i] = '<unk>'
        if wordlist[i][0].lower() not in dictionary[wordlist[i][0].lower()]:
            wordlist[i] = '<unk>'
    return wordlist

'''
devmode takes in a list of files and produces a dev set and training set,
trains on the training set, then tests itself on the dev set and prints out results
@param filelist: the list of authors and their files
@param n: the n-gram size we're using
@param dictionary: the dictionary we're using
@param vocabsize: the size of the vocabulary we're using
'''
def devmode(filelist, n, dictionary, vocabsize):
    print("Training. This may take a while...")
    langmodels = {}
    problist = {}
    devsetlist = {}
    countlist = {}
    sentences = {}
    for author in filelist:
        wordlist = getwordlist(filelist[author], dictionary)
        
        #make the devset, but start it at a sentence (denoted by @)
        devsetlist[author] = wordlist[int(len(wordlist)*9/10):]
        devsetlist[author] = devsetlist[author][devsetlist[author].index('@'):]
        #make the training set the rest of the words
        wordlist = wordlist[:int(len(wordlist)*9/10)]
        langmodels[author] = ngramify(wordlist, n)
        countlist[author] = findcounts(langmodels[author], vocabsize)
    
    print("Finished training, preparing results (also may take a while):")
    authortots = {}
    for author1 in filelist:
        authortots[author1] = [0,0]
        sentences = sentencify(devsetlist[author1])
        for sentence in sentences:
            if len(sentence) < 3:
                continue
            authortots[author1][0] += 1
            problist = {}
            for author2 in filelist:
                problist[author1,author2] = findprob(langmodels[author2], sentence, countlist[author2], n)
            if max(problist.values()) == problist[author1, author1]:
                authortots[author1][1] += 1
                
    print("Results on the dev set:")
    print("Author, Sentences Correct, Total Sentences")
    for author in sorted(filelist):
        authorname = author
        if len(authorname) < 7:
            authorname += '\t'
        print(authorname,'\t', authortots[author][1], '\t/', authortots[author][0])

'''
testmode takes in a filelist and a testfile, trains on the filelist, then
tries to guess the author of each line of the test file, and prints out its
best guess for each line
@param filelist: the training set
@param testfile: the test file
@param n: the n-gram depth we're going to
@param dictionary: the dictionary we're using
@param vocabsize: the size of the vocabulary we're using
''' 
def testmode(filelist, testfile, n, dictionary, vocabsize): 
    print("Training. This may take a while...")
    langmodels = {}
    countlist = {}
    for author in filelist:
        wordlist = getwordlist(filelist[author], dictionary)
        
        langmodels[author] = ngramify(wordlist, n)
        
        countlist[author] = findcounts(langmodels[author], vocabsize)
    
    testfile = open(testfile)
    sentences = []
    for line in testfile:
        sentences += '@'
        sentences += tokenize(line)
        sentences += '@' #mark the end of the line as a sentence break
    for word in sentences:
        if word not in dictionary:
            word = '<unk>'
    
    print("Finished training, preparing results:")
    maxes = [] #list of the most likely authors for a given sentence/line
    
    for sentence in sentences:
        if len(sentence) < 3:
            continue
        problist = {}
        for author in filelist:
            problist[author] = findprob(langmodels[author], sentence, countlist[author], n)
        bestguess = max(problist.keys(), key=lambda x:problist[x])
        maxes.append(bestguess)
       
    print("Results on the test set:")
    for author in maxes:
        print(author)

'''
main sets the n-depth we're running to, reads in the command-line arugments,
opens and initializes the dictionary, and decides which mode to run in
'''
def main():
    n=3
    if len(sys.argv) not in [3,4]:
        print("Invalid number of arguments. To use this please type either of:")
        print("-dev [authorlistfile]")
        print("-test [authorlistfile] [testfile]")
        exit()
    args = open(sys.argv[2])
    filelist = openurls(args)
    
    #opening dictionary, saving to a dict ordered by the first character
    dicfile = open('wordList.txt')
    dictionary = {}
    vocabsize = 0
    for word in dicfile:
        vocabsize += 1
        if word[0] in dictionary:
            dictionary[word[0]].append(word.strip())
        else:
            dictionary[word[0]] = [word.strip()]
    
    if sys.argv[1] == '-dev':
        devmode(filelist, n, dictionary, vocabsize)
    elif sys.argv[1] == '-test':
        testmode(filelist, sys.argv[3], n, dictionary, vocabsize)
    else:
        print("Invalid second argument. To use classifier.py please type either of:")
        print("-dev [authorlistfile]")
        print("-test [authorlistfile] [testfile]")
        exit()

if __name__ == '__main__':
    main()