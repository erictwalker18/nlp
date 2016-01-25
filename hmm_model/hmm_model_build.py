'''
hmm_model_build.py
@author: Eric Walker
CS 322 Fall '15 Carleton College
HMM model builder
'''

import sys
import pickle

#A is a 2d matrix
#a_{ij} = count(qi->qj)/count(qi->any)
def getA(counts):
    A={}
    for tag1 in counts:
        if tag1 == '<end>':
            continue
        A[tag1] = {}
        tot = 0
        for temp in counts[tag1]:
            tot += counts[tag1][temp]
        for tag2 in counts:
            if tag2 == '<start>':
                continue
            elif tag2 not in counts[tag1]:
                A[tag1][tag2] = 0
            else:
                A[tag1][tag2] = counts[tag1][tag2]/tot
    return A

    
#B is a 2d matrix
#b_{ij} = count(qi observe vj)/count(qi)
def getB(dataset, tags):
    B={}
    for tag in tags:
        if tag == '<start>' or tag == '<end>':
            continue
        B[tag] = {}
        for word in dataset:
            if tag not in dataset[word]:
                B[tag][word] = 0
            else:
                B[tag][word] = dataset[word][tag]/tags[tag]
    return B

def main():
    args = open(sys.argv[1])
    dataset=[]
    for line in args:
        dataset.append([])
        for item in line.split(' '):
            dataset[-1].append(item)
    trainingset = dataset
    #testset = dataset[int(len(dataset)/9):]
    
    print("Loading the dictionary...")
    
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
    
    print('Calculating the B matrix and checking if words are in the dictionary...')
    tags = {}
    wordtagcounts = {}
    words = []
    for sentence in trainingset:
        for i in range(len(sentence)):
            x = sentence[i]
            if '/' in x and len(x) > 2: #error checking
                if x.count('/')>1:
                    wordpartstag = x.split('/')
                    tag = wordpartstag[-1]
                    word = ' '.join(wordpartstag[:-1])
                else:
                    (word, tag) = x.split('/')
                word = word.lower()
                
                if word not in words:
                    words.append(word)
                
                #checking for existing in the dictionary
                if word[0] not in dictionary:
                    continue
                elif word not in dictionary[word[0]]:
                    word = '<unk>'
                
                if word not in wordtagcounts:
                    wordtagcounts[word] = {}
                if tag not in wordtagcounts[word]:
                    wordtagcounts[word][tag] = 1
                else:
                    wordtagcounts[word][tag] += 1
                #updating the tag dictionary, for use in A
                if tag not in tags:
                    tags[tag] = 1
                else:
                    tags[tag] += 1
                    
    tagcounts = {}
    #initialize tagcounts:
    tags['<start>'] = len(trainingset)
    tags['<end>'] = len(trainingset)
    for tag1 in tags:
        tagcounts[tag1] = {}
        for tag2 in tags:
            tagcounts[tag1][tag2] = 0
            
    print('Calculating the A matrix...')
    for sentence in trainingset:
        sentencetags = []
        #first find all the tags in the sentence
        for x in sentence:
            if not('/' in x and len(x) > 2): #error checking
                continue
            sentencetags.append(x.split('/')[-1])
        #now loop through all the tags and add counts
        for i in range(len(sentencetags)-1):
            if i==0:
                tagcounts['<start>'][sentencetags[i]] += 1
            else:
                tagcounts[sentencetags[i-1].split('/')[-1]][sentencetags[i]] += 1
        tagcounts[sentencetags[-1]]['<end>'] += 1
    
    print("Calculating HMM probabilities...")
    A = getA(tagcounts)
    B = getB(wordtagcounts, tags)
    print("Saving to countmodel.dat")
    pickle.dump((A, B, words), open('countmodel.dat', 'wb'))
    
if __name__ == '__main__':
    main()