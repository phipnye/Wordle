import pandas as pd
import numpy as np
import sys
import time

#Import Possible Words
word_list = pd.read_csv("word_list.csv", header=None)

#Declare list of letters that are invalid for a given position
impos1 = []
impos2 = []
impos3 = []
impos4 = []
impos5 = []

#List of the letters that must be contained using the unique values in the impossibilities lists
must_contain = []

#Dictionary of the correct word
correct_word = [None] * 5

#Initialize an array of the impossibilities for each position
impossibilities = np.empty(5, dtype=object)
impossibilities[:] = impos1, impos2, impos3, impos4, impos5

"""
Algorithm that parses through the word list and assigns each word a score based on the number of entries that share the
same letter in the same spot. It will return the word with the greatest score, or in cases where the score is shared, the
first word alphabetically with the highest score.
"""
def best_guess():
    #Declare an empty list of size 5
    hashes = [None] * 5

    #Now initialize the elements of that with dictionaries containing each letter and their corresponding scores (starting at 0)
    for i in range(5):
        hashes[i] = {'a' : 0, 'b' : 0, 'c' : 0, 'd' : 0,'e' : 0, 'f' : 0, 'g' : 0, 'h' : 0, 'i' : 0, 'j' : 0, 'k' : 0, 'l' : 0,
        'm' : 0, 'n' : 0, 'o' : 0, 'p' : 0, 'q' : 0, 'r' : 0, 's' : 0, 't' : 0,'u' : 0, 'v' : 0, 'w' : 0, 'x' : 0, 'y' : 0, 'z' : 0}

    #Declare an empty dictionary that stores the scores of each letter
    scores = {}

    #Iterate through the word list and assign each word an initial score of 0
    for element in word_list[0]:
        scores[element] = 0
        #Now iterate through the hashes and add to the score of the corresponding letter in the ith position
        for i in range(5):
            hashes[i][element[i]] += 1

    #Now iterate through the word list again and now assign scores to the entire word based on the hashes dictionary scores
    for elements in word_list[0]:
        for i in range(5):
            scores[elements] = scores[elements] + hashes[i][elements[i]]

    #Return the word with the greatest score
    return max(scores, key=scores.get)

"""
Function that receives feedback from the user based on the guess provided in best_guess
"""
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

#Generate first guess
first_guess = best_guess()

#First guess is SLATE
print(f"Start with {first_guess.upper()} as your first guess.\n")

#Get feedback on the word slate
feedback()

#Modify word_list, must_contain, or impossibilities based on the feeback received on SLATE
for i in range(5):
    #If the feedback indicates a grey letter
    if Input[i] == '_':
        #Note: no need to worry about repeated letters in SLATE
        for ind in range(5):
                #Add the letter to each element of impossibilities
                impossibilities[ind,] += [first_guess[i]]

    #If the feedback indicates a yellow leter
    elif Input[i] == '/':
        #Add the letter to the corresponding element in impossibilities
        impossibilities[i,] += [first_guess[i]]
        #And, if it's not already in must_contain, add it
        if first_guess[i] not in must_contain:
           must_contain += [first_guess[i]]

    #If the feedback indicates a green letter
    elif Input[i] == '*':
        #Filter the word list to only words that contain the corresponding letter in the corresponding spot
        word_list = word_list[word_list[0].str[i] == first_guess[i]]
        #And initialize the ith element of the correct_word list with the corresponding letter
        correct_word[i] = first_guess[i]

    #Otherwise, some other character was received for feedback, so end the program and notify the user of the issue
    else:
        sys.exit("Invalid feedback entry.")

#Filter out results that contain impossible letter entries
for i in range(5):
    word_list = word_list[~np.isin(word_list[0].str[i], impossibilities[i])]

#If we know certain letters must be in the word, remove words that don't contain such letters
if(len(must_contain) != 0):
    for ele in must_contain:
        word_list = word_list[word_list[0].str.contains(ele)]

#Offer new guess
print(f"Now try {best_guess().upper()} as your next guess.\n")

#Receive feedback on new word
feedback()

