'''
parser.py
@author: Eric Walker
CS 322 Fall '15 Carleton College
Parser assignment
'''
import sys

'''
reads a grammar file and returns the grammar associated with it
@param file: the grammar file
@return: the dictionary form of the grammar
'''
def getGrammar(file):
    lines = open(file)
    gram = {}
    for line in lines:
        line = line.rstrip()
        if len(line) < 1:
            continue
        if line[0] == '#':
            continue
        
        items = line.split(' ')
        if items[0] not in gram:
            gram[items[0]] = []
        gram[items[0]].append(items[2])
        if len(items) > 3:
            gram[items[0]][-1]+=' '+items[3]
    return gram

'''
parses a sentence and prints it
@param gram: the grammar to parse with
@param sent: the sentence to parse
@return: the complicated table made when parsing
'''
def parse(gram, sent):
    table = {}
    for j in range(1, len(sent)+1):
        table[j-1] = {}
        table[j-1][j] = []
        
        
        for A in gram:
            if sent[j-1] in gram[A]:
                table[j-1][j].append((A,sent[j-1]))
        
        table[j-1][j] += findsingleparent(gram, table[j-1][j])
        for i in range(j-2, -1, -1):
            if j not in table[i]:
                table[i][j] = []
            for k in range(i+1, j):
                for B in table[i][k]:
                    for C in table[k][j]:
                        table[i][j] += findparent(gram, B, C)
                        table[i][j] += findsingleparent(gram, findparent(gram, B, C))

    hasvalid = False
    for var in table[0][len(sent)]:
        if var[0] == 'S':
            hasvalid = True
            print("\n----------------------------")
            printtree(var,1)
        else:
            continue
    
    if not hasvalid:
        print("No valid parses found for this sentence.")
    return table

'''
finds any possible parent non-terminals of BC recursively
(it will find A and D in A->D, D->BC)
@param gram: the grammar to look in
@param B: something of the form (nonterm, [nonterm term or form B])
@param C: similar to C
@return: a list of possible parent trees (parent (B, C))
'''
def findparent(gram, B, C):
    parentlist = []
    for A in gram:
        if B[0]+' '+C[0] in gram[A]:
            parentlist.append((A,(B,C)))
    return parentlist

'''
Finds if there are any rules A -> B, B -> term
@param gram: the grammar to look in
@param B: list of (nonterm, term)
@return: additions to be made to B in terms of derivations
'''
def findsingleparent(gram, B):
    parentlist = []
    for tup in B:
        for A in gram:
            if tup[0] in gram[A] and not findduplicate(A, tup):
                parentlist.append((A,tup))
                parentlist += findsingleparent(gram, [(A,tup)])
    return parentlist

'''
Finds if there would be any duplicates in the rule
that is, if (C (B (A ...))), we couldn't put A on
(However, it would be ok with (A () ())), which we'd
get from unit productions like NOM -> NOM NN, NOM -> NN
@param A: the tag to check for duplicates
@param tup: the tuple to check for duplicates
@return whether A is already in tup or not
'''
def findduplicate(A,tup):
    if type(tup[0]) is not tuple and type(tup[1]) is tuple and A != tup[0]:
        return findduplicate(A, tup[1])
    elif type(tup[0]) is not tuple and type(tup[1]) is tuple and A == tup[0]:
        return True
    elif type(tup[0]) is not tuple and type(tup[1]) is not tuple:
        return A == tup[0]
    return False

'''
takes in a tree and a current level, then prints it
@param tree: the tree to print
@param n: the level of the tree (used for tabbing)
'''
def printtree(tree, n):
    if type(tree[1]) is tuple:
        print('('+ tree[0]+' ', end='')
        print('\t', end='')
        #check for (S, (VP, ((...),(...))), then just treat the (VP...) as a new tree
        if len(tree[1]) == 2 and type(tree[1][0]) is not tuple:
            printtree(tree[1],n+1)
        else:
            printtree(tree[1][0], n+1)
            print('\n'+'\t'*n, end='')
            printtree(tree[1][1], n+1)
            print(')',end='')
    else:
        print('('+tree[0]+' '+tree[1]+')', end='')

'''
main opens the command line arguments, gets a grammar, then parses
the input sentence
'''
def main():
    file = sys.argv[1]
    sent = sys.argv[2]
    
    gram = getGrammar(file)
    parse(gram, sent.rstrip().split())
    
if __name__ == '__main__':
    main()