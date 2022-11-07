# Jupyter-GPU Docker配置

如果docker compose在v1.28.0+，可以直接运行：

```sh
docker-compose up -d
```

否则，运行：

```sh
./start_docker.sh
```



## 镜像构建

- 在`image`文件夹运行`build_image.sh`构建`atomie/gpu-jupyter:v1.4_cuda-11.2_ubuntu-20.04_slim_updated`
- 在`image-squash`文件夹运行`build_squash_image.sh`构建`atomie/gpu-jupyter:squash`（依赖`atomie/gpu-jupyter:v1.4_cuda-11.2_ubuntu-20.04_slim_updated`）

