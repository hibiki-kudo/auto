import MeCab
import pandas as pd


def mecab_list(copas):
    m = MeCab.Tagger("-Ochasen")
    m.parse("")
    disas = m.parseToNode(copas)
    outputList = []

    while disas:
        word = disas.surface
        part = disas.feature.split(',')
        if part[0] != u'BOS/EOS':
            if (len(word) > 1 or part[6] != "*") and word != "nan" and part[0] == "名詞" and (
                    part[1] == "一般" or part[0] == "固有名詞" or part[0] == "サ変接続"):
                outputList.append([word, part[0], part[6]])

        disas = disas.next
    return outputList


def ranking(words):
    words_ranking = {}
    population = 0
    for word in words:
        if word[1] != "名詞":
            continue

        elif words_ranking.get(word[0]) == None:
            words_ranking[word[0]] = 1

        else:
            words_ranking[word[0]] += 1

        population += 1

    words_ranking = [list(a) for a in sorted(words_ranking.items(), key=lambda x: x[1], reverse=True)]

    counter = 0
    for word_ranking in words_ranking:
        words_ranking[counter].append(str(round(word_ranking[1] / population, 7) * 100) + "%")
        counter += 1

    return words_ranking


def analysis(file_name=""):
    profile_text = " ".join([str(a) for a in pd.read_csv(file_name)["profile_message"]])
    words = mecab_list(profile_text)
    words_rank = ranking(words)

    df = pd.DataFrame(words_rank[:500:], columns=["単語", "回数", "割合"])
    df.to_csv(f"{file_name[:-19]}_analysis.csv")


if __name__ == "__main__":
    file_name = ""

    profile_text = " ".join([str(a) for a in pd.read_csv(file_name)["profile_message"]])
    words = mecab_list(profile_text)
    words_rank = ranking(words)

    df = pd.DataFrame(words_rank[:500:], columns=["単語", "回数", "割合"])
    df.to_csv(f"{file_name[:-19]}_analysis.csv")
