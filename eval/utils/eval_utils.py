"""Response Parsing and Evaluation for various models"""
import re
import random
import numpy as np

random.seed(42)
# ----------- Process Multi-choice -------------

def get_multi_choice_prediction(response, all_choices, index2ans):
    for char in [',', '.', '!', '?', ';', ':', "'"]:
        response = response.strip(char)
    response = " " + response + " " # add space to avoid partial match

    index_ans = True
    ans_with_brack = False
    candidates = []
    for choice in all_choices:  # (A) (B) (C) (D)
        if f'({choice})' in response:
            candidates.append(choice)
            ans_with_brack = True

    if len(candidates) == 0:
        for choice in all_choices: # A B C D
            if f' {choice} ' in response:
                candidates.append(choice)

    # if all above doesn't get candidates, check if the content is larger than 5 tokens and try to parse the example
    if len(candidates) == 0 and len(response.split()) > 5:
        for index, ans in index2ans.items():
            if ans.lower() in response.lower():
                candidates.append(index)
                index_ans = False # it's content ans.

    if len(candidates) == 0:  # still not get answer, randomly choose one.
        pred_index = random.choice(all_choices)
    elif len(candidates) > 1:
        start_indexes = []
        if index_ans:
            if ans_with_brack: 
                for can in candidates:
                    index = response.rfind(f'({can})')
                    start_indexes.append(index) # -1 will be ignored anyway
                # start_indexes = [generated_response.index(f'({can})') for can in candidates]
            else:
                for can in candidates:
                    index = response.rfind(f" {can} ")
                    start_indexes.append(index)
        else:
            # start_indexes = [generated_response.lower().index(index2ans[can].lower()) for can in candidates]
            for can in candidates:
                index = response.lower().rfind(index2ans[can].lower())
                start_indexes.append(index)
        # get the last one
        pred_index = candidates[np.argmax(start_indexes)]
    else: # only one candidate
        pred_index = candidates[0]

    return index2ans[pred_index]


def check_is_number(string):
    try:
        float(string.replace(',', ''))
        return True
    except ValueError:
        # check if there's comma inside
        return False

def check_is_decimal(string):
    try:
        if "." in string:
            float(string)
            return True
        else:
            return False
    except ValueError:
        return False

def check_is_scientific_notation(string):
    try:
        if "e" in string:
            float(string)
            return True
        else:
            return False
    except ValueError:
        return False


def normalize_str(string):
    # check if characters in the string

    # if number, numerize it.
    string = string.strip()

    is_number = check_is_number(string)

    if is_number:
        string = string.replace(',', '')
        string = float(string)
        # leave 2 decimal
        string = round(string, 2)
        return [string]
    else: # it's likely to be a string
        # lower it 
        string = string.lower()
        if len(string) == 1:
            return [" " + string, string + " "] # avoid trivial matches
        return [string]

def extract_numbers(string):
    # Pattern for numbers with commas
    pattern_commas = r'-?\b\d{1,3}(?:,\d{3})+\b'
    # Pattern for scientific notation
    pattern_scientific = r'-?\d+(?:\.\d+)?[eE][+-]?\d+'
    # Pattern for simple numbers without commas
    pattern_simple = r'-?(?:\d+\.\d+|\.\d+|\d+\b)(?![eE][+-]?\d+)(?![,\d])'

    # Extract numbers with commas
    numbers_with_commas = re.findall(pattern_commas, string)
    # Extract numbers in scientific notation
    numbers_scientific = re.findall(pattern_scientific, string)
    # Extract simple numbers without commas
    numbers_simple = re.findall(pattern_simple, string)

    # Combine all extracted numbers
    all_numbers = numbers_with_commas + numbers_scientific + numbers_simple
    return all_numbers


# ----------- Evaluation -------------
def evaluate(samples):
    pred_correct = 0
    gold_list = []
    pred_list = []
    judge_dict = dict()
    for sample in samples:
        gold_list.append(sample['gt_content'])
        pred_list.append(sample['pred_ans'])
    for i in range(len(gold_list)):
        gold_i = gold_list[i]
        pred_i = pred_list[i] # a list of predicted answers
        correct = False

        if isinstance(gold_i, list):
            for answer in gold_i:
                if answer.lower() == pred_i.lower():
                    pred_correct += 1
                    correct = True
                    break
        else: # gold_i is a string
            if gold_i.lower() == pred_i.lower():
                pred_correct += 1
                correct = True
        if correct:
            judge_dict[samples[i]['No']] = 'Correct'
        else:
            judge_dict[samples[i]['No']] = 'Wrong'

    if len(samples) == 0:
        return {'acc': 0}
    return judge_dict, {'acc': pred_correct / len(samples)}
