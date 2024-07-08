exp_name='Qwen-VL_pathmmu'
CUDA_VISIBLE_DEVICES=3 python main.py \
--exp_name ${exp_name} \
--config_path configs/qwenvl.yaml \
--mmodel_type "Qwen-VL" \
--model_path /mnt/Xsky/syx/model/LMM/Qwen-VL-Chat \
--categories ALL

