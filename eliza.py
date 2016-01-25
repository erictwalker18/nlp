'''
eliza.py
@author: Eric Walker
CS 322 Fall '15 Carleton College
ELIZA-style program for simulating psychiatric conversation
'''
import re

'''
getReponse takes in a string of user input and uses regular expressions
    to replace particular phrases to simulate conversation

@param userInput: the user input string
@return: a modified string to be presented to the user
'''
def getResponse(userInput):
    response=userInput
    acceptedReponses = ('I see.', 'Why not?', 'Goodbye!', 'Let\'s not talk about me.',
                        'Why do you ask about .*\?', 'Do you enjoy being .*\?',
                        'Why do you think .*\?', 'So .* makes you .*\?', 
                        'Why do you want .*\?', 'Hello. Please tell me about your problems.',
                        'Why do you feel .*\?', 'Why does it matter where .*\?', 'Your? .*')
    response = re.sub(r'yes', 'I see.', response)
    response = re.sub(r'\bno\b', 'Why not?', response)
    response = re.sub(r'\bgoodbye\b', 'Goodbye!', response)
    response = re.sub(r'.*\byou.*', 'Let\'s not talk about me.', response)
    response = re.sub(r"\bwhat is (?P<object>[a-z\s'\.:;!]*)\?", r'Why do you ask ' 
                                'about \g<object>?', response)
    response = re.sub(r"\bi am (?P<desc>[a-z\s'0-9\.:;\?!]*)", 'Do you enjoy being '
                            '\g<desc>?', response)
    response = re.sub(r"\bwhy is (?P<quest>[a-z\s'0-9]*)\?", 'Why do you think \g<quest>?', response)
    
    #Responses I added
    response = re.sub(r"\bi (?P<stuff>[a-z\s'0-9]*) because (?P<reason>"
                            "[a-z\s'0-9]*)", 'So \g<reason> makes you \g<stuff>?', response)
    response = re.sub(r"how should i (?P<quest>[a-z\s'0-9]*)?", "Why do you want"
                      " to \g<quest>?", response)
    response = re.sub(r'\b(hi|hello)\b', 'Hello. Please tell me about your problems.', response)
    response = re.sub(r"\bi feel (?P<feeling>[a-z0-9'\s]*)\.?", "Why do you feel \g<feeling>?",
                      response)
    response = re.sub(r"\bwhere \b(?P<verb>[a-z]*)\b (?P<subj>[a-z\s'0-9]*)\?", 
                      "Why does it matter where \g<subj> \g<verb>?",response)
    
    #Replacing 'my *' with your, appropriately capitalized and punctuated
    response = re.sub(r"\bmy (?P<thing>[a-z\s'0-9]*)", 'your \g<thing>', response)
    response = re.sub(r"your (?P<s>[a-z\s'0-9]*)$", 'your \g<s>.', response)
    response = re.sub(r"^your\b", 'Your', response)
    response = re.sub(r"(?P<punc>[.?!]\s)your\b", '\g<punc>Your', response)
    
    #Replacing 'i *' with you, appropriately capitalized and punctuated
    response = re.sub(r"\bi\b", 'you', response)
    response = re.sub(r"you (?P<s>[a-z\s'0-9]*)$", 'you \g<s>.', response)
    response = re.sub(r"^you\b", 'You', response)
    response = re.sub(r"(?P<punc>[.?!]\s)you\b", '\g<punc>You', response)
    
    recognized = False
    for accept in acceptedReponses:
        recognized = recognized or (re.search(accept, response) != None)
    if not recognized:
        response = re.sub('.*', 'Please go on...', response)

    return response

def main():
    userInput = input("Hello. Please tell me about your problems:\n").lower()
    while True:
        response = getResponse(userInput)
        if (response == 'Goodbye!'):
            break
        userInput = input(response + '\n').lower()
        
    print("Thank you for the conversation. That will be $453.28. \n"
          "See the receptionist for an itemized receipt.")

if __name__ == '__main__':
    main()