import json
from nltk.corpus import stopwords
from functools import partial

with open("vocab.json", "r") as file:
    vocab = json.load(file)

LOWERCASE = [chr(x) for x in range(ord("a"), ord("z") + 1)]
UPPERCASE = [chr(x) for x in range(ord("A"), ord("Z") + 1)]
LOWERCASE_OTHERS = [
    "ç",
    "á",
    "â",
]
UPPERCASE_OTHERS = [x.upper() for x in LOWERCASE_OTHERS]
LETTERS = LOWERCASE + UPPERCASE + LOWERCASE_OTHERS + UPPERCASE_OTHERS


def edit1(text):
    words = []

    # Fase 1: as remoçoes.
    for p in range(len(text)):
        new_word = text[:p] + text[p + 1 :]
        if len(new_word) > 0:
            words.append(new_word)

    # Fase 2: as adições.
    for p in range(len(text) + 1):
        for c in LETTERS:
            new_word = text[:p] + c + text[p:]
            words.append(new_word)

    # Fase 3: as substituições.
    for p in range(len(text)):
        orig_c = text[p]
        for c in LETTERS:
            if orig_c != c:
                new_word = text[:p] + c + text[p + 1 :]
                words.append(new_word)

    return set(words)


def edit2(text):
    words1 = edit1(text)
    words2 = set()

    for w in words1:
        candidate_words2 = edit1(w)
        candidate_words2 -= words1
        words2.update(candidate_words2)

    words2 -= set([text])

    return words2


def word_prob(word, vocab):
    try:
        return vocab[word] / sum(vocab.values())

    except KeyError:
        return 0


def gera_candidatos(word, vocab):
    if word in vocab:
        candidatos = [word]

    else:
        candidatos = []

    candidatos += (
        [w for w in edit1(word) if w in vocab]
        + [w for w in edit2(word) if w in vocab]
        + [word]
    )

    return candidatos


def corrige_palavra(word, vocab):
    return max(gera_candidatos(word, vocab), key=partial(word_prob, vocab=vocab))


def corrige_texto(in_text, vocab):
    out_text = ""

    for p in in_text.split(" "):
        if p in stopwords.words("portuguese"):
            out_text += p + " "
        else:
            out_text += corrige_palavra(p, vocab) + " "

    return out_text[:-1]


while True:
    try:
        word = input("Enter string to correct (Ctrl+C to exit): ")
        print(f"Corrected string: {corrige_texto(word, vocab)}\n")

    except KeyboardInterrupt:
        print("\nGoodbye.")
        break