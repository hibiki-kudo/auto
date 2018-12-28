import copy

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from wordcloud import WordCloud

from morphological_analysis import *
from search import TwitterSearch


def tweet_collect(twitter):
    csv_info = []

    while True:
        try:
            for tweet in twitter.tweets:
                csv_info.append(copy.deepcopy(tweet.text))

            twitter.scroll()

            if len(csv_info) >= 1000:
                break

        except:
            print("収集終了")
            break

    return csv_info


def create_wordcloud(text, file_name):
    fpath = "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc"
    mask = np.array(Image.open("./シルエット画像/クローバー.jpg"))

    # ストップワードの設定
    stop_words = ["https", "twitter", "status", "pic", "com", "www", "ーーーー", " "]

    word_cloud = WordCloud(background_color="white", mask=mask, font_path=fpath, width=900, height=900,
                           stopwords=set(stop_words), max_font_size=100).generate(text)

    plt.figure(figsize=(15, 12))
    plt.imshow(word_cloud)
    plt.axis("off")
    plt.savefig("./ワードクラウド結果画像/" + file_name)


def main():
    user_name = ""
    q = f"from:{user_name} exclude:replies since:2018-1-1"

    twitter = TwitterSearch()
    twitter.search(q)

    csv_info = tweet_collect(twitter)
    words = mecab_list(" ".join(csv_info))
    csv_info = ranking(words)
    df = pd.DataFrame(csv_info, columns=["単語", "回数", "確率"])
    df.to_csv(f"./csvファイル/{user_name}_word_cloud.csv")
    create_wordcloud(",".join([a[0] for a in words]), f"{user_name}_word_cloud.png")


if __name__ == "__main__":
    main()
