import pandas as pd
import json
import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account

# Obtencion de datos desde firestore y almacenamiento en Dataframe
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)
db_movies = db.collection('movies')

# Funciones 
@st.cache_data()
def get_all_movies():
  movies_ref = list(db_movies.stream())
  movies_dict = list(map(lambda x: x.to_dict(), movies_ref))
  movies_df = pd.DataFrame(movies_dict)
  return movies_df

def load_by_title(title):
    filtered_title = df[df['name'].str.lower().str.contains(title_search.lower())]
    return filtered_title

def load_by_director(director):
    query = db_movies.where('director', '==', director)
    docs = list(query.stream())
    data = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data)

df = get_all_movies()

# Construccion con streamlit
st.title("Netflix App")
st.text("Done! (using st.cache)")

# Checkbox todas las peliculas
all_movies = st.sidebar.checkbox("Mostrar todos los filmes", value=True)
if all_movies:
    st.header("Todos los filmes")
    st.dataframe(df)

# Búsqueda por título
title_search = st.sidebar.text_input("Título del filme:")
if st.sidebar.button("Buscar filmes"):
    filtered_title = load_by_title(title_search)
    st.subheader(f"Total de filmes mostrados: {len(filtered_title)}")
    st.dataframe(filtered_title)

# Filtro por director
director_list = sorted(df['director'].dropna().unique())
selected_director = st.sidebar.selectbox("Selecciona un director", director_list)
if st.sidebar.button("Filtrar director"):
    filtered_director = load_by_director(selected_director)
    if not filtered_director.empty:
        st.subheader(f"Total de filmes mostrados: {len(filtered_director)}")
        st.dataframe(filtered_director)
    else:
        st.sidebar.warning("No hay películas para ese director.")

# Registrar nueva pelicula
st.sidebar.markdown("---")
st.sidebar.subheader("Nuevo filme")

new_name = st.sidebar.text_input("Name")
new_company = st.sidebar.text_input("Company")
new_director = st.sidebar.text_input("Director")
new_genre = st.sidebar.text_input("Genre")

if st.sidebar.button("Crear nuevo filme"):
    if new_name and new_genre and new_director and new_company:
        doc_ref = db_movies.document()
        doc_ref.set({
            "name": new_name,
            "company": new_company,
            "director": new_director,
            "genre": new_genre
        })
        st.sidebar.success("Película agregada correctamente!")
        get_all_movies.clear()  
    else:
        st.sidebar.error("Todos los campos son obligatorios.")
