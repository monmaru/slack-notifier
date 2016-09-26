import os
from datetime import datetime, timedelta
import time
import asyncio
from typing import Dict, List
# noinspection PyPackageRequirements
import yaml
from slacker import Slacker
from message import MessageBuilder


# !/usr/bin/env python
# -*- coding: utf-8 -*-


class SlackWrapper(object):
    BOT_NAME = 't-analyzers-bot'
    ICON_EMOJI = ':ghost:'

    def __init__(self):
        setting_file = os.path.join(os.path.dirname(__file__), 'setting.yml')
        with open(setting_file, 'r', encoding='utf-8') as file:
            setting = yaml.load(file)
            self.s_bot = Slacker(setting['slack']['bot-token'])  # type: Slacker
            self.s_user = Slacker(setting['slack']['user-token'])  # type: Slacker
            self.channel = setting['slack']['channel']
            self.data_dir = setting['data']['dir']

    async def notify(self, dt: datetime) -> None:
        """
        Slackに解析結果を通知する
        :param dt: 解析結果の日付
        """
        dt_str = dt.strftime('%Y-%m-%d')
        common_text = '■{0}の解析結果'.format(dt_str)
        message = MessageBuilder(self.data_dir)
        with message.build(dt):
            # つぶやき数
            self.s_bot.chat.post_message(
                channel=self.channel,
                text=common_text,
                attachments=message.tweet_count_attachments,
                username=self.BOT_NAME,
                icon_emoji=self.ICON_EMOJI
            )

            # つぶやき数のグラフ
            self.s_bot.files.upload(
                message.chart_path,
                title='つぶやき数の推移_{0}'.format(dt_str),
                channels=self.channel
            )

            # 特徴語ランキング
            self.s_bot.chat.post_message(
                channel=self.channel,
                text=common_text,
                attachments=message.feature_words_attachments,
                username=self.BOT_NAME,
                icon_emoji=self.ICON_EMOJI
            )

            # Word Cloud
            self.s_bot.files.upload(
                message.word_cloud_path,
                title='Word Cloud_{0}'.format(dt_str),
                channels=self.channel
            )

            # たまにファイルアップロードがうまくいかないことがあった。
            # 効果があるか分からないが、念のため別スレッドで少し待つ
            await asyncio.sleep(5)

            # Webサイトへのリンク
            self.s_bot.chat.post_message(
                channel=self.channel,
                text=message.more_info,
                username=self.BOT_NAME,
                icon_emoji=self.ICON_EMOJI
            )

    def delete_expired_files(self, dt: datetime) -> None:
        """
        有効期限切れファイルを削除する。
        :param dt: 有効期限の時刻
        """
        files = self.get_expired_file_info(dt)

        if len(files) == 0:
            return

        for file in files:
            result = self.s_user.files.delete(file['id'])
            if not result.successful:
                print(result.error)

    def get_expired_file_info(self, dt: datetime) -> List[Dict]:
        """
        有効期限切れファイル情報を取得する。
        取得に失敗した場合や有効期限切れファイルが存在しない場合は空配列を返す。
        :param dt: 有効期限の時刻
        :return: 有効期限よりも前にアップロードされたファイル情報のリスト
        """
        # This method cannot be called by a bot user.
        # https://api.slack.com/methods/files.list
        files = self.s_user.files.list(ts_to=self.to_unix_time(dt))
        if files.successful:
            return [file for file in files.body['files']]
        else:
            print(files.error)
            return []

    @staticmethod
    def to_unix_time(dt: datetime) -> float:
        return time.mktime(dt.timetuple())


def run() -> None:
    # noinspection PyBroadException
    try:
        slack = SlackWrapper()

        # 昨日のつぶやきの分析結果を通知する。
        yesterday = datetime.now() - timedelta(days=1)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(slack.notify(yesterday))
        loop.close()

        # 30日以上前にアップロードしたファイルは削除する。
        # TODO 下記実装を有効化する。
        # expired_date = datetime.now() - timedelta(days=30)
        # slack.delete_expired_files(expired_date)
    except:
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run()
