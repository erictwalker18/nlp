'''
hmm_model_build.py
@author: Eric Walker
CS 322 Fall '15 Carleton College
HMM tagger
'''

import pickle
import sys
import math

def load_matricies(filename):
    (A, B, words) = pickle.load(open(filename, 'rb'))
    return (A,B, words)

def viterbi(A, B, O, words):
    vit = []
    backpointer = []
    for i in range(len(O)+1):
        vit.append({})
        backpointer.append({})
    for s in A:
        if s == '<start>':
            continue
        if O[0] not in words: #we only look at words that we've actually seen in the test set, otherwise, they're unknown words
            O[0] = '<unk>'
        vit[0][s] = A['<start>'][s]*B[s][O[0]]
        backpointer[0][s] = '<start>'
    for t in range(1,len(O)):
        for s in A:
            if s == '<start>':
                continue
            vit[t][s] = -sys.maxsize - 1
            if O[t] not in words: #we only look at words that we've actually seen in the test set, otherwise, they're unknown words
                O[t] = '<unk>'
            bthing = B[s][O[t]]
            for sprev in A:
                if sprev == '<start>':
                    continue
                vtj = vit[t-1][sprev]*(A[sprev][s]*bthing)
                if vtj > vit[t][s]:
                    vit[t][s] = vtj
                    backpointer[t][s] = sprev
    s = '<end>'
    t = len(O)
    vit[t][s] = -sys.maxsize - 1
    for sprev in A:
        if sprev == '<start>':
            continue
        vtj = vit[t-1][sprev]*(A[sprev][s])
        if vtj > vit[t][s]:
            vit[t][s] = vtj
            backpointer[t][s] = sprev
    return backpointer
    
def main():
    filename = sys.argv[1]
    (A,B,words) = load_matricies(filename)
    O = sys.stdin.readline()
    O = O.rstrip().split(' ')
    back = viterbi(A,B, O, words)
    O = sys.stdin.readline()
    O = O.rstrip().split(' ')
    output = ''
    tag = back[-1]['<end>']
    for i in range(1, len(O)+1):
        t = len(O)-i
        output = O[t]+'/'+tag + ' ' + output
        tag = back[t][tag]
    #print(output)
    sys.stdout.write(output)

if __name__ == '__main__':
    main()