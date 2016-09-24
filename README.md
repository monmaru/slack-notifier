# slack-notifier
[tweet-analyzer](https://github.com/t-analyzers/tweet-analyzer)の分析結果をSlackに通知するツールです。  

## Requirements & Install
- python 3.4+  
```
pip install -r requirements.txt
```

## Usage

### Settings
**setting.yml**に設定を記載してください。  
- slack  
  - token  
  Slack APIトークン  
  - channel  
  通知対象のチャンネル名  
- data
  - dir  
  分析結果の出力パス  
  ex: '/Users/hoge/t-analyzers.github.io/data/'  

### Run
分析完了後に下記コマンドを実行してください。  
```
python slack.py
```

## License
[MIT](http://opensource.org/licenses/MIT)