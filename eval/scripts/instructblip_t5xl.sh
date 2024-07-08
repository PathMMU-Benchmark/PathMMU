exp_name='instructblip_t5xl_pathmmu'
CUDA_VISIBLE_DEVICES=3 python main.py \
--exp_name ${exp_name} \
--model_type "flant5xl" \
--mmodel_type "blip2_t5_instruct" \
--config_path configs/instructblip.yaml \
--categories ALL
