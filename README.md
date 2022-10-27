# 情境数据处理



## 监听上传

`src/watching_upload.py`：监听文件夹，将内部文件上传并实时上传新建的文件

- 指定`-c config.yml`来读取程序设置

使用Docker运行：首先修改`docker-compose.yml`里挂载的数据路径，然后在`src/config.yml`里配置要监听的数据文件夹，最后在根目录运行

```sh
docker-compose up -d
```



## Elasticsearch & Kibana 配置

参见：[Elasticsearch & Kibana 配置](./elastic_kibana/README.md)



## Elasticdump使用

进入`elasticdump`文件夹，需要配置：

- 在`config_auth`中配置ES用户名和密码（从`config_auth_template`拷贝）；
- 在`command.sh`中配置index及其他elasticdump参数。

两种运行方法：

- 如果已经装好elasticdump，可以在指定输出文件名后运行`command.sh`脚本

  ```sh
  ./command.sh <输出文件名>
  ```

- 如果使用docker方法，可以在指定输出文件名后运行`run_docker_elasticdump.sh`脚本

  ```sh
  ./run_docker_elasticdump.sh <输出文件名>
  ```



## Jupyter-GPU Docker配置

参见：[Jupyter-GPU Docker配置](./jupyter_gpu/README.md)

