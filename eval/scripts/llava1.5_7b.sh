exp_name='llava1.5_7b_pathmmu'
CUDA_VISIBLE_DEVICES=2 python main.py \
--exp_name ${exp_name} \
--config_path configs/llava1.5.yaml \
--mmodel_type "llava" \
--model_path /mnt/Xsky/syx/model/llava_vicuna/llava-v1.5-7b \
--categories ALL

