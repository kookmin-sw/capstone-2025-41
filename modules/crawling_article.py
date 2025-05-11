import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit as st
from collections import Counter
from modules.DB import SupabaseDB
from urllib.parse import urlparse, parse_qs

class crawlingArticle:
    def __init__(self):
        self.db = SupabaseDB()
        self.article_df = self.collect_article()

    def collect_article(self):
        # 네이버 경제 뉴스 웹 페이지 파싱
        headers = {"User-Agent": "Mozilla/5.0"}
        base_url = 'https://finance.naver.com/news/mainnews.naver?page='

        url_set = set()
        for page in range(1, 10):
            page_url = base_url + str(page)

            response = requests.get(page_url, headers=headers)
            if response.status_code != 200:
                print(f"페이지 로딩 실패: {page_url}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']

                if '/news/news_read.naver' in href:
                    parsed = urlparse(href)
                    params = parse_qs(parsed.query)
                    article_id = params.get('article_id', [None])[0]
                    office_id = params.get('office_id', [None])[0]

                    if article_id and office_id:
                        true_url = f"https://n.news.naver.com/article/{office_id}/{article_id}"
                        url_set.add(true_url)

        # 기사 타이틀, 본문 셀렉터
        title_selector = "#title_area > span"
        main_selector = "#dic_area"

        # url 리스트와 기사 데이터를 수집할 리스트
        url_lst = list(url_set)
        art_lst = []

        # 전체 경제 뉴스 기사 파싱
        for url in url_lst:
            html = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
            })
            soup = BeautifulSoup(html.text, "lxml")
            
            # 뉴스 제목 수집
            title = soup.select(title_selector)
            title_lst = [t.text for t in title]
            title_str = "".join(title_lst)
            
            # 뉴스 본문 수집
            main = soup.select(main_selector)
            main_lst = []
            for m in main:
                m_text = m.text
                m_text = m_text.strip()
                main_lst.append(m_text)
            main_str = "".join(main_lst)

            art_dic = {}
            art_dic["title"] = title_str
            art_dic["main"] = main_str
            art_dic["url"] = url

            art_lst.append(art_dic)

        article_df = pd.DataFrame(art_lst)
        return article_df

    def visualize_wordcloud(self):
        font_path = os.path.join("assets", "NanumGothic-Bold.ttf")
        text = " ".join(self.article_df["title"])
        word_counts = Counter(text.split())
        wordcloud = WordCloud(
            width=800, height=400, background_color='white', font_path=font_path
        ).generate_from_frequencies(word_counts)

        fig = plt.figure()
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        st.pyplot(fig)

    def save_article(self):
        """Supabase에 기사 데이터 저장"""
        article_data = self.article_df.to_dict(orient="records")
        self.db.insert_article_data_json(article_data)
        print("뉴스 기사 데이터가 Supabase에 저장되었습니다.")

    def load_article(self):
        """Supabase에서 기사 데이터 불러오기"""
        data = self.db.get_article_data_today()
        if not data:
            print("Supabase에 저장된 데이터가 없습니다. 새로 수집합니다.")
            return self.collect_article()
        return pd.DataFrame(data)

    def get_article(self):
        return self.article_df