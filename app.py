from jinja2 import Environment
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from flask import Flask, request, render_template
import csv
import os

app = Flask(__name__, static_url_path='/static')

# Import the zip filter
env = Environment()
env.filters['zip'] = zip
def jinja2_enumerate(iterable):
    return enumerate(iterable)

def stemmer(documents):
    punc = ['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', "%", "'", "``"]
    stpwrd = nltk.corpus.stopwords.words('english')
    stpwrd.extend(punc)
    porter = PorterStemmer()
    filtered_docs = []
    for doc in documents:
        tokens = word_tokenize(doc)
        tmp = ""
        for word in tokens:
            if word.lower() not in stpwrd:
                tmp += porter.stem(word.lower()) + " "
        filtered_docs.append(tmp)

    return (filtered_docs)


def stemmer_query(query):
    punc = ['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', "%", "'", "``"]
    stpwrd = nltk.corpus.stopwords.words('english')
    stpwrd.extend(punc)
    stemmer = PorterStemmer()
    title_tokens = [stemmer.stem(token) for token in query.split() if token.lower() not in stpwrd]
    return(title_tokens)


def build_inverted_index(documents):
    inverted_index = {}
    filtered_docs = stemmer(documents)
    # Tokenize each document and count the term frequency
    for idx, doc in enumerate(filtered_docs):
        tokens = doc.split()
        term_freq = {}
        for token in tokens:
            if token in term_freq:
                term_freq[token] += 1
            else:
                term_freq[token] = 1
        for token, tf in term_freq.items():
            if token in inverted_index:
                inverted_index[token][idx] = tf
            else:
                inverted_index[token] = {idx: tf}
    return (inverted_index)


def process_query(query, inverted_index):
    qdocs = set()
    filtered_query = stemmer_query(query)
    df = {}
    tf_idf = {}
    for j in range(len(filtered_query)):
        if filtered_query[j] in inverted_index:
            qdocs = qdocs.union(inverted_index[filtered_query[j]].keys())
            print(qdocs)
            df[filtered_query[j]] = len(inverted_index[filtered_query[j]])
            N = len(qdocs)
            for i, tf in inverted_index[filtered_query[j]].items():
                if i in tf_idf:
                    tf_idf[i] += tf * (N / df[filtered_query[j]])
                else:
                    tf_idf[i] = tf * (N / df[filtered_query[j]])
    sorted_tf_idf = sorted(tf_idf, key=lambda k: tf_idf[k] * -1)
    return (sorted_tf_idf)


filename = "result_papers.csv"
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, filename)



with open(csv_path, mode="r") as csvfile:
    papers = []
    reader = csv.DictReader(csvfile)
    for row in reader:
        papers.append(row)

corpus = []
for paper in papers:
    f = ""
    f = paper['title'] + " " + paper['cov_authors'] +  " " + paper['non_cov_authors'] +  " " + paper['abstract'] + \
        paper['date']
    f = ((f.replace('[','')).replace(']','')).replace("'",'')
    corpus.append(f)

inverted_index = build_inverted_index(corpus)

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/search", methods=['GET', 'POST'])

def search():
    # Get the query
    query = request.form.get("query")
    sorted_tf_idf = process_query(query, inverted_index)
    print(sorted_tf_idf)
    results = []
    for i in sorted_tf_idf:
        paper = {}
        paper = papers[i]
        results.append({
            "title": paper["title"],
            "title_link": paper["title_link"],
            "date": paper["date"],
            "authors_cov": paper["cov_authors"].replace('[','').replace(']','').split("'"),
            "author_links": paper["author_links"].replace('[','').replace(']','').split("'"),
            "authors_noncov": paper["non_cov_authors"].replace('[','').replace(']','').split("'"),
            "abstract": paper["abstract"]
        })

    return render_template("search.html", query=query, papers=results, zip = zip, enumerate = enumerate)



if __name__ == "__main__":
    app.run(debug=True)


