import requests
import pandas as pd
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit as st

class crawlingArticle:
    def __init__(self):
        self.article_file = "data/article_data.json"
        self.article_df = self.collect_article()

    def collect_article(self):
        # 네이버 경제 뉴스 웹 페이지 파싱
        url = "https://news.naver.com/section/101"
        html = requests.get(url, headers={'User-agent':'Mozilla/5.0'})
        soup = BeautifulSoup(html.text, "lxml")
        a_tag = soup.find_all("a")

        # 네이버 경제 뉴스 기사 중 메인 페이지에 뜨는 기사 링크 수집
        url_set = set()
        for a in a_tag:
            # 경제 뉴스 기사 링크만 가져오기
            if a["href"].startswith("https://n.news.naver.com/mnews/article/") and "comment" not in a["href"]:
                url_set.add(a["href"])

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

            art_lst.append(art_dic)

        article_df = pd.DataFrame(art_lst)
        return article_df

    def visualize_wordcloud(self):
        font_path = '/usr/share/fonts/truetype/nanumfont/NanumGothic.ttf'

        text = " ".join(self.article_df["title"]) + " ".join(self.article_df["main"])
        wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path).generate(text)

        fig = plt.figure()
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        st.pyplot(fig)

    def get_article(self):
        return self.article_df

    def save_article(self):
        self.article_df.to_json(self.article_file, orient="records", force_ascii=False, indent=4)