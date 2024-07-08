from typing import Dict
from tabulate import tabulate
from utils.general_utils import *
from utils.data_utils import  CAT_SHORT2LONG, DOMAIN_CAT2SUB_CAT

def calculate_ins_level_acc(results: Dict):
    """calculate the instruction level accuracy for given category results"""
    acc = 0
    ins_num = 0
    for cat_name, cat_results in results.items():
        acc += cat_results['acc'] * cat_results['num_example']
        ins_num += cat_results['num_example']
    if ins_num == 0:
        return 0
    return acc / ins_num

def main():
    parser = ArgumentParser()
    parser.add_argument('--exp_name', type=str, default='blip2_flant5xl_pathology',
                        help='The name of the experiment')
    parser.add_argument('--output_path', type=str, default="./outputs", help="The path to data root directory.")

    args = parser.parse_args()

    ex_output_path = os.path.join(args.output_path, args.exp_name)

    # load all results
    all_results = {}
    for cat_folder_name in os.listdir(ex_output_path):
        if cat_folder_name in CAT_SHORT2LONG.values():
            cat_folder_path = os.path.join(ex_output_path, cat_folder_name)
            cat_results = json.load(open(os.path.join(cat_folder_path, 'result.json')))
            
            all_results[cat_folder_name] = cat_results

    # print results
    headers = ['Category', 'Acc', 'Data Num']
    table = []

    # for cat_name, cat_results in all_results.items():
    #     table.append([cat_name, round(cat_results['acc'], 3), int(cat_results['num_example'])])
    
    # add domain category
    for domain, in_domain_cats in DOMAIN_CAT2SUB_CAT.items():
        in_domain_cat_results = {}
        for cat_name in in_domain_cats: # use the order in DOMAIN_CAT2SUB_CAT
            if cat_name in all_results.keys():
                in_domain_cat_results[cat_name] = all_results[cat_name]
            else:
                pass
        in_domain_ins_acc = calculate_ins_level_acc(in_domain_cat_results)
        in_domain_data_num = np.sum([cat_results['num_example'] for cat_results in in_domain_cat_results.values()])
        table.append(['Overall-' + domain, round(in_domain_ins_acc, 3), int(in_domain_data_num)])
        # add sub category
        for cat_name, cat_results in in_domain_cat_results.items():
            table.append([cat_name, round(cat_results['acc'], 3), int(cat_results['num_example'])])
        # table.append(["-----------------------------", "-----", "----"])

    # table.append(["-----------------------------", "-----", "----"])
    all_ins_acc = calculate_ins_level_acc(all_results)
    table.append(['Overall', round(all_ins_acc, 3), np.sum([cat_results['num_example'] for cat_results in all_results.values()])])
    # table.append(['Overall', np.mean([cat_results['acc'] for cat_results in all_results.values()]), np.sum([cat_results['num_example'] for cat_results in all_results.values()])])
    print(tabulate(table, headers=headers, tablefmt='orgtbl'))


if __name__ == '__main__':
    main()
