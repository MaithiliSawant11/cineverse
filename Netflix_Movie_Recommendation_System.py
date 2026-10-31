"""Netflix Movie Recommendation System - reconstructed from supplied PDF."""
# Install dependencies separately: pip install pandas numpy scikit-learn nltk seaborn


# Install/import dependencies
!pip -q install nltk scikit-learn pandas numpy

import re
import ast
import pickle
import warnings
import numpy as np
import pandas as pd
import seaborn as sns
import nltk

from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings("ignore")


# Merge the dataframes using the movie title (as in the original project)
movies = movies.merge(credits, on="title")
print("Merged shape:", movies.shape)
display(movies.head(2))


df = movies[["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]].copy()
print("Selected dataframe shape:", df.shape)
display(df.head())


# Convert JSON-like strings into Python lists
def fetch_names(text):
    """Extract each item's 'name' field from a JSON-like string."""
    if pd.isna(text):
        return []
    try:
        return [item["name"] for item in ast.literal_eval(text) if isinstance(item, dict) and "name" in item]
    except (ValueError, SyntaxError, TypeError):
        return []

def fetch_genres(text):
    return fetch_names(text)

def fetch_keywords(text):
    return fetch_names(text)

df["genres"] = df["genres"].apply(fetch_genres)
df["keywords"] = df["keywords"].apply(fetch_keywords)

display(df[["title", "genres", "keywords"]].head(3))


# Extract the first three cast members
def fetch_cast(text):
    if pd.isna(text):
        return []
    try:
        cast_list = ast.literal_eval(text)
        return [person["name"] for person in cast_list[:3] if isinstance(person, dict) and "name" in person]
    except (ValueError, SyntaxError, TypeError):
        return []

df["cast"] = df["cast"].apply(fetch_cast)
display(df[["title", "cast"]].head(3))


# Extract director name(s) from crew
def fetch_director(text):
    if pd.isna(text):
        return []
    try:
        crew_list = ast.literal_eval(text)
        return [
            person["name"]
            for person in crew_list
            if isinstance(person, dict) and person.get("job") == "Director" and "name" in person
        ]
    except (ValueError, SyntaxError, TypeError):
        return []

df["crew"] = df["crew"].apply(fetch_director)
display(df[["title", "crew"]].head(3))


# Remove rows with missing values (the original notebook dropped null rows)
print("Missing values before cleaning:")
display(df.isnull().sum())

df.dropna(subset=["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"], inplace=True)
df.reset_index(drop=True, inplace=True)

print("Missing values after cleaning:")
display(df.isnull().sum())


# Convert overview text into a list of words
df["overview"] = df["overview"].apply(lambda text: text.split() if isinstance(text, str) else [])

# Combine overview, genres, keywords, cast and director into one tags column
df["tags"] = (
    df["overview"]
    + df["genres"]
    + df["keywords"]
    + df["cast"]
    + df["crew"]
)

data = df[["movie_id", "title", "tags"]].copy()
display(data.head())
print("Number of movies:", len(data))


# Remove spaces inside individual tag phrases, matching the PDF's preprocessing step
data["tags"] = data["tags"].apply(
    lambda tag_list: [str(word).replace(" ", "") for word in tag_list]
)

# Convert the list of tags into one text string
data["tags"] = data["tags"].apply(lambda tag_list: " ".join(tag_list))

display(data.head())
print(data.loc[0, "tags"])


ps = PorterStemmer()

def text_preprocessing(text):
    new_text = []
    for word in str(text).split():
        lower_word = word.lower()
        new_text.append(ps.stem(lower_word))
    return " ".join(new_text)

data["tags"] = data["tags"].apply(text_preprocessing)

display(data.head())
print(data.loc[0, "tags"])


cv = CountVectorizer(max_features=5000, stop_words="english")
vectors = cv.fit_transform(data["tags"]).toarray()

print("Vector matrix shape:", vectors.shape)
print("Vocabulary size:", len(cv.get_feature_names_out()))


# Cosine similarity between every pair of movies
similarity = cosine_similarity(vectors)

print("Similarity matrix shape:", similarity.shape)


def recommend(movie):
    matches = data.index[data["title"].str.casefold() == str(movie).casefold()].tolist()

    if not matches:
        print(f"Movie '{movie}' was not found. Check the spelling or choose a title from data['title'].")
        return []

    movie_index = matches[0]
    distance = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distance)),
        reverse=True,
        key=lambda item: item[1]
    )[1:6]

    recommendations = []
    for index, score in movie_list:
        title = data.iloc[index].title
        recommendations.append(title)
        print(f"{title}  (similarity: {score:.4f})")

    return recommendations


# Sample recommendations shown/tested in the PDF
recommend("Avatar")


recommend("Iron Man")


recommend("Batman")


recommend("Superman")


recommend("X-Men")


recommend("Spider-Man")


with open("movie_list.pkl", "wb") as file:
    pickle.dump(data, file)

with open("similarity.pkl", "wb") as file:
    pickle.dump(similarity, file)

with open("count_vectorizer.pkl", "wb") as file:
    pickle.dump(cv, file)

print("Saved: movie_list.pkl, similarity.pkl, count_vectorizer.pkl")


# Dataset inspection commands shown in the source notebook
display(movies.head(3))
display(credits.head())
print('Movies shape:', movies.shape)
print('Credits shape:', credits.shape)
print('Columns:', movies.columns, credits.columns)
display(movies.head(2))
display(df.head(3))


# Inspect parsed feature columns and individual examples
display(df['genres'].head())
display(df['keywords'].head())
display(df['cast'].head())
display(df['crew'].head())
print('Overview example:', df['overview'].iloc[0])
print('Tags example:', data['tags'].iloc[0])


# Small string/list demonstrations shown in the PDF
print(' '.join(['i', 'am', 'a', 'boy']))
print('I AM a Boy'.lower())
print('i am a boy'.replace(' ', ''))
print([5] + [5])
print('love / lover / lovers / lovable / lovely / loving:')
for word in ['love', 'lover', 'lovers', 'lovable', 'lovely', 'loving']:
    print(ps.stem(word))


# Vectorizer and similarity inspection commands shown in the PDF
print('Vector shape:', vectors.shape)
print('First vocabulary terms:', cv.get_feature_names_out()[:50])
print('Number of vectors:', len(vectors))
print('Similarity matrix size:', len(similarity))
print('First movie similarity row (first 20 values):', similarity[0][:20])
print('Top five similar movie indices/scores for the first movie:')
print(sorted(list(enumerate(similarity[0])), reverse=True, key=lambda item: item[1])[1:6])
