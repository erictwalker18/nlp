'''
synthesizer.py
@author: Eric Walker
CS 322 Fall '15 Carleton College
Final project
'''
#import winsound
import pygame
import wave
import os
import array
import numpy as np
import re

'''
checks a list of symbols to see if all of them are valid
@param symbols: the symbols to check
@param sounds: the sound dictionary the program uses
@return: true if sounds are all recognized, false otherwise with an error message
'''
def checksymbols(symbols, sounds):
    for sym in symbols:
        #skip words that aren't upper case- these will be parsed differently
        if sym.isupper() and sym not in sounds:
            print('Sorry, the symbol', sym, 'is not accepted.')
            return False
    return True

'''
returns the fft of a particular window of length 400
@param pos: the position in the wave data to start
@param currentsym: the wave data to get the fft from
@return: the fourier transform of the window starting at pos
'''
def getFft(pos, currentsym):
    #use the hamming window so we can get the inverse out later
    ham = np.hamming(400)
    frame = currentsym[pos:pos+400]
    frame = np.multiply(ham, frame)
    
    transform = np.fft.fft(frame)
    #square magnitude code, just in case we'd need it later
    '''
    squaremag = np.sqrt(np.square(transform.real)+np.square(transform.imag))
    logsquaremag = 10*np.log10(squaremag)
    '''
    return transform

'''
parses the arpabet dictionary file
@param file: the arpabet file
@return: a dict referring words to arpabet translations
'''
def parsearpadict(file):
    arpadict = {}
    for line in file:
        keys = line.rstrip().split(' ')
        if keys[0] == ';;;':
            continue
        i=1
        while i < len(keys):
            if keys[i] == '':
                keys.remove('')
            keys[i] = re.sub(r'[0-9]\b', r'', keys[i])
            i += 1
        arpadict[keys[0]] = keys[1:]
    return arpadict

'''
Welcomes the user and runs the for loop that asks the user for input,
then outputs sound, if possible
'''
def main():
    print("Hello, welcome to the synthesizer!")
    print("Loading the arpabet dictionary... (Takes a second)")
    
    filename = 'arpadict.txt'
    arpadict = parsearpadict(open(filename))
    
    print("Type what you want to hear in all uppercase arpabet, separated by spaces,")
    print("or in regular text (lowercase). For example: HH AY _ how are you")
    print("If you want to quit, just type 'quit' (without the parentheses)")
    sounds = {}
    soundframes = {}
    for filename in os.listdir('audiofiles/'):
        sound = filename.split('.')[0]
        if filename[0] == '.':
            continue
        sounds[sound] = wave.open('audiofiles/'+filename, 'rb')
        soundframes[sound] = sounds[sound].readframes(sounds[sound].getnframes())
    
    ex = sounds['W']
    #get default output file format
    channels = ex.getnchannels()
    sampwidth = ex.getsampwidth()
    framerate = ex.getframerate()
    comptype = ex.getcomptype()
    compname = ex.getcompname()
    
    pygame.init()
    pygame.mixer.init()

    while True:
        symbols = input("Enter some text you want played:").split(' ')
        
        if symbols[0]=='quit':
            break
        
        for sym in symbols:
            if not sym.isupper() and sym != '_':
                if sym.upper() not in arpadict:
                    print("Didn't recognize", sym, ". Try typing it into the program in arpabet.")
                    symbols[symbols.index(sym)] = '_'
                else:
                    symbols[symbols.index(sym):symbols.index(sym)+1] = arpadict[sym.upper()]
        
        if os.path.isfile('output.wav'):
            os.remove('output.wav')
        if not checksymbols(symbols, sounds):
            continue
        if len(symbols) == 1:
            winsound.PlaySound('audiofiles/'+symbols[0]+'.wav', winsound.SND_FILENAME)
            continue
        length = 0
        smoothlength = 5
        for sym in symbols:
            length += sounds[sym].getnframes() + smoothlength
        
        #generate output file
        output = wave.open('output.wav', 'wb')
        output.setparams((channels, sampwidth, framerate, length, comptype, compname))
        isfirst = True
        totalout = array.array('h',[])
        
        lasttransform = []
        
        for sym in symbols:
            temp = wave.open('audiofiles/'+sym+'.wav')
            a = temp.readframes(temp.getnframes())
            currentsym = array.array('h', a)
            
            #find Fourier transform of the first window of the current symbol
            #and the last window of the current symbol
            pos1 = 0
            currenttransform = getFft(pos1, currentsym)
            pos2 = int(len(currentsym)-401)
            newlasttransform = getFft(pos2, currentsym)
            
            #if we're on the first symbol, there's no previous symbol to smooth from,
            #so we'll smooth from silence, or all 0s in the fft
            if isfirst:
                lasttransform = np.zeros(400, dtype=np.complex128)
            
            #add smoothing from lasttransform to currenttransform
            #(basically take the average of the fourier transforms, then inverse fourier transform)
            smoother = np.divide(np.add(lasttransform, currenttransform),2)
            
            #compute the inverse fourier transform
            middle = np.fft.ifft(smoother).real.astype(int)
            middle = middle[100:300]
            #middle = np.divide(middle,  np.hamming(400)[100:300])
            
            #convert the inverse fourier transform back to bytes
            middle = np.ndarray.tolist(middle.astype(int))
            middle = array.array('h', middle)
            
            #do linear smoothing to smooth out the curves
            start = middle[-1]
            end = currentsym[0]
            if start != end:
                middle += array.array('h', [int(i/(abs(end-start))) for i in range(smoothlength)])
            else:
                middle += array.array('h', [start]*smoothlength)
            currentsym = middle+currentsym
            
            
            #once we're done with the old lasttransform, save the new one
            lasttransform = newlasttransform
            
            #write the modified frames to the output file
            newthing = bytearray(currentsym)
            totalout += currentsym
            framestowrite = newthing
            output.writeframes(framestowrite)
            if isfirst:
                isfirst = False
        
        #play the sound
        #winsound.PlaySound('output.wav', winsound.SND_FILENAME)
        sounda = pygame.mixer.Sound('output.wav')
        sounda.play()
        output.close()
    print("Thanks for listening!")

if __name__ == '__main__':
    main()
