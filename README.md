## 概要
- 各関数毎にDockerを作成し起動はPytestを起動しています。これはCICD用です。

## Localテスト方法
- Docker Build
  ``` 
  docker build -t docker-image:test .
  ```
- Docker 起動(Test)
  ``` 
  docker run -p 9000:8080 docker-image:test

  ```
 

## 関数
- hello-sample-01
- 