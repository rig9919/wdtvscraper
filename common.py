import re

def split(title):
    # split a complete title into the title and the year
    words = re.findall('\w+', title)
    # look at the last item in the words list
    if words[len(words)-1].isdigit():
        # if it's digits, then it represents the year and the
        # second-to-last item is the end of the title
        return {'title': ' '.join(words[0:len(words)-1]), 
                'year': words[len(words)-1]}
    else:
        # if it's not, then the year is not in the name so we make one up
        # and give title the entire contents of the word list
        return {'title': ' '.join(words), 
                'year': ''}
