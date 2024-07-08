### Env Setup

#### To run BLIP2 and InstructBLIP models
```
conda create -n pathmmmu python=3.8.13 
conda activate pathmmmu
pip install -r requirements

# install up-to-date lavis
cd ./eval/src
git clone https://github.com/salesforce/LAVIS.git
cd LAVIS
pip install -e .

pip install tabulate
```

#### To llava
refer to https://github.com/haotian-liu/LLaVA
```
cd src/
git clone https://github.com/haotian-liu/LLaVA.git
cd LLaVA

conda create -n llava python=3.10 -y
conda activate llava
pip install --upgrade pip  # enable PEP 660 support
pip install -e .

pip install tabulate
```