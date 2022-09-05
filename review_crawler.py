# google
# google_play_scraper 버전으로 작성
# https://github.com/JoMingyu/google-play-scraper
# pip install google_play_scraper를 진행해야함

# IOS
# 1. RSS 방식으로 이용
# https://itunes.apple.com/국가명/rss/customerreviews/page=1/id=아이디명/sortBy=mostRecent/xml
# 2. app_store_scraper 이용
# pip install app_store_scraper
import google_play_scraper
# -*- coding: utf-8 -*-
from google_play_scraper import Sort, reviews_all
from app_store_scraper import AppStore
import pandas as pd
import xmltodict
import requests

''''###
설명 
reviewId : ID (ios, google 공통 존재)
userName : 작성자
at : 작성날짜
score : 별점(5점만점)
title : 제목(ios만 해당)
content : 리뷰내용
reviewCreatedVersion : 리뷰 작성 당시 App 버전 (없는 경우 , 설치 안하고 작성한걸로 추정) (단, 답변달린 ios는 버전 확인 불가)
os : OS
userImage : 작성자 이미지(google만 해당)
thumbsUpCount : 좋아요 수(google만 해당)
replyContent : 리뷰 답변(google만 해당)
repliedAt : 리뷰 답변 작성날짜(google만 해당)
###'''


def get_google_reviews_all(app_name, lang, country):
    result = reviews_all(
        app_name,
        sleep_milliseconds=0,  # defaults to 0
        lang=lang,  # defaults to 'en'
        country=country,  # defaults to 'us'
        sort=Sort.MOST_RELEVANT,  # defaults to Sort.MOST_RELEVANT
        filter_score_with=None  # defaults to None(means all score)
    )

    return pd.DataFrame(result)


def get_last_page_num(url):
    response = requests.get(url).content.decode('utf8')
    xml = xmltodict.parse(response)
    last_url = [l['@href'] for l in xml['feed']['link'] if (l['@rel'] == 'last')][0]
    last_index = [int(s.replace('page=', '')) for s in last_url.split('/') if ('page=' in s)][0]
    return last_index


def extract_reply_content(df_cloumn):
    if str(df_cloumn) != 'nan':
        res = df_cloumn['body']
    else:
        res = None
    return res


def extract_reply_at(df_cloumn):
    if str(df_cloumn) != 'nan':
        res = df_cloumn['modified']
    else:
        res = None
    return res


# 리뷰 답변 버전 사용 가능, 단 해당 버전은 사용시 설치시 버전을 확인 불가
def get_ios_reviews_all_add_responce(id):
    my_app = AppStore(country='kr', app_name='gccare', app_id=id)
    my_app.review()
    fetched_reviews = my_app.reviews
    ios_review_df = pd.DataFrame(fetched_reviews)
    ios_review_df['reviewId'] = 'ios_' + ios_review_df.reset_index()['index'].astype('str')
    ios_review_df.rename(columns={'date': 'at', 'rating': 'score', 'review': 'content'}, inplace=True)

    ios_review_df['replyContent'] = ios_review_df['developerResponse'].apply(extract_reply_content)
    ios_review_df['repliedAt'] = ios_review_df['developerResponse'].apply(extract_reply_at)
    ios_review_df = ios_review_df.drop(['isEdited', 'developerResponse'], axis=1)

    return ios_review_df


def get_ios_reviews_all(id, country):
    # rss link 양식
    # https://itunes.apple.com/국가명/rss/customerreviews/page=1/id=아이디명/sortBy=mostRecent/xml
    url = 'https://itunes.apple.com/' + country + '/rss/customerreviews/page=1/id=' + id + '/sortBy=mostRecent/xml'

    try:
        last_index = get_last_page_num(url)
    except Exception as e:
        # print(url)
        print('No Reviews: appid %i' % id)
        print('Exception:', e)
        return

    result = []
    # 각 review page별로 추가
    for idx in range(1, last_index + 1):
        url = 'https://itunes.apple.com/' + country + '/rss/customerreviews/page=' + str(
            idx) + '/id=' + id + '/sortBy=mostRecent/xml'
        response = requests.get(url).content.decode('utf8')
        xml = xmltodict.parse(response)

        try:
            review_content = xml['feed']['entry']
        except KeyError as e:
            print("Empty Review", e)
            continue

        # 단일 리뷰인 경우 xml 구조가 달라짐
        try:
            print(review_content[0]['author']['name'])
            single_review = False
        except:
            single_review = True
            pass

        if single_review:
            result.append({
                'reviewId': review_content['id'],
                'userName': review_content['author']['name'],
                'at': review_content['updated'],
                'score': int(review_content['im:rating']),
                'title': review_content['title'],
                'content': review_content['content'][0]['#text'],
                'reviewCreatedVersion': review_content['im:version'],
            })
        else:
            for i in range(len(review_content)):
                result.append({
                    'reviewId': review_content[i]['id'],
                    'userName': review_content[i]['author']['name'],
                    'at': review_content[i]['updated'],
                    'score': int(review_content[i]['im:rating']),
                    'title': review_content[i]['title'],
                    'content': review_content[i]['content'][0]['#text'],
                    'reviewCreatedVersion': review_content[i]['im:version'],
                })
    res_df = pd.DataFrame(result)
    res_df['at'] = pd.to_datetime(res_df['at'], format="%Y-%m-%dT%H:%M:%S-07:00")

    return res_df


def get_ios_reviews(ios_app_id, country):
    fir_df = get_ios_reviews_all(ios_app_id, country)
    sec_df = get_ios_reviews_all_add_responce(ios_app_id)

    merge_df = pd.merge(left=fir_df, right=sec_df, how="left", on="userName")
    merge_df = merge_df.drop(['score_y', 'at_y', 'title_y', 'content_y', 'reviewId_y'], axis=1)
    merge_df.rename(columns={'score_x': 'score', 'at_x': 'at', 'title_x': 'title', 'content_x': 'content',
                             'reviewId_x': 'reviewId'}, inplace=True)
    merge_df['repliedAt'] = pd.to_datetime(merge_df['repliedAt'], format="%Y-%m-%dT%H:%M:%SZ")

    return merge_df


if __name__ == "__main__":
    country = 'kr'
    lan = 'ko'
    google_app_name = 'com.gchc.combination'
    ios_app_id = '1568995483'

    # 어떠케어 IOS ID : 1568995483
    # ios 리뷰 df 추출
    ios_review_df = get_ios_reviews(ios_app_id, country)
    ios_review_df['os'] = 'ios'
    # ios_review_df.to_csv("gccare_ios_review_0705.csv", encoding='utf-8-sig', index=False)

    # 어떠케어 구글 App 이름 : 'com.gchc.combination'
    # 구글 리뷰 df 추출
    google_review_df = get_google_reviews_all(google_app_name, lan, country)
    google_review_df['os'] = 'google'
    # google_review_df.to_csv("gccare_google_review_0705.csv", encoding='utf-8-sig', index=False)

    # ios google 통합
    all_review_df = pd.concat([ios_review_df, google_review_df])
    all_review_df.to_csv("gccare_all_review_0905.csv", encoding='utf-8-sig', index=False)
