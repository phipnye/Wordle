import pandas as pd
import numpy as np
import sys
import time

#Import Possible Words
global word_list
word_list = pd.read_csv("word_list.txt", delimiter = "\n", header=None)

#Declare list of letters that are not contained anywhere
global not_contained
not_contained = []

#Declare list of letters that are invalid for a given position
impos1 = []
impos2 = []
impos3 = []
impos4 = []
impos5 = []

#List of the letters that must be contained using the unique values in the impossibilities lists
global must_contain
must_contain = []

#Dictionary of the correct word
global correct_word
correct_word = [None] * 5

#Initialize an array of the impossibilities for each position
global impossibilities
impossibilities = np.empty(5, dtype=object)
impossibilities[:] = impos1, impos2, impos3, impos4, impos5

"""
Algorithm that parses through the word list and assigns each word a score based on the number of entries that share the
same letter in the same spot. It will return the word with the greatest score, or in cases where the score is shared, the
first word alphabetically with the highest score.
"""
def best_guess():
    hashes = [None] * 5
    for i in range(5):
        hashes[i] = {'a' : 0, 'b' : 0, 'c' : 0, 'd' : 0,'e' : 0, 'f' : 0, 'g' : 0, 'h' : 0, 'i' : 0, 'j' : 0, 'k' : 0, 'l' : 0,
        'm' : 0, 'n' : 0, 'o' : 0, 'p' : 0, 'q' : 0, 'r' : 0, 's' : 0, 't' : 0,'u' : 0, 'v' : 0, 'w' : 0, 'x' : 0, 'y' : 0, 'z' : 0}

    scores = {}

    for element in word_list[0]:
        scores[element] = 0
        for i in range(5):
            hashes[i][element[i]] += 1

    for elements in word_list[0]:
        for i in range(5):
            scores[elements] = scores[elements] + hashes[i][elements[i]]


    return max(scores, key=scores.get)

def feedback():
    #Wait for 2 seconds
    time.sleep(2)

    print("Enter * for correct entries in the correct spot\nEnter / for correct entries in an incorrect spot\nEnter _ for incorrect entries\n")
    global Input
    Input = input("Feedback: ")

    #Stop execution if invalid input is received or if the guess was correct
    if len(Input) != 5:
        sys.exit("Invalid feedback entry.")
    elif Input == '*****':
        sys.exit("Congrats!")

##################################End of Setup##############################################
#############################################################################################
#############################################################################################
#############################################################################################

first_guess = best_guess()

print(f"Start with {first_guess.upper()} as your first guess.\n")

feedback()

for i in range(5):
    if Input[i] == '_':
        not_contained = not_contained + [first_guess[i]]
    elif Input[i] == '/':
        impossibilities[i,] += [first_guess[i]]
        if first_guess[i] not in must_contain:
           must_contain += [first_guess[i]]
    elif Input[i] == '*':
        word_list = word_list[word_list[0].str[i] == first_guess[i]]
        correct_word[i] = first_guess[i]
    else:
        sys.exit("Invalid feedback entry.")

#Add wrong letters to the list of impossibilities
for ele in impossibilities:
    ele += not_contained

#Filter out results that contain impossible letter entries
for i in range(5):
    word_list = word_list[~np.isin(word_list[0].str[i], impossibilities[i])]

#If we know certain letters must be in the word, remove words that don't contain such letters
if(len(must_contain) != 0):
    for ele in must_contain:
        word_list = word_list[word_list[0].str.contains(ele)]

#Offer new guess
print(f"Now try {best_guess().upper()} as your next guess.\n")

feedback()

while True:
    new_guess = best_guess()
    for i in range(5):
        if Input[i] == '*':
            word_list = word_list[word_list[0].str[i] == new_guess[i]]
            correct_word[i] = new_guess[i]
        elif Input[i] == '/':
            impossibilities[i,] += [new_guess[i]]
            if new_guess[i] not in must_contain:
                must_contain += [new_guess[i]]
            for ind in [i-4,i-3,i-2,i-1]:
                if new_guess[ind] == new_guess[i] and (Input[ind] == '/' or Input[ind] == "*"):
                    word_list = word_list[word_list[0].str.count(new_guess[i]) > 1]
        elif Input[i] == '_':
            if new_guess[i] not in must_contain and new_guess[i] not in correct_word and new_guess[i] not in not_contained:
                if not any(new_guess[i] == new_guess[i - x] for x in range(1,5)):
                        not_contained += [new_guess[i]]
                else:
                    for ind in [i-1,i-2,i-3,i-4]:
                        if new_guess[ind] == new_guess[i] and (Input[ind] == '_'):
                            not_contained += [new_guess[i]]
                        else:
                            word_list = word_list[word_list[0].str.count(new_guess[i]) == int((new_guess[i-1] == new_guess[i]) and (Input[i-1] != '_'))+int((new_guess[i-2] == new_guess[i]) and (Input[i-2] != '_'))+int((new_guess[i-3] == new_guess[i]) and (Input[i-3] != '_'))+int((new_guess[i-4] == new_guess[i]) and (Input[i-4] != '_'))]
            elif new_guess[i] in not_contained:
                break
            elif new_guess[i] in must_contain:
                impossibilities[i,] += [new_guess[i]]
                word_list = word_list[word_list[0].str.count(new_guess[i]) == 1]
            else:
                for ind in [correct_word.index(new_guess[i])-4,correct_word.index(new_guess[i])-3,correct_word.index(new_guess[i])-2,correct_word.index(new_guess[i])-1]:
                    impossibilities[ind,] += [new_guess[i]]   
        else:
            sys.exit("Invalid feedback entry.")

    #Add wrong letters to the list of impossibilities
    for ele in impossibilities:
        ele += not_contained

    #Filter out results that contain impossible letter entries
    for i in range(5):
        word_list = word_list[~np.isin(word_list[0].str[i], impossibilities[i])]

    #If we know certain letters must be in the word, remove words that don't contain such letters
    if(len(must_contain) != 0):
        for ele in must_contain:
            word_list = word_list[word_list[0].str.contains(ele)]

    #Offer new guess
    print(f"Now try {best_guess().upper()} as your next guess.\n")

    feedback()