# -*- coding: utf-8 -*-
"""RAGS and Retrieval Sys- Final.pynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1hNZbZCG1Rhbv-6ngrgod-Kl-78rRvuZB

**Enhancing Search Engine Relevance for Video Subtitles**
"""

from google.colab import drive
drive.mount('/content/drive')

import sqlite3
import zipfile
import io

# Connect to the subtitles database
db_path = r'/content/drive/MyDrive/Copy of eng_subtitles_database.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fetch a single subtitle record
cursor.execute("SELECT num, name, content FROM zipfiles LIMIT 1")
num, name, content = cursor.fetchone()

# Extract .srt from zipped binary
zip_file = zipfile.ZipFile(io.BytesIO(content))
srt_file = zip_file.namelist()[0]  # Assume 1 file per zip
text = zip_file.read(srt_file).decode('utf-8', errors='ignore')

print(f"Subtitle ID: {num}\nFilename: {name}\nText Preview:\n{text[:1000]}")

"""Data preprocessing"""

import re

def clean_subtitle_text(raw_text):
    text = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', '', raw_text)
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'http\S+|www\S+|osdb\.link\S+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

cleaned_text = clean_subtitle_text(text)
print(cleaned_text[:1000])

def chunk_text(text, chunk_size=50, overlap=10):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if len(chunk.split()) >= 10:
            chunks.append(chunk)
    return chunks

chunks = chunk_text(cleaned_text)
print(f"Chunks: {len(chunks)}\n\nSample:\n{chunks[0]}")

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
chunk_embeddings = model.encode(chunks, show_progress_bar=True)

pip install chromadb

import chromadb

# Use the new default in-memory client (sufficient for local/dev)
client = chromadb.Client()

# Create collection
collection = client.get_or_create_collection("subtitle_chunks")

# Add chunks and embeddings
ids = [f"chunk_{i}" for i in range(len(chunks))]

collection.add(
    documents=chunks,
    ids=ids,
    embeddings=chunk_embeddings
)

print("✅ Chunks added to in-memory ChromaDB")

!pip install whisper
!pip install openai-whisper

import whisper

# Load Whisper model
whisper_model = whisper.load_model("base")

# Transcribe audio file
result = whisper_model.transcribe(r"/content/Rags & Retrieval Systm.mp3")
transcribed_text = result['text']
print("🎧 Transcribed:\n", transcribed_text)

query_cleaned = clean_subtitle_text(transcribed_text)
print("🧹 Cleaned Query:\n", query_cleaned)
query_embedding = model.encode([query_cleaned])[0]

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5  # Top 5 closest chunks
)

# Display results
print("🔍 Top Matching Subtitle Chunks:\n")
for doc, dist in zip(results['documents'][0], results['distances'][0]):
    print(f"[Score: {1 - dist:.4f}] {doc}\n")

! pip install streamlit

# Commented out IPython magic to ensure Python compatibility.
# %%writefile app5.py
# import streamlit as st
# import whisper
# import chromadb
# from sentence_transformers import SentenceTransformer
# 
# # ---- Page Config ----
# st.set_page_config(page_title="EchoScribe 🎙", page_icon="🎧", layout="wide")
# 
# # ---- Custom Title Styling ----
# st.markdown(
#     """
#     <div style="text-align: center;">
#         <h1 style="color: #FF4B4B; font-size: 48px; font-weight: bold; font-style: italic;">
#             EchoScribe 🎙
#         </h1>
#     </div>
#     """,
#     unsafe_allow_html=True
# )
# 
# # ---- Sidebar for Upload ----
# st.sidebar.header("⚙️ Settings")
# uploaded_file = st.sidebar.file_uploader("📂 Upload an Audio File", type=["wav", "mp3", "m4a"])
# 
# # ---- Load Whisper Model ----
# @st.cache_resource
# def load_whisper():
#     return whisper.load_model("base")
# 
# whisper_model = load_whisper()
# 
# # ---- Load Sentence Transformer Model ----
# @st.cache_resource
# def load_embedding_model():
#     return SentenceTransformer("all-MiniLM-L6-v2")
# 
# embedding_model = load_embedding_model()
# 
# # ---- Initialize ChromaDB ----
# chroma_client = chromadb.PersistentClient(path="chroma_db")
# collection = chroma_client.get_or_create_collection(name="subtitles")
# 
# # ---- Sample Subtitle Data ----
# subtitles = [
#     "The Prophet Muhammad sent letters to rulers inviting them to Islam.",
#     "Heraklius was a Byzantine Emperor who received the Prophet’s letter.",
#     "The letter to Heraklius spoke about the oneness of God and guidance.",
#     "Islamic history contains many diplomatic correspondences.",
#     "Studying old letters helps us understand history better."
# ]
# 
# # Store subtitles in ChromaDB with embeddings (Avoid re-adding)
# if collection.count() == 0:
#     for i, subtitle in enumerate(subtitles):
#         embedding = embedding_model.encode(subtitle).tolist()
#         collection.add(ids=[str(i)], embeddings=[embedding], documents=[subtitle])
# 
# # ---- Process Uploaded File ----
# if uploaded_file:
#     with open("temp_audio.m4a", "wb") as f:
#         f.write(uploaded_file.getbuffer())
# 
#     st.audio(uploaded_file, format='audio/mpeg')
# 
#     with st.spinner("⏳ Transcribing... Please wait!"):
#         result = whisper_model.transcribe("temp_audio.m4a")
#         transcribed_text = result['text']
# 
#     # ---- Display Transcribed Text in an Expander ----
#     with st.expander("🎧 Transcribed Text", expanded=True):
#         st.markdown(f"<p style='background:#f1f3f4; padding:10px; border-radius:10px;'>{transcribed_text}</p>", unsafe_allow_html=True)
# 
#     # ---- Query Matching Subtitles ----
#     query_embedding = embedding_model.encode([transcribed_text])[0].tolist()
#     results = collection.query(query_embeddings=[query_embedding], n_results=5)
# 
#     # ---- Display Matched Subtitles in a Styled Table ----
#     st.markdown("### 🎯 Best Matched Subtitle Segments")
#     if results['documents'][0]:
#         match_data = [{"Score": f"{1 - dist:.4f}", "Subtitle": doc} for doc, dist in zip(results['documents'][0], results['distances'][0])]
#         st.table(match_data)
#     else:
#         st.warning("No matching subtitles found.")
#

!npm install localtunnel
!streamlit run /content/app5.py &>/content/logs.txt &
!npx localtunnel --port 8501 & curl ipv4.icanhazip.com