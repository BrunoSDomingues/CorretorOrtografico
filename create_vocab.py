import json
import re
import nltk
from collections import Counter

with open("dump_small.jsonln", "r") as file:
    data = [json.loads(line) for line in file]


def limpa_aspas(texto):
    pattern = r"""(['"]+)(.*?)\1"""
    repl = r"\2"
    matcher = re.compile(pattern, re.VERBOSE)
    return matcher.sub(repl, texto)


def limpa_ref(texto):
    pattern = r"""<ref>.*?</ref>"""
    repl = r""
    matcher = re.compile(pattern, re.VERBOSE)
    return matcher.sub(repl, texto)


def limpa_url(texto):
    # Regex obtida de https://www.geeksforgeeks.org/python-check-url-string/
    pattern = r"""
        (?i)  # Ignore case.
        \b  # Inicio de palavra.
        (?:
            https?://
        |
            www
            \d{0,3}
            [.]
        |
            [a-z0-9.\-]+
            [.]
            [a-z]{2,4}
            /
        )
        (?:
            [^\s()<>]+
        |
            \(
            (?:
                [^\s()<>]+
            |
                \(
                [^\s()<>]+
                \)
            )*
            \)
        )+
        (?:
            \(
            (?:
                [^\s()<>]+
            |
                \(
                [^\s()<>]+
                \)
            )*
            \)
        |
            [^\s`!()\[\]{};:'\".,<>?«»“”‘’]
        )
    """
    repl = ""
    matcher = re.compile(pattern, re.VERBOSE)
    return matcher.sub(repl, texto)


def limpa_templates(texto):
    conta = 0
    spans_proibidos = []

    for item in re.finditer(r"{{|}}", texto):
        if item[0] == "{{":
            if conta == 0:
                inicio = item.span()[0]
            conta += 1

        else:
            conta -= 1
            if conta == 0:
                fim = item.span()[1]
                spans_proibidos.append((inicio, fim))

    texto_limpo = ""
    inicio = 0

    for span in spans_proibidos:
        fim, novo_inicio = span
        texto_limpo += texto[inicio:fim]
        inicio = novo_inicio

    texto_limpo += texto[inicio:]

    return texto_limpo


def limpa_wikilinks(texto):
    pattern = r"""
        \[\[
        (?:
            [^|]*?\|
        )*?
        (
            [^|]*?
        )
        \]\]
    """
    repl = r"\1"
    matcher = re.compile(pattern, re.VERBOSE)
    return matcher.sub(repl, texto)


def limpa_cat(texto):
    pattern = r"\[\[Categoria:.*?\]\]"
    repl = r""
    matcher = re.compile(pattern)
    return matcher.sub(repl, texto)


def pega_palavras(tokens):
    matcher = re.compile(r"[a-záéíóúçâêôãõà]+(?:-[a-záéíóúçâêôãõà]+)*")
    return [token for token in tokens if matcher.fullmatch(token)]


def minusculas(tokens):
    return [token.lower() for token in tokens]


def remove_digitos(tokens):
    matcher = re.compile(r"[^\d]*")
    return [token for token in tokens if matcher.fullmatch(token)]


def limpa_stopwords(tokens):
    stopwords = nltk.corpus.stopwords.words("portuguese")
    return [token for token in tokens if token not in stopwords]


def limpa_texto(texto):
    texto = limpa_aspas(texto)
    texto = limpa_ref(texto)
    texto = limpa_url(texto)
    texto = limpa_templates(texto)
    texto = limpa_wikilinks(texto)
    return texto


def limpa_tokens(tokens):
    tokens = minusculas(tokens)
    tokens = remove_digitos(tokens)
    tokens = pega_palavras(tokens)
    return tokens


all_words = []

for item in data:
    texto = item["body"]
    texto = limpa_texto(texto)
    tokens = nltk.word_tokenize(texto)
    tokens = limpa_tokens(tokens)
    tokens = limpa_stopwords(tokens)
    all_words += tokens

all_words_clean = limpa_tokens(all_words)

word_counts = Counter(all_words_clean)
word_counts_list = list(word_counts.items())
word_counts_list_sorted = sorted(word_counts_list, key=lambda x: (-x[1], x[0]))

wcls = dict(word_counts_list_sorted[:3000])

with open("vocab2.json", "w+") as vocab:
    vocab.write("{\n")
    for word in wcls:
        if word == list(wcls.keys())[-1]:
            end = "\n"
        else:
            end = ",\n"
        vocab.write(f'    "{word}": {wcls[word]}{end}')
    vocab.write("}")