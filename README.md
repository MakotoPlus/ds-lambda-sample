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



## RDS 起動停止Lambdaの機能説明  
- 主に開発で利用しているリソースの自動起動・自動停止を実現するLambda  
- 自動起動はLambda起動時のシステム日付が、土・日、祝日の場合、Lambdaを実行してもRDSを起動させず、平日時のみ起動させます。  
- 自動停止はLambda起動時のシステム日付が、土・日、祝日、平日関わらず停止させます。  
- 実行する時間は、Eventにて指定して下さい。  
- 祝日情報は内閣府サイトから取得しています。(https://www.cao.go.jp/)  
- DBがPrivate Subnetの場合でも実行可能。  
- 複数のDBインスタンスを操作したい場合は、リスト型でインスタンス名を指定する  
#### 前提条件
- このLambdaは祝日情報を取得するために外部通信が必要。もし外部通信が出来ない状況であれば祝日でも平日とみなし、RDSの起動を行います。  
- MultiAZは、インスタンス単位ではなくクラスター単位となり現在は未対応  
#### Eventパラメータについて
- 起動時には、EventにJSONパラメータを渡す必要がある  
- フォーマット  
```JSON

 { 
   'switch': 'on or off',               # 起動 or 停止
   'region': ['ap-northeast-1'],          # 停止したいリージョン
   'DBInstanceIdentifier': 'XXXX',      # DBインスタンス名
   'check_date_yyyymmdd': '20230131',   # テスト用
  }

```

