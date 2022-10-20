docker stop context-jupyter
docker rm context-jupyter
docker run --gpus all -d -it --name context-jupyter --restart always -p 29503:8888 -v $(pwd)/data:/home/jovyan -e GRANT_SUDO=yes -e JUPYTER_ENABLE_LAB=yes -e NOTEBOOK_ARGS="--collaborative" --user root cschranz/gpu-jupyter:v1.4_cuda-11.2_ubuntu-20.04_slim
