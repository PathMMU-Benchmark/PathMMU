import os
import json
import yaml
import re
from PIL import Image


CAT_SHORT2LONG = {
    'pdtt': 'PubMed_test_tiny',
    'pdt': 'PubMed_test',
    'pdd': 'PubMed_val',
    'clstt': 'PathCLS_test_tiny',
    'clst': 'PathCLS_test',
    'clsd': 'PathCLS_val',
    'sptt': 'SocialPath_test_tiny',
    'spt': 'SocialPath_test',
    'spd': 'SocialPath_val',
    'at': 'Atlas_test',
    'att': 'Atlas_test_tiny',
    'ad': 'Atlas_val',
    'edutt': 'EduContent_test_tiny',
    'edut': 'EduContent_test',
    'edud': 'EduContent_val'
}

DOMAIN_CAT2SUB_CAT = {
    'PubMed': ['PubMed_test_tiny', 'PubMed_test'],
    'SocialPath': ['SocialPath_test_tiny', 'SocialPath_test'],
    'Atlas': ['Atlas_test_tiny', 'Atlas_test'],
    'EduContent': ['EduContent_test_tiny', 'EduContent_test'],
    'PathCLS': ['PathCLS_test', 'PathCLS_test_tiny']
}
DOMAIN_CAT2SUB_CAT2 = {
    'dev_overall': ['PubMed_val', 'SocialPath_val', 'Atlas_val', 'EduContent_val', 'PathCLS_val'],
    'test_overall': ['PubMed_test', 'SocialPath_test', 'Atlas_test', 'EduContent_test', 'PubMed_test_tiny', 'SocialPath_test_tiny', 'Atlas_test_tiny', 'EduContent_test_tiny', 'PathCLS_test', 'PathCLS_test_tiny'],
    'test_tiny_overall': ['SocialPath_test_tiny', 'PubMed_test_tiny', 'Atlas_test_tiny', 'EduContent_test_tiny', 'PathCLS_test_tiny'],
}

# DATA LOADING
def walk_dir(data_dir, file_types=['.jpg', '.png', '.PNG', '.JPG', '.jpeg', '.JPEG']):
    path_list = []
    for dirpath, _, files in os.walk(data_dir):
        for f in files:
            for this_type in file_types:
                if f.lower().endswith(this_type):
                    path_list.append(os.path.join(dirpath, f))
                    break
    return path_list


def load_yaml(file_path):
    with open(file_path, 'r') as stream:
        try:
            yaml_dict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    return yaml_dict


def parse_img_path(text):
    matches = re.findall("<img='(.*?)'>", text)
    return matches


def get_pathmmu_data(data_root_path, category):
    with open(os.path.join(data_root_path, 'data.json')) as fp:
        data = json.load(fp)
    split = '_'.join(category.split('_')[1:])
    category = category.split('_')[0]
    samples = data[category][split]
    datas = []

    for data in samples:
        question = data['question']
        img_path = data['img']
        img_path = os.path.join(data_root_path, 'images', img_path)
        if not os.path.exists(img_path):
            print(category)
            print("Image Error, does not exist")
            print(data)
            continue
        # img = Image.open(img_path).convert('RGB')
        datas.append(
            {'No': data['No'], 'question': question, 'options': data['options'], 'answer': data['answer'], 'img_path': img_path})
    print(f"Loading {category} data done. Total {len(datas)} samples out of {len(samples)}, ratio {len(datas)/len(samples)}.")
    return datas



# DATA SAVING
def save_json(filename, ds):
    with open(filename, 'w') as f:
        json.dump(ds, f, indent=4)


def save_jsonl(filename, data):
    """
    Save a dictionary of data to a JSON Lines file with the filename as key and caption as value.

    Args:
        filename (str): The path to the file where the data should be saved.
        data (dict): The dictionary containing the data to save where key is the image path and value is the caption.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        for img_path, caption in data.items():
            # Extract the base filename without the extension
            base_filename = os.path.basename(img_path)
            # Create a JSON object with the filename as the key and caption as the value
            json_record = json.dumps({base_filename: caption}, ensure_ascii=False)
            # Write the JSON object to the file, one per line
            f.write(json_record + '\n')

def save_args(args, path_dir):
    argsDict = args.__dict__
    with open(path_dir + 'setting.txt', 'w') as f:
        f.writelines('------------------ start ------------------' + '\n')
        for eachArg, value in argsDict.items():
            f.writelines(eachArg + ' : ' + str(value) + '\n')
        f.writelines('------------------- end -------------------')


# DATA PROCESSING
def construct_prompt(sample, config):
    question = sample['question']
    options = sample['options']
    # import pdb
    # pdb.set_trace()
    example = ""
    start_chr = 'A'
    prediction_range = []
    index2ans = {}
    new_options = []
    for option in options:
        prediction_range.append(start_chr)
        option = option.split(')')[1].strip()
        new_options.append(option)
        example += f"({start_chr}) {option}\n"
        index2ans[start_chr] = option
        start_chr = chr(ord(start_chr) + 1)
    empty_prompt_sample_structure = config['multi_choice_example_format']
    empty_prompt = empty_prompt_sample_structure.format(question, example)
    res_dict = {}
    res_dict['index2ans'] = index2ans
    res_dict['correct_choice'] = sample['answer'][0]
    res_dict['all_choices'] = prediction_range
    res_dict['empty_prompt'] = empty_prompt
    res_dict['final_input_prompt'] = empty_prompt
    res_dict['gt_content'] = new_options[ord(sample['answer'][0].upper()) - ord('A')]
    res_dict.update(sample)
    return res_dict
