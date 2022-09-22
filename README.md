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

