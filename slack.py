import os
from datetime import datetime, timedelta
import asyncio
# noinspection PyPackageRequirements
import yaml
from slacker import Slacker
from message import MessageBuilder


# !/usr/bin/env python
# -*- coding: utf-8 -*-


class SlackBot(object):
    BOT_NAME = 't-analyzers-bot'
    ICON_EMOJI = ':ghost:'

    def __init__(self):
        setting_file = os.path.join(os.path.dirname(__file__), 'setting.yml')
        with open(setting_file, 'r', encoding='utf-8') as file:
            setting = yaml.load(file)
            self.slack = Slacker(setting['slack']['token'])  # type: Slacker
            self.channel = setting['slack']['channel']
            self.data_dir = setting['data']['dir']

    async def notify(self, target_date: datetime) -> None:
        """
        Slackに解析結果を通知する
        :param target_date: 対象とする解析結果の日付
        """
        common_text = '■{0}の解析結果'.format(target_date.strftime('%Y/%m/%d'))
        message = MessageBuilder(self.data_dir)
        with message.build(target_date):
            # つぶやき数
            self.slack.chat.post_message(
                channel=self.channel,
                text=common_text,
                attachments=message.tweet_count_attachments,
                username=self.BOT_NAME,
                icon_emoji=self.ICON_EMOJI
            )

            # つぶやき数のグラフ
            self.slack.files.upload(
                message.chart_path,
                title='つぶやき数の推移',
                channels=self.channel
            )

            # 特徴語ランキング
            self.slack.chat.post_message(
                channel=self.channel,
                text=common_text,
                attachments=message.feature_words_attachments,
                username=self.BOT_NAME,
                icon_emoji=self.ICON_EMOJI
            )

            # Word Cloud
            self.slack.files.upload(
                message.word_cloud_path,
                title='Word Cloud',
                channels=self.channel
            )

            # Webサイトへのリンク
            self.slack.chat.post_message(
                channel=self.channel,
                text=message.more_info,
                username=self.BOT_NAME,
                icon_emoji=self.ICON_EMOJI
            )

            # たまにファイルアップロードがうまくいかないことがあったので、念のため別スレッドで少し待つ
            await asyncio.sleep(5)


def run() -> None:
    # noinspection PyBroadException
    try:
        yesterday = datetime.now() - timedelta(days=1)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(SlackBot().notify(yesterday))
        loop.close()
    except:
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run()
