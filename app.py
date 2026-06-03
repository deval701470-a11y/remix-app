import streamlit as st
import os
from pydub import AudioSegment
import tempfile

st.set_page_config(
    page_title="🎵 Auto Remix Maker",
    page_icon="🎵",
    layout="centered"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0e0e0e;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 20px;
        padding: 15px 40px;
        font-size: 18px;
        width: 100%;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("# 🎵 Auto Remix Maker")
st.markdown("#### Song upload karo → Style chuno → Remix ready!")
st.divider()

uploaded_file = st.file_uploader(
    "📁 MP3 ya WAV song upload karo",
    type=["mp3", "wav"]
)

st.markdown("### 🎚️ Remix Style Chuno")
remix_choice = st.selectbox(
    "Kaisa remix chahiye?",
    [
        "🔥 EDM Remix",
        "😴 Lo-fi Remix", 
        "💣 Bass Boosted",
        "🌊 Slowed + Reverb",
        "🎤 Trap Remix",
        "🎸 Rock Remix"
    ]
)

col1, col2 = st.columns(2)
with col1:
    volume_boost = st.slider("🔊 Volume", -10, 10, 0)
with col2:
    speed = st.slider("⚡ Speed", 0.7, 1.5, 1.0, 0.05)

st.divider()

if st.button("🚀 Remix Banao!"):
    if uploaded_file is None:
        st.error("❌ Pehle song upload karo!")
    else:
        progress = st.progress(0)
        status = st.empty()

        try:
            with tempfile.TemporaryDirectory() as tmp:

                status.text("📥 Song load ho raha hai...")
                progress.progress(15)

                input_path = os.path.join(tmp, "input.mp3")
                with open(input_path, "wb") as f:
                    f.write(uploaded_file.read())

                status.text("🎵 Audio process ho raha hai...")
                progress.progress(35)

                song = AudioSegment.from_file(input_path)

                status.text("🎚️ Remix apply ho raha hai...")
                progress.progress(60)

                if "EDM" in remix_choice:
                    result = song.speedup(playback_speed=1.2 * speed)
                    result = result + (6 + volume_boost)

                elif "Lo-fi" in remix_choice:
                    result = song.speedup(playback_speed=0.85 * speed)
                    result = result.low_pass_filter(3000)
                    result = result + (-2 + volume_boost)

                elif "Bass" in remix_choice:
                    bass_layer = song.low_pass_filter(200) + 8
                    result = song.overlay(bass_layer)
                    result = result + volume_boost

                elif "Slowed" in remix_choice:
                    result = song.speedup(playback_speed=0.78 * speed)
                    echo1 = result - 9
                    echo2 = result - 15
                    result = result.overlay(echo1, position=300)
                    result = result.overlay(echo2, position=600)
                    result = result + volume_boost

                elif "Trap" in remix_choice:
                    result = song.speedup(playback_speed=0.95 * speed)
                    bass_layer = song.low_pass_filter(200) + 8
                    result = result.overlay(bass_layer)
                    result = result + volume_boost

                elif "Rock" in remix_choice:
                    result = song.speedup(playback_speed=1.05 * speed)
                    treble = song.high_pass_filter(800) + 5
                    result = result.overlay(treble)
                    result = result + volume_boost

                status.text("💾 Remix save ho raha hai...")
                progress.progress(85)

                output_path = os.path.join(tmp, "remix.mp3")
                result.export(output_path, format="mp3", bitrate="320k")

                with open(output_path, "rb") as f:
                    remix_data = f.read()

                progress.progress(100)
                status.text("✅ Done!")

                st.success("🎉 Tera Remix Ready Hai!")
                st.balloons()
                st.audio(remix_data, format="audio/mp3")

                name = uploaded_file.name.replace(".mp3","").replace(".wav","")
                st.download_button(
                    "⬇️ Download Karo",
                    remix_data,
                    file_name=f"{name}_remix.mp3",
                    mime="audio/mp3"
                )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Chota file try karo ya doosra song upload karo")
