# slack-notifier
[tweet-analyzer](https://github.com/t-analyzers/tweet-analyzer)の分析結果をSlackに通知するツールです。  

## Requirements & Install
- python 3.5+  
```
pip install -r requirements.txt
```

## Usage

### Settings
**setting.yml**に下記項目を設定してください。  
```
slack:
  bot-token: 'xoxp-xxxxxxx' # BotのAPIトークン
  user-token: 'xoxp-xxxxxxx' # ユーザーのAPIトークン
  channel: '#analysisresult' # 通知対象のチャンネル名
data:
  dir: '/Users/hoge/t-analyzers.github.io/data/' # 分析結果の出力パス
```

### Run
分析完了後に下記コマンドを実行してください。  
```
python slack.py
```

## License
[MIT](http://opensource.org/licenses/MIT)