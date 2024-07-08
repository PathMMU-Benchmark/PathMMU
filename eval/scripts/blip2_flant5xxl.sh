exp_name='blip2_flant5xxl_pathmmu'
CUDA_VISIBLE_DEVICES=2 python main.py \
--exp_name ${exp_name} \
--model_type "pretrain_flant5xxl" \
--mmodel_type "blip2_t5" \
--config_path configs/blip2.yaml \
--categories ALL
