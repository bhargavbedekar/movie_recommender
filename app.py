import streamlit as st
import pickle
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

# Add custom CSS for better styling
st.markdown("""
<style>
    /* Global styles */
    body {
        font-family: 'Inter', sans-serif;
        background-color: #1a1a1a;
        color: #e0e0e0;
    }

    /* Container styles */
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }

    /* Header styles */
    h1, h2, h3 {
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    /* Selectbox styles */
    .stSelectbox > div > div {
        background-color: #2c2c2c;
        border-radius: 8px;
        border: 1px solid #444444;
        color: white;
    }
    .stSelectbox > div > div:hover {
        border-color: #646cff;
    }

    /* Button styles */
    .stButton > button {
        width: 100%;
        border-radius: 25px;
        font-weight: 600;
        background-color: #646cff;
        color: white;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #767dff;
        box-shadow: 0 4px 12px rgba(100, 108, 255, 0.4);
    }

    /* Movie item styles */
    .movie-item {
        background-color: #2c2c2c;
        border-radius: 12px;
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .movie-item:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }

    /* Movie poster styles */
    .movie-item img {
        width: 100%;
        height: auto;
        display: block;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
        transition: transform 0.3s ease;
    }
    .movie-item:hover img {
        transform: scale(1.05);
    }

    /* Movie title styles */
    .movie-title {
        font-weight: 600;
        font-size: 0.9rem;
        color: #ffffff;
        text-align: center;
        padding: 0.75rem;
        background-color: rgba(0, 0, 0, 0.5);
    }

    /* Adjust column gap */
    .row-widget.stHorizontal {
        gap: 1rem;
    }
</style>
""", unsafe_allow_html=True)


st.title('🎬 Movie Recommender System')

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

selected_movie_name = st.selectbox(
    "Which movie do you like?",
    movies['title'].tolist(),
    index=0,
    help="Select a movie you enjoyed to get recommendations"
)


def fetch_poster(movie_id):
    url = f"https://letterboxd.com/tmdb/{movie_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    script_tag = soup.find('script', type='application/ld+json')

    image_url = None

    if script_tag:
        json_string = script_tag.string.strip()
        start = json_string.find('{')
        end = json_string.rfind('}') + 1
        json_data = json.loads(json_string[start:end])
        image_url = json_data.get('image')

    return str(image_url) if image_url else "https://via.placeholder.com/300x450?text=No+Image+Available"


def recommend_movie(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommend_movie_posters = []
    recommend_movie = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommend_movie_posters.append(fetch_poster(movie_id))
        recommend_movie.append(movies.iloc[i[0]].title)
    return recommend_movie, recommend_movie_posters


# Modified recommendation display
import streamlit as st

# Modified recommendation display
if st.button("Get Recommendations", type="primary"):
    with st.spinner('Finding great movies for you...'):
        names, posters = recommend_movie(selected_movie_name)

    st.subheader(f"Top 5 recommendations based on '{selected_movie_name}'")

    # Create 5 columns for the recommendations
    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            # Wrap the image and title in a div for styling
            st.markdown(f"""
                <div class="movie-item">
                    <img src="{posters[i]}" alt="{names[i]}">
                    <div class="movie-title">{names[i]}</div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("Developed with ❤️ by Bhargav Bedekar")
