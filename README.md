# AWS Resource Tool
## 概要
- 開発環境のECS, RDS, EC2, EventBridgeのコスト削減用の起動停止Lambda
- 起動ルール：平日はResourceを起動するが、土、日、祝日は起動しない。
- 停止ルール：無条件で実行する。

#### 前提条件
- 祝日情報を取得するために外部通信が必要。もし外部通信が出来ない状況であれば祝日でも平日とみなし、起動を行います。  
- 起動・停止コマンドが正しく実行されたかのチェックのみで本当に起動、停止出来るかはまた別の問題となり検知する機能は有していません。  
- RDS
  - SingleAZのみの対応(MultiAZは、インスタンス単位ではなくクラスター単位となり現在は未対応)  
- EC2
  - 特になし
- EventBridge
  - グループ名はdefault以外は未対応
  
### 機能説明  
- 開発環境のリソースの自動起動・自動停止を想定したLambda  
- 自動起動について  
  - システム日付が平日のみ起動します。  
  - 土・日、祝日は、Lambdaを実行しても起動処理は行いません。
- 自動停止について  
  - 自動停止はLambda起動時のシステム日付の祝日、平日に関わらず停止を行います。
- 祝日判定について  
  - 内閣府サイトから情報を取得して判定しています。(https://www.cao.go.jp/)  
- ECSについて  
  - クラスター名、サービス名、起動時の必要タスク数を指定する。  
  - 複数のクラスーを指定可能  
- RDSについて  
  - Private Subnetの場合でも動作可能。  
  - 複数DBインスタンスを操作したい場合は、リスト型でインスタンス名を指定する。  
- EC2について  
  - インスタンスIDを指定します。
  - 複数のEC2インスタンスを指定可能  
  - EC2に停止保護されている場合は、スキップ(Default)するか解除して停止するか指定できます。
- EventBridgeについて  
  - 複数EventBridgeを操作したい場合は、リスト型で名前を指定する。  
#### 利用方法
1. Lambda起動パラメータ設定
   - serverless/dev.yml
   - 詳細下段の「Lambda起動時のパラメータについて参照」

2. aws configure 設定
  
3. serverless framework install & deploy コマンド
    ```
    npm install
    serverless deploy
    ```


#### Lambda起動時のパラメータについて
- 下記フォーマットのパラメータを指定する。
- 利用しないリソースでも[ ] などを設定する必要あり
- ファイル：serverless/{env}.yml 
```

 { 
   'switch': 'on' or 'off',               # 起動 or 停止
   'region': ['ap-northeast-1'],          # 停止したいリージョン
   'EcsService': [{
      'cluster': 'ecs cluster name'       # ECSクラスター名
      'service': 'ecs servicename'        # ECSサービス名
      'desiredCount': 2                   # 起動数
   }],
   'DBInstanceIdentifier': ['XXXX'],      # DBインスタンス名
   'EC2' : {                              # EC2
      'instance' : [],                    # EC2インスタンス名
      'stopMode' : 'normal'  or 'hard'    # 停止モード(hardは停止保護されている場合解除して停止します)
   },
   'EventBridge': ['XXXX'],               # EventBridge名
  }

```

## 関数
- func/on-off/src/lambda_function.handler

### 補足
- DockerはPytestを実行します。

## Pytest方法
- Docker Build
  ``` 
  cd func/on-off
  docker build -t docker-image:test .
  ```
- Docker 起動(Test)
  ``` 
  docker run -p 9000:8080 docker-image:test
  ``` 
