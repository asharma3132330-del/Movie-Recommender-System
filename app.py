import os
import streamlit as st
import pickle
import pandas as pd
import requests
import time
import gzip


# ====== Load Similarity Matrix from compressed file ======
@st.cache_data(show_spinner=True)
def load_similarity():
    with gzip.open("similarity.pkl.gz", "rb") as f:
        return pickle.load(f)

similarity = load_similarity()


# ====== Load Movie Data ======
movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)


# ====== TMDB Poster Fetch ======
def fetch_poster(movie_id, retries=3):
    api_key = os.getenv("TMDB_API_KEY")
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            poster_path = data.get("poster_path")
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path

        except requests.exceptions.RequestException:
            time.sleep(0.5)

    return "https://via.placeholder.com/300x450?text=No+Image"


# ====== Recommendation Function ======
def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        movie_idx = i[0]

        title = movies.iloc[movie_idx].title
        movie_id = movies.iloc[movie_idx].movie_id

        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(movie_id))

        time.sleep(0.2)

    return recommended_movies, recommended_posters


# ====== Streamlit UI ======
st.set_page_config(layout="wide")

left, center, right = st.columns([1, 2, 1])
with center:
    st.title("🎬 Movie Recommender System")
    st.write("Select a movie and get similar recommendations.")

    selected_movie = st.selectbox(
        "Choose a movie",
        movies["title"].values
    )

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        recommend_btn = st.button("Recommend")


# ====== Show Recommendations ======
if recommend_btn:
    recommended_movies, recommended_posters = recommend(selected_movie)

    st.markdown(
        "<h2 style='text-align:center;'>Recommended Movies</h2>",
        unsafe_allow_html=True
    )

    cols = st.columns(5, gap="large")

    for i, col in enumerate(cols):
        with col:
            st.image(recommended_posters[i])
            st.caption(recommended_movies[i])


st.markdown("---")
st.caption("AI Movie Recommendation Project")
