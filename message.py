import json
import os
from contextlib import contextmanager
from datetime import datetime
from glob import glob
from typing import Dict, List

import matplotlib.pyplot as plt
from pandas import DataFrame


# !/usr/bin/env python
# -*- coding: utf-8 -*-


class MessageBuilder(object):
    """
    Slackに通知する情報（メッセージ、グラフ）を生成するクラス
    """
    LF = '\n'
    FW_URL = 'https://t-analyzers.github.io/featurewords'
    IL_URL = 'https://t-analyzers.github.io/imagelist'

    def __init__(self, data_dir: str):
        self._data_dir = data_dir
        self._tc_message = ''
        self._fw_message = ''
        self._chart_path = ''
        self._word_cloud_path = ''

    @contextmanager
    def build(self, dt: datetime) -> None:
        """
        通知するメッセージとグラフを生成する。
        各プロパティにアクセスする前にこの関数を呼び出す必要がある。
        :param dt: 解析結果の日付
        """
        try:
            date_str = dt.strftime('%Y%m%d')
            # 解析結果ファイルの検索
            # 1ファイルしかマッチしない想定
            json_files = glob('{0}feature_words_*{1}.json'.format(self._data_dir, date_str))
            if len(json_files) == 0:
                raise FileNotFoundError('{0}の解析結果は見つかりませんでした。'.format(date_str))

            with open(json_files[0]) as file:
                data_list = json.load(file)
                self._tc_message = self._build_tweet_count_message(data_list=data_list)
                self._fw_message = self._build_feature_words_message(data_list=data_list)
                self._chart_path = self._create_chart_img(data_list=data_list)

            self._word_cloud_path = glob('{0}wordcloud_{1}.png'.format(self._data_dir, date_str))[0]
            yield

        finally:
            if os.path.exists(self._chart_path):
                os.remove(self._chart_path)

    def _build_tweet_count_message(self, data_list: List[Dict]) -> str:
        """
        つぶやき数をサマライズしたメッセージを生成する
        """
        def build_difference(before: int, after: int):
            difference = after - before
            triangle = '△' if difference >= 0 else '▼'
            return '（前日{0}{1}）'.format(triangle, str(abs(difference)))

        # 対象日のつぶやき数
        latest_data = data_list[0]
        total = latest_data['tweets_count']
        rt_count = latest_data['retweets_count']
        t_count = total - rt_count

        # 前日のつぶやき数
        before_data = data_list[1]
        before_total = before_data['tweets_count']
        before_rt_count = before_data['retweets_count']
        before_t_count = before_total - before_rt_count

        return self.LF.join([
            '合計：  {0}{1}'.format(str(total), build_difference(before_total, total)),
            'リツィート除く：  {0}{1}'.format(str(t_count), build_difference(before_t_count, t_count)),
            'リツィート：  {0}{1}'.format(str(rt_count), build_difference(before_rt_count, rt_count))
        ])

    @classmethod
    def _build_feature_words_message(cls, data_list: List[Dict]) -> str:
        """
        特徴語ランキングのメッセージを生成する
        """
        latest_data = data_list[0]
        return cls.LF.join(['{0}位  {1}'.format(str(i + 1), v) for i, v in enumerate(latest_data['feature_words'])])

    @classmethod
    def _create_chart_img(cls, data_list: List[Dict]) -> str:
        """
        つぶやき数の推移グラフを生成する
        """
        # noinspection PyUnresolvedReferences
        import seaborn as sns
        df = DataFrame(
            index=[data['date'] for data in data_list],
            data={
                '#ALL': [data['tweets_count'] for data in data_list],
                '#NotRT': [data['tweets_count'] - data['retweets_count'] for data in data_list],
                '#RT': [data['retweets_count'] for data in data_list]
            }
        )

        df = df.reindex(index=df.index[::-1])
        df.plot(y=['#ALL', '#NotRT', '#RT'], linestyle='dashed', marker='o')
        plt.title('Weekly')
        plt.xlabel('date')
        plt.ylabel('tweet count')
        temp_img_path = os.path.join(os.path.dirname(__file__), 'temp/graph.png')
        plt.savefig(temp_img_path)
        return temp_img_path

    @classmethod
    def _build_attachments(cls, title: str, text: str) -> List[Dict]:
        """
        Attachmentsを生成する
        https://api.slack.com/docs/message-attachments
        """
        return [{
            'fallback': 'MCOPY Tweets Analysis Result - {0}'.format(cls.FW_URL),
            'title': title,
            'text': text,
            'color': '#764FA5'
        }]

    @property
    def word_cloud_path(self) -> str:
        return self._word_cloud_path

    @property
    def chart_path(self) -> str:
        return self._chart_path

    @property
    def tweet_count_attachments(self) -> List[Dict]:
        return self._build_attachments('つぶやき数', self._tc_message)

    @property
    def feature_words_attachments(self) -> List[Dict]:
        return self._build_attachments('特徴語ランキング', self._fw_message)

    @property
    def more_info(self) -> str:
        return self.LF.join(['more info...', self.FW_URL, self.IL_URL])
