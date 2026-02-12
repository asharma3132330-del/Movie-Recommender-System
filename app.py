import os
import streamlit as st
import pickle
import pandas as pd
import requests
import gzip
import time


# ===== Load Similarity Matrix =====
@st.cache_resource(show_spinner=True)
def load_similarity():
    with gzip.open("similarity.pkl.gz", "rb") as f:
        return pickle.load(f)


# ===== Load Movie Data =====
@st.cache_resource
def load_movies():
    movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
    return pd.DataFrame(movies_dict)


movies = load_movies()


# ===== Poster Fetch =====
def fetch_poster(movie_id):
    api_key = os.getenv("TMDB_API_KEY")

    if not api_key:
        return "https://via.placeholder.com/300x450?text=No+Poster"

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
        data = requests.get(url, timeout=5).json()
        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path

    except:
        pass

    return "https://via.placeholder.com/300x450?text=No+Poster"


# ===== Recommendation =====
def recommend(movie):
    similarity = load_similarity()

    try:
        movie_index = movies[movies["title"] == movie].index[0]
    except:
        st.error("Movie not found.")
        return [], []

    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        idx = i[0]
        recommended_movies.append(movies.iloc[idx].title)
        recommended_posters.append(fetch_poster(movies.iloc[idx].movie_id))

    return recommended_movies, recommended_posters


# ===== UI =====
st.set_page_config(layout="wide")

st.title("🎬 Movie Recommender System")
st.write("Select a movie and get recommendations.")

selected_movie = st.selectbox("Choose a movie", movies["title"].values)

if st.button("Recommend"):
    with st.spinner("Finding recommendations..."):
        names, posters = recommend(selected_movie)

    if names:
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.image(posters[i])
                st.caption(names[i])

st.markdown("---")
st.caption("AI Movie Recommendation Project")
