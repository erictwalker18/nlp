'''
spellcheck.py
@author: Eric Walker
CS 322 Fall '15 Carleton College
Spell Checker and Corrector
'''

import random
import re
import sys
import stemmer

'''
tokenize takes in a line of text and tokenizes it, replacing ' between letters with
escape character '#', and denotes the start of sentences or lines with '@'
@param line: the line to be tokenized
@return: a list of words cleaned of punctuation, with escape characters for ' as part of words
    and denotes the starts of lines
'''
def tokenize(line):
    words = re.sub(r'(^|\. )([A-Z])', r'\1@\2', line)
    words = re.sub(r'([A-Za-z])\'([A-Za-z_])', r'\1#\2', words)
    words = re.split(r'[-\.,?!:;_()\[\]`\'"/\t\n\r \x0b\x0c]+', words)
    return [word.strip() for word in words if word.strip() != '']

'''
subcost takes in a target and source word and indecies for both, then returns whether or not
the characters at those points are the same
@param target: the target string
@param source: the source string
@param i: the index for the target string
@param j: the index for the source string
@return: 0 if the characters match, 2 if not
'''
def subcost(target, source, i , j):
    if target[i] != source[j]:
        return 2
    return 0

'''
mineditdist finds the minimum edit distance between two words, target and source,
using the Damerau-Levenshtein distance
@param target: the target string
@param source; the source string
@return: an int that is the edit distance between the two strings 
'''
def mineditdist(target, source):
    n = len(target)
    m = len(source)
    
    distance = [[0 for x in range(m+1)] for y in range(n+1)]
        
    for i in range(1,n+1):
        distance[i][0] = distance[i-1][0] + 1
        
    for j in range(1,m+1):
        distance[0][j] = distance[0][j-1] + 1
    
    for i in range(1,n+1):
        for j in range(1, m+1):
            c = subcost(target, source, i-1, j-1)
            '''Converting to the Damerau-Levenshtein distance:
               basically, switching two adjacent letters has a cost of 1
               instead of a cost of 2 (1 deletion and 1 insertion)
               
               This difference was the one I noticed the most- switching
               two letters is a common misspelling, so it was necessary
               to make it "cheaper" to switch them back to get better results.
               
               Given the short time of development, this was the only distance
               alteration made.'''
            if i > 1 and j > 1 and target[i-1] == source[j-2] and target[i-2] == source[j-1]:
                distance[i][j] = min(distance[i-1][j]+1, distance[i-1][j-1]+c, 
                                     distance[i][j-1]+1, distance[i-2][j-2]+1)
            else:
                distance[i][j] = min(distance[i-1][j]+1, distance[i-1][j-1]+c, 
                                     distance[i][j-1]+1)
    
    return distance[n][m]

'''
checkword takes in a word, a list of words to check against, whether or not to ignore case,
and the context for the word. It then checks if the word is valid against the list of words,
and appropriately prints out messages about what it is doing
@param word: the word to be checked
@param words: the list of words to check word against
@param firstword: (optional) whether or not the word is a firstword- basically whether or not
    to ignore case
@param context: (optional) the line on which the word appeared, useful for printing out 
    messages while the user waits for the word suggestions to appear
@return: a list of the 5 closest words to the input word, in ascending order of distance
'''
def checkword(word, words, firstword = False, context = ''):
    if word in words or stemmer.stem(word) in words:
        return True
    if len(word)>25:
        return False
    if firstword and (str(word[0]).upper()+word[1:] in words):
        return True
    print("Found a word that wasn't recognized: ", word, ", in the line: ")
    print(re.sub(word, word.upper(), context), end = '')
    print("We're looking for close matches to this word. Please wait...")
    dist = 0
    editdists = [10]*5
    wordlist = {0:'',1:'',2:'',3:'',4:''}
    longest = max(editdists)
    index = 1
    for line in words:
        '''Stuff to make it faster!'''
        '''Match upper/lowercase'''
        if not firstword and word[0].isupper() != line[0].isupper():
            continue
        '''Don't allow words that are too long or too short from the dictionary'''
        if len(line)-3 > len(word) or len(word)-3 > len(line):
            continue
        '''Randomly check if some letters are contained in both, 
            only for long enough words. This is the part that really gets the time
            down to the order of seconds, rather than minutes.'''
        if len(word) > 3:
            count = 0
            for x in range(int(len(word)/4)):
                if word[int(random.random()*len(word))] in line:
                    count += 1
            if count < (int(len(word)/4)) - int(4/len(word)):
                continue
        
        '''If we get through all that, then calculate the min edit distance'''
        #ignore case if it's the first word
        if firstword:
            dist = mineditdist(line.lower(), word.lower())
        else:
            dist = mineditdist(line, word)
        
        '''Saves the word if it's in the top 5'''
        if dist < longest:
            index = editdists.index(longest)
            editdists.remove(longest)
            wordlist[index] = line
            editdists.insert(index, dist)
            longest = max(editdists) 
    '''Ordering the list of words that are the closest to the source word'''
    returnlist = []
    while len(returnlist)<5:
        for val in editdists:
            if len(returnlist) == 5:
                break
            if val == min(editdists):
                returnlist.append(wordlist.get(editdists.index(val)))
                wordlist.pop(editdists.index(val),0)
                editdists[editdists.index(val)] = 11
            
    print(returnlist)
    return returnlist

'''
main opens the dictionary file, as well as the input file and the output file. It runs
through the input file and checks all the words in it to make sure they are valid words.
If a word is not valid, it prompts the user to select one of the suggestions from the 
checkword method. Based on user input, it then writes a corrected file with the corrections.
'''
def main():
    print("Welcome to the spell checker! Your file will now be spell-checked:")
    f = open("words")
    dictionary = []
    for line in f:
        dictionary.append(line.rstrip())
    textf = open(sys.argv[1])
    output = open('corrected_'+sys.argv[1], 'w')
    checkresponse = ''
    for line in textf:
        words = tokenize(line)
        editedline = line
        for word in words:
            word = re.sub('#', "'", word)
            if word.isupper():
                word = '@' + word.lower()
            if word[0] == '@':
                checkresponse = checkword(word[1:].lower(), dictionary, firstword=True, 
                                          context=line)
                word = word[1:]
            else:
                checkresponse = checkword(word, dictionary, context = line)
            
            if checkresponse == True:
                pass
            elif checkresponse == False:
                print("Found a word that is too long to be checked: ", word," in: ")
                print(line)
            else:
                print("Please choose one of these suggestions by typing 1-5 or typing ",
                        "your own correction.")
                for x in range(5):
                    print(str(x+1), ": ", checkresponse[x])
                choice = input("Please choose one of these suggestions by typing 1-5 or "
                                "typing your own correction: ")
                if choice in ['1', '2', '3', '4', '5']:
                    editedline = re.sub(word, checkresponse[int(choice)-1], editedline)
                else:
                    editedline = re.sub(word, choice, editedline)
        output.write(editedline)
    output.close()            
    f.close()
    print("File was written to corrected_"+sys.argv[1])

if __name__ == '__main__':
    main()