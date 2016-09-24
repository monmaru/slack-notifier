import os
from datetime import datetime, timedelta
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
            self.token = setting['slack']['token'],
            self.channel = setting['slack']['channel']
            self.data_dir = setting['data']['dir']

    def notify(self):
        """
        Slackに解析結果を通知する
        """
        slack = Slacker(self.token)
        yesterday = datetime.now() - timedelta(days=1)
        common_text = '■{0}の解析結果'.format(yesterday.strftime('%Y/%m/%d'))

        message = MessageBuilder(self.data_dir)
        with message.build(yesterday):
            # つぶやき数
            slack.chat.post_message(
                channel=self.channel,
                text=common_text,
                attachments=message.tweet_count_attachments,
                username=self.BOT_NAME,
                icon_emoji=self.ICON_EMOJI
            )

            # つぶやき数のグラフ
            slack.files.upload(
                message.chart_path,
                title='つぶやき数の推移',
                channels=self.channel
            )

            # 特徴語ランキング
            slack.chat.post_message(
                channel=self.channel,
                text=common_text,
                attachments=message.feature_words_attachments,
                username=self.BOT_NAME,
                icon_emoji=self.ICON_EMOJI
            )

            # Word Cloud
            slack.files.upload(
                message.word_cloud_path,
                title='Word Cloud',
                channels=self.channel
            )

            # Webサイトへのリンク
            slack.chat.post_message(
                channel=self.channel,
                text=message.more_info,
                username=self.BOT_NAME,
                icon_emoji=self.ICON_EMOJI
            )


def run():
    # noinspection PyBroadException
    try:
        SlackBot().notify()
    except:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run()
