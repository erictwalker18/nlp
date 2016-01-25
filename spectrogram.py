'''
spectrogram.py
@author: Eric Walker
CS 322 Fall '15 Carleton College
Spectrogram maker
'''

import wave
import numpy as np
import struct
import PIL.Image as Image
import sys

def main():
    filename = sys.argv[1]
    wavefile = wave.open(filename, 'rb')
    #wav files are 1 channel, 16bit samples, 16000 hz
    #25ms frames are 400 samples long
    #10ms windows are 160 samples long
    length = wavefile.getnframes()
    wavedata = []
    for i in range(0,length):
        a=wavefile.readframes(1)
        wavedata.append(struct.unpack('<h',a)[0])
    magnitudes = []
    length = int(len(wavedata)/160)
    topcolor = 0
    han = np.hanning(400)
    for i in range(0,length):
        frame = wavedata[i*160:i*160+400]
        if (len(frame)!= 400):
            han = np.hanning(len(frame))
        frame = np.multiply(han, frame)
        transform = np.fft.fft(frame)
        transform = transform[len(transform)/2:]
        squaremag = np.sqrt(np.square(transform.real)+np.square(transform.imag))
        magnitudes.append(10*np.log10(squaremag))
        if topcolor < np.max(magnitudes[-1]):
            topcolor = np.max(magnitudes[-1])
    #frequency is i cycles per n samples, or i cycles per 25ms
    #see notes on what the frequency for the magnitudes[k] is
    
    blank = Image.new('RGB',(length,len(magnitudes[0])))
    pixels = blank.load()

    for x in range(length):
        vals = magnitudes[x]
        for y in range(len(magnitudes[x])):
            rgb = int(256-vals[y]*256/topcolor)
            pixels[x,y]= (rgb,rgb,rgb)
    blank.save("output.png", 'png')
    toshow = Image.open('output.png')
    toshow.show()
    
if __name__ == '__main__':
    main()
