import torch
from tqdm import tqdm

from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation import GenerationConfig

from utils.general_utils import *
from utils.data_utils import load_yaml, get_pathmmu_data, construct_prompt, save_json, CAT_SHORT2LONG
from utils.model_utils import call_blip2_engine_df, call_llava_engine_df, call_QwenVL_engine_df,\
    blip_image_processor, llava_image_processor
from llava.model.builder import load_pretrained_model
from llava.mm_utils import tokenizer_image_token, get_model_name_from_path, KeywordsStoppingCriteria
from lavis.models import load_model_and_preprocess
from utils.eval_utils import evaluate, get_multi_choice_prediction



def run_model(samples, model, call_model_engine_fn=None, tokenizer=None):
    out_samples = []
    for sample in tqdm(samples):
        try:
            response = call_model_engine_fn(sample, model, tokenizer)
        except Exception as e:
            print(e)
            print('Error in sample:')
            print(sample)
            continue
        pred_ans = get_multi_choice_prediction(response, sample['all_choices'], sample['index2ans'])
        if response == sample['gt_content']:
            pred_ans = sample['gt_content']
        out_samples.append({'No': sample['No'],
                            'img_path': sample['img_path'],
                            'question': sample['question'],
                            'gt_content': sample['gt_content'],
                            'response': response,
                            'answer': sample['answer'],
                            'pred_ans': pred_ans,
                            'all_choices': sample['all_choices'],
                            'index2ans': sample['index2ans'],
                            'prompt': sample['final_input_prompt'],
                            })
    return out_samples


def main():
    parser = ArgumentParser()
    parser.add_argument('--exp_name', type=str, default='',
                        help='The name of the experiment')
    parser.add_argument('--config_path', type=str, default="configs/blip2_t5.yaml")
    parser.add_argument('--data_path', type=str, default="../data", help="The path to data root directory.")
    parser.add_argument('--categories', nargs='+',
                        help=f'The name of the pathmmmu sub-category. Availble: {CAT_SHORT2LONG.keys()}')
    parser.add_argument('--model_type', type=str, default="pretrain_flant5xl")
    parser.add_argument('--mmodel_type', type=str, default="blip2_t5")
    parser.add_argument('--model_path', type=str, default="")
    args = parser.parse_args()
    if args.categories[0] == 'ALL':
        args.categories = CAT_SHORT2LONG.keys()
    device = torch.device("cuda") if torch.cuda.is_available() else "cpu"


    call_model_engine_dict = {
        'Qwen-VL': call_QwenVL_engine_df,
        'blip2_t5': call_blip2_engine_df,
        'blip2_t5_instruct': call_blip2_engine_df,
        'llava': call_llava_engine_df,
    }
    vis_process_func_dict = {
        'Qwen-VL': None,
        'blip2_t5': blip_image_processor,
        'blip2_t5_instruct': blip_image_processor,
        'llava': llava_image_processor
    }
    call_model_engine = call_model_engine_dict[args.mmodel_type]
    tokenizer = None
    if args.mmodel_type in ['blip2_t5', 'blip2_t5_instruct']:
        print('blip/instructblip initializing.....')
        vis_process_func = vis_process_func_dict[args.mmodel_type]
        model, vis_processors, _ = load_model_and_preprocess(name=args.mmodel_type,
                                                             model_type=args.model_type,
                                                             is_eval=True,
                                                             device=device)
    elif args.mmodel_type in ['llava']:
        print('llava initializing.....')
        vis_process_func = vis_process_func_dict[args.mmodel_type]
        model_name = get_model_name_from_path(args.model_path)
        tokenizer, model, vis_processors, _ = load_pretrained_model(args.model_path, None,
                                                                    model_name)
    elif args.mmodel_type in ['Qwen-VL']:
        print('qwenvl initializing.....')
        tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(args.model_path, device_map="cuda",
                                                     trust_remote_code=True).eval()
        model.generation_config = GenerationConfig.from_pretrained(args.model_path, trust_remote_code=True)
        call_model_engine = call_QwenVL_engine_df
        vis_process_func = None
        vis_processors = None
    else:
        raise NotImplementedError(f'model type {args.mmodel_type} is not implemented')

    # load config and process to one value
    args.config = load_yaml(args.config_path)
    for key, value in args.config.items():
        if key != 'eval_params' and type(value) == list:
            assert len(value) == 1, 'key {} has more than one value'.format(key)
            args.config[key] = value[0]

    # run for each category
    for cat_short in args.categories:
        category = CAT_SHORT2LONG[cat_short]
        print("#" * 50, f"Running {category}", "#" * 50)
        sub_dataset = get_pathmmu_data(args.data_path, category)

        samples = []
        for sample in sub_dataset:
            try:
                sample = construct_prompt(sample, args.config)
            except Exception as e:
                print(e)
                print('error occurs in constructing prompt!!!')
                print(sample)
                continue
            if args.mmodel_type in ['llava', 'blip2_t5', 'blip2_t5_instruct']:
                sample['image'] = vis_process_func(sample['img_path'], vis_processors).to(device)
            elif args.mmodel_type in ['Qwen-VL']:
                pass
            else:
                raise NotImplementedError(f'model type {args.mmodel_type} is not implemented')
            samples.append(sample)

        # run ex
        out_samples = run_model(samples, model, call_model_engine, tokenizer)

        # save resutls
        # output dir
        output_dir = os.path.join('outputs', args.exp_name, category)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        save_output_path = os.path.join(output_dir, 'output.json')
        save_result_path = os.path.join(output_dir, 'result.json')

        judge_dict, metric_dict = evaluate(out_samples)
        for out_sample in out_samples:
            out_sample.update({"judge": judge_dict[out_sample['No']]})

        save_json(save_output_path, out_samples)
        metric_dict.update({"num_example": len(out_samples)})
        save_json(save_result_path, metric_dict)

if __name__ == '__main__':
    main()