#Continue running until the sys.exit is called.
while True:
    #Generate new guess and assign it to new_guess
    new_guess = best_guess()
    #Iterate through the feedback now
    for i in range(5):
        #If the feedback indicates a green letter
        if Input[i] == '*':
            #Filter the word list to only words that contain the corresponding letter in the corresponding spot
            word_list = word_list[word_list[0].str[i] == new_guess[i]]
            #And initialize the ith element of the correct_word list with the corresponding letter
            correct_word[i] = new_guess[i]
        
        #If the feedback indicates a yellow leter
        elif Input[i] == '/':
            #Add the letter to the corresponding element in impossibilities
            impossibilities[i,] += [new_guess[i]]
            #And, if it's not already in must_contain, add it
            if new_guess[i] not in must_contain:
                must_contain += [new_guess[i]]
            for ind in [i-4,i-3,i-2,i-1]:
                #If there is a repeated letter and both receive feedback that is not `_`
                if new_guess[ind] == new_guess[i] and (Input[ind] == '/' or Input[ind] == "*"):
                    #Filter the word list to words that contain more than one of the corresponding letter
                    word_list = word_list[word_list[0].str.count(new_guess[i]) > 1]
        
        #If the feedback indicates a grey letter
        elif Input[i] == '_':
            #If the corresponding letter is not in correct_word, must_contain, and every element of impossibilities
            if new_guess[i] not in must_contain and new_guess[i] not in correct_word and all(new_guess[i] not in impossibilities[x] for x in range(5)):
                #If there isn't a repetition of the corresponding letter in new_guess
                if not any(new_guess[i] == new_guess[i - x] for x in range(1,5)):
                        for n in range(5):
                            #Add the corresponding letter to every element of impossibilities
                            impossibilities[n,] += [new_guess[i]]
                #If there is a repetition of the corresponding letter in new_guess
                else:
                    #For all other indeces
                    for ind in [i-1,i-2,i-3,i-4]:
                        #Check for where the repetition occurs and check the feedback given for the index of where the repetition occurs
                        #If the feedback on the repetition indicates it's a grey letter too
                        if new_guess[ind] == new_guess[i] and (Input[ind] == '_'):
                            for n in range(5):
                                #Add the corresponding letter to every element of impossibilities
                                impossibilities[n,] += [new_guess[i]]
                        #If the feedback on the repetition indicates anything other than a grey letter
                        else:
                            #Filter out words that don't contain a sufficient number of the repeating letter
                            word_list = word_list[word_list[0].str.count(new_guess[i]) == sum([(new_guess[i-x] == new_guess[i]) and (Input[i-x] != '_') for x in range(1,5)])]
                            break
            #Otherwise, if every element of impossibilities already contains the corresponding letter
            elif all(new_guess[i] in impossibilities[x] for x in range(5)):
                #Do nothing and go on to next iteration of the initial for loop
                break
            #Otherwise, if the corresponding letter is in must_contain
            elif new_guess[i] in must_contain:
                if new_guess[i] in new_guess[(i+1):]:
                    impossibilities[i,] += new_guess[i]
                    break
                for ind in range(5):
                    if new_guess[i] != correct_word[ind]:
                        #Add the letter to the corresponding element in impossibilities
                        impossibilities[ind,] += [new_guess[i]]
                #And, if it's not already in must_contain, add it
                if new_guess[i] not in must_contain:
                    must_contain += [new_guess[i]]
            #Otherwise, if the corresponding letter is in correct_word
            else:
                #For all other indeces in correct_word, other than the one that is already contained by the correct letter
                for ind in [correct_word.index(new_guess[i])-4,correct_word.index(new_guess[i])-3,correct_word.index(new_guess[i])-2,correct_word.index(new_guess[i])-1]:
                    #Add the corresponding letter to the other elements of impossibilities
                    impossibilities[ind,] += [new_guess[i]]   
    
        #Otherwise, some other character was received for feedback, so end the program and notify the user of the issue
        else:
            sys.exit("Invalid feedback entry.")

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