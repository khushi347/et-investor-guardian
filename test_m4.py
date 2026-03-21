import streamlit as st
from charts_video.chart import plot_stock
from charts_video.voice import generate_voice

st.title("📊 M4 Test")

stock = st.selectbox("Select Stock", ["TCS.NS", "RELIANCE.NS"])
st.plotly_chart(plot_stock(stock))

if st.button("Generate Voice"):
    text = f"Today's market update. {stock.replace('.NS','')} is showing market activity."
    file = generate_voice(text)
    audio = open(file, "rb")
    st.audio(audio.read(), format="audio/mp3")