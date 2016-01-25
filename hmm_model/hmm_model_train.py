'''
hmm_model_build.py
@author: Eric Walker
CS 322 Fall '15 Carleton College
HMM model trainer
'''

import sys
import pickle
import copy

#alpha is a 2d matrix
#alpha_{jt} = forward probability of being in state j at time t
def getalph(A, B, O, words):
    alph = []
    for i in range(len(O)+1):
        alph.append({})
    #initialization of alpha
    for tag in A:
        if tag == '<start>':
            continue
        if O[0] not in words: #we only look at words that we've actually seen in the test set, otherwise, they're unknown words
            O[0] = '<unk>'
        alph[0][tag] = A['<start>'][tag]*B[tag][O[0]]
    for t in range(1,len(O)):
        for tag in A:
            if tag == '<start>':
                continue
            if O[t] not in words: #we only look at words that we've actually seen in the test set, otherwise, they're unknown words
                O[t] = '<unk>'
            
            alph[t][tag] = 0
            for tag2 in A:
                if tag2 == '<start>':
                    continue
                alph[t][tag] += alph[t-1][tag2]*A[tag2][tag]*B[tag][O[t]]
                
                
                
    #use the <end> part to make calculations simpler later
    t = len(O)
    alph[t]['<end>'] = 0
    for tag in A:
        if tag == '<start>':
            continue
        alph[t]['<end>'] += alph[t-1][tag]*A[tag]['<end>']
    #for i in range(len(alph)):
    #    print(i, alph[i])
    return alph

#beta is a 2d matrix
#beta{jt} = probability of getting from state j at time t to final state
def getbeta(A, B, O, words):
    beta = []
    for i in range(len(O)+1):
        beta.append({})
    #initialization of beta
    for tag in A:
        if tag == '<start>':
            continue
        beta[len(O)][tag] = A[tag]['<end>']
    for i in range(1,len(O)+1):
        t = len(O)-i
        for tag in A:
            if tag == '<start>':
                continue
            if O[t] not in words: #we only look at words that we've actually seen in the test set, otherwise, they're unknown words
                O[t] = '<unk>'
            
            beta[t][tag] = 0
            for tag2 in A:
                if tag2 == '<start>':
                    continue
                beta[t][tag] += beta[t+1][tag2]*A[tag][tag2]*B[tag][O[t]]
    
    #for i in range(len(beta)):
    #    print(i, beta[i])
    return beta

#A is a 2d matrix
#a_{ij} = count(qi->qj)/count(qi->any)
def getA(countset, tags):
    tagcounts = {}
    #initialize tagcounts:
    tags['<start>'] = len(countset)
    tags['<end>'] = len(countset)
    for tag1 in tags:
        tagcounts[tag1] = {}
        for tag2 in tags:
            tagcounts[tag1][tag2] = 0
    for sentence in countset:
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
    
    A={}
    for tag1 in tagcounts:
        if tag1 == '<end>':
            continue
        A[tag1] = {}
        tot = 0
        for temp in tagcounts[tag1]:
            tot += tagcounts[tag1][temp]
        for tag2 in tagcounts:
            if tag2 == '<start>':
                continue
            elif tag2 not in tagcounts[tag1]:
                A[tag1][tag2] = 0
            else:
                A[tag1][tag2] = tagcounts[tag1][tag2]/tot
    return A

#B is a 2d matrix
#b_{ij} = count(qi observe vj)/count(qi)
def getB(countset, dictionary, words):
    tags = {}
    wordtagcounts = {}
    for sentence in countset:
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
                    #checking for existing in the dictionary
                    if word[0] not in dictionary:
                        continue
                    elif word not in dictionary[word[0]]:
                        word = '<unk>'
                    else:
                        words.append(word)
                
                if word not in wordtagcounts:
                    wordtagcounts[word] = {}
                if tag not in wordtagcounts[word]:
                    wordtagcounts[word][tag] = 1
                else:
                    wordtagcounts[word][tag] += 1
                if tag not in tags:
                    tags[tag] = 1
                else:
                    tags[tag] += 1
    for word in words:
        if word not in wordtagcounts:
            wordtagcounts[word] = {}
    
    B={}
    for tag in tags:
        if tag == '<start>' or tag == '<end>':
            continue
        B[tag] = {}
        for word in wordtagcounts:
            if tag not in wordtagcounts[word]:
                B[tag][word] = 0
            else:
                B[tag][word] = wordtagcounts[word][tag]/tags[tag]
    return (B, tags, words)

def getzeta(A, B, alph, beta, O, words):
    zeta = []
    for i in range(len(O)+1):
        zeta.append({})
    #start->qi stuff
    if O[0] not in words:
        O[0] = '<unk>'
    zeta[0]['<start>'] = {}
    for i in A:
        if i == '<start>':
            continue
        if alph[len(alph)-1]['<end>'] != 0:
            zeta[0]['<start>'][i] = alph[0][i]*A['<start>'][i]*B[i][O[0]]*beta[0][i]/alph[len(alph)-1]['<end>']
        else:
            zeta[0]['<start>'][i] = 0
    #recursion stuff qi->qj        
    for t in range(len(O)-1):
        if O[t+1] not in words:
            O[t+1] = '<unk>'
        for i in A:
            if i == '<start>':
                continue
            zeta[t+1][i] = {}
            for j in A:
                if j == '<start>':
                    continue
                if alph[len(alph)-1]['<end>'] != 0:
                    zeta[t+1][i][j] = alph[t][i]*A[i][j]*B[j][O[t+1]]*beta[t+1][j]/alph[-1]['<end>']
                else:
                    zeta[t+1][i][j] = 0
    for i in A:
        if i == '<start>':
            continue
        zeta[-1][i] = {}
        if alph[len(alph)-1]['<end>'] != 0:
            zeta[-1][i]['<end>'] = alph[len(O)-1][i]*A[i]['<end>']*beta[len(O)][i]/alph[-1]['<end>']
        else:
            zeta[-1][i]['<end>'] = 0
    
    return zeta

def getgamm(A, alph, beta, O, words):
    gamm = []
    for i in range(len(O)):
        gamm.append({})
    
    for t in range(len(O)):
        for j in A:
            if j == '<start>':
                continue
            if alph[len(alph)-1]['<end>'] != 0:
                gamm[t][j] = alph[t][j]*beta[t][j]/alph[len(alph)-1]['<end>']
            else:
                gamm[t][j] = 0
                
    return gamm

def loaddictionary():
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
    return dictionary

def main():
    args = open(sys.argv[1])
    dataset=[]
    for line in args:
        dataset.append([])
        line = line.rstrip()
        for item in line.split(' '):
            dataset[-1].append(item)
    countset = copy.deepcopy(dataset[:int(len(dataset)/100)])
    trainingset = copy.deepcopy(dataset[:int(len(dataset)/50)])
    
    #opening dictionary, saving to a dict ordered by the first character
    print("Loading the dictionary...")
    dictionary = loaddictionary()
    words = []
    print("Cleaning the input data of tags")
    #data cleaning
    for i in range(len(trainingset)):
        for x in range(len(trainingset[i])):
            if '/' in trainingset[i][x] and len(trainingset[i][x]) > 2: #error checking
                if trainingset[i][x].count('/')>1:
                    wordparts = trainingset[i][x].split('/')
                    trainingset[i][x] = ' '.join(wordparts[:-1])
                else:
                    trainingset[i][x] = trainingset[i][x].split('/')[0]
                trainingset[i][x] = trainingset[i][x].lower()
                if trainingset[i][x] not in words:
                    if trainingset[i][x][0] not in dictionary:
                        continue
                    elif trainingset[i][x] in dictionary[trainingset[i][x][0]]:
                        words.append(trainingset[i][x])
                    else:
                        trainingset[i][x]  = '<unk>'
                        if '<unk>' not in words:
                            words.append('<unk>')
                        
    print("Loading A and B on a small portion of the data...")
    (B, tags, words) = getB(countset, dictionary, words)
    A = getA(countset, tags)
    
                        
    print("Performing optimization... this may take a while")
    underflowcheck = -1
    for l in range(1000):
        ahat = {}
        bhat = {}
        
        #initialize the matricies
        for a in A:
            ahat[a] = {}
            for b in A:
                if b == '<start>':
                    continue
                ahat[a][b] = 0
            if a == '<start>':
                continue
            ahat[a]['<end>'] = 0
            bhat[a] = {}
            for v in words:
                bhat[a][v] = 0
            
        #do the thing
        for O in trainingset:
            alph = getalph(A,B,O,words)
            beta = getbeta(A, B, O, words)
            zeta = getzeta(A, B, alph, beta, O, words)
            gamm = getgamm(A, alph, beta, O, words)
            
            #ahat calculations
            for i in A:
                if i == '<start>':
                    continue
                ahat['<start>'][i] += gamm[0][i]
                ahat[i]['<end>'] += zeta[-1][i]['<end>']
                for j in A:
                    if j == '<start>':
                        continue
                    topsum = 0
                    bottomsum = 0
                    for t in range(1,len(O)-1):
                        topsum += zeta[t][i][j]
                        bottomsum += gamm[t][i]
                    if bottomsum != 0:
                        ahat[i][j] += topsum / bottomsum
                    else:
                        ahat[i][j] += 0
                    
            #bhat calculations
            for j in A:
                if j == '<start>':
                    continue
                bottomsum = 0
                for t in range(len(O)):
                    bottomsum += gamm[t][j]
                if bottomsum == 0:
                    continue
                for t in range(len(O)):
                    topsum = gamm[t][j]
                    bhat[j][O[t]] = topsum/bottomsum
        
        #normalize ahat and bhat
        ahattot = 0
        bhattot = 0
        for i in ahat:
            ahattot += sum(ahat[i].values())
        if ahattot == 0:
            break
        for i in ahat:
            for j in ahat[i]:
                ahat[i][j] = ahat[i][j]/ahattot
              
        for i in bhat:
            bhattot += sum(bhat[i].values())
        if bhattot == 0:
            break
        for i in bhat:
            for j in bhat[i]:
                bhat[i][j] = 100*bhat[i][j]/bhattot #multiplying by 100 helps underflow issues
        if underflowcheck == -1:
            underflowcheck = bhattot
        
        if bhattot < .9*underflowcheck: #break if we start to get an underflow error
            break
        A=ahat
        B=bhat
        
    print("Saving to trainmodel.dat")
    pickle.dump((A, B, words), open('trainmodel.dat', 'wb'))
    
if __name__ == '__main__':
    main()