exp_name='llava1.5_13b_pathmmu'
CUDA_VISIBLE_DEVICES=3 python main.py \
--exp_name ${exp_name} \
--config_path configs/llava1.5.yaml \
--mmodel_type "llava" \
--model_path /mnt/Xsky/syx/model/llavav1.5/llava-v1.5-13b \
--categories ALL

