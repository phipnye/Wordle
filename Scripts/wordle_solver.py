### Setup
import pandas as pd
import numpy as np
import seaborn as sns
import warnings
import sys
import time
import re
import os

# Relative file pathing
def CD(x = ''):
    return os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), x)
def OUTPUT(x = ''):
    return os.path.join(CD(), 'Output', x)
def INPUT(x = ''):
    return os.path.join(CD(), 'Input', x)

# Word list data.frame
word_list = pd.read_csv(INPUT('word_list.csv'), names=['Word'], dtype=str)
# CSV that stores the correct word and the number of tries it took when the correct word is found
results_file = OUTPUT('results.txt')

# Split the letters of each word out wide
letter_cols = ['Letter' + str(i) for i in np.arange(5)]
word_list[letter_cols] = word_list['Word'].str.split('', n=5, expand=True).iloc[:,1:6]

# Initialize a variable to hold the number of tries
n_tries = 0

"""
Algorithm that parses through the word list and assigns each word a score based on the number of entries that share the
same letter in the same spot. It will return the word with the greatest score, or in cases where the score is shared, 
the first word alphabetically with the highest score.
"""
def calculate_score(word_scores: pd.DataFrame, word: str) -> int:
    word_letters = np.array(list(word), dtype=str)
    matches = (word_scores[letter_cols] == word_letters).sum().sum()
    return matches

def best_guess(word_list: pd.DataFrame) -> str:
    word_list['Score'] = word_list['Word'].apply(lambda x: calculate_score(word_list, x))
    # Return the (first) word with the greatest score
    return word_list[word_list['Score'] == word_list['Score'].max()]['Word'].values[0]

"""
Function that receives feedback from the user based on the guess provided in best_guess
"""
def feedback(guess: str, num_tries: int) -> (bool, str):
    # Wait for 1 second
    time.sleep(1)

    while True:
        print(
            'Enter "*" for correct entries in the correct spot\n'
            'Enter "/" for correct entries in an incorrect spot\n'
            'Enter "_" for incorrect entries\n'
            'Enter "stop" to exit\n'
            )
        fdbk = input('Feedback: ')

        # Exit the program if the user specifies
        if fdbk == 'stop':
            running = False
            msg = 'Exiting'

        # Continue asking for input unless it's 5 contiguous valid characters
        elif not bool(re.match('^[*/_]{5}$', fdbk)):
            print('Invalid feedback\n')
            continue

        # Record the word and the number of tries if the guess was correct
        elif fdbk == '*****':
            with open(results_file, 'a') as fil:
                fil.write(guess + ',' + str(num_tries) + '\n')
            all_res = pd.read_csv(results_file, names=['Word', 'Number of guesses'], dtype={'Word': 'str', 'Number of guesses': 'category'})
            warnings.filterwarnings("ignore", category=FutureWarning, module="seaborn")
            (
                sns.histplot(data=all_res, x='Number of guesses', stat='count', discrete=True, color='blue')
                .get_figure()
                .savefig(re.sub(r'\.txt$', '.png', results_file))
            )
            running = False
            msg = 'Congrats!'

        # Continue running if the correct answer was not found yet and the user did not specify to stop playing
        else:
            running = True
            msg = fdbk
        
        return running, msg

### End of Setup

### Run the program

if __name__ == '__main__':
    running = True

    # Continue running until the user gets the correct answer or requests to stop playing
    while running:
        if not word_list.shape[0]:
            sys.exit('Sorry, the correct answer could not be found.')
        
        # Generate new guess
        new_guess = best_guess(word_list)
        new_guess_arr = np.array(list(new_guess), dtype=str)
        n_tries += 1

        # Offer new guess and gather feedback
        print(f'Try {new_guess.upper()} as your next guess.\n')
        running, fdbk = feedback(new_guess, n_tries)

        if running:
            fdbk_arr = np.array(list(fdbk), dtype=str)
            
            for i, result in enumerate(fdbk_arr):
                # If our guess provided the correct letter in the correct position, subset down to rows that meet that criteria
                if result == '*':
                    word_list = word_list[word_list['Letter' + str(i)] == new_guess_arr[i]]
                
                # If our letter was correct but in the wrong position
                elif result == '/':
                    # Remove entries with the same letter in the same position
                    word_list = word_list[word_list['Letter' + str(i)] != new_guess_arr[i]]
                    # Make sure this letter isn't a repeat to prevent filtering that's already been applied
                    if not ((new_guess_arr[:i] == new_guess_arr[i]) & (fdbk_arr[:i] == '/')).any():
                        # Subset down to rows where the word contains the correct number of the given letter
                        num_mat = ((new_guess_arr == new_guess_arr[i]) & np.isin(fdbk_arr, ['*', '/'])).sum()
                        word_list = word_list[word_list['Word'].str.count(new_guess_arr[i]) >= num_mat]
                
                # If our letter was entirely incorrect
                else:
                    # Make sure this letter wasn't marked as correct before subsetting down to words that don't contain the corresponding letter
                    prev_matches = ((new_guess_arr == new_guess_arr[i]) & np.isin(fdbk_arr, ['*', '/']))
                    if not prev_matches.any():
                        word_list = word_list[~word_list['Word'].str.contains(new_guess_arr[i])]
                    else:
                        word_list = word_list[word_list['Word'].str.count(new_guess_arr[i]) == prev_matches.sum()]
                        word_list = word_list[word_list['Letter' + str(i)] != new_guess_arr[i]]

        else:
            game_res = fdbk

    print(game_res)

# EOF