import sys
try:
    import audioop
except ImportError:
    try:
        import audioop_lts as audioop
        sys.modules["audioop"] = audioop
    except ImportError:
        pass

import streamlit as st
import os
from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter
import tempfile
import io

st.set_page_config(
    page_title="Auto Remix Maker",
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
    .stProgress > div > div {
        background-color: #ff4b4b;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("# 🎵 Auto Remix Maker")
st.markdown("#### Song upload karo → Style chuno → Remix ready!")
st.markdown("##### 🎧 Full song remix - No cutting!")
st.divider()

# Upload
uploaded_file = st.file_uploader(
    "📁 MP3 ya WAV song upload karo",
    type=["mp3", "wav"]
)

if uploaded_file is not None:
    file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
    st.info(f"📄 File: {uploaded_file.name} | Size: {file_size:.1f} MB")

st.divider()

# Remix Style
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

# Settings
col1, col2 = st.columns(2)
with col1:
    volume_boost = st.slider("🔊 Volume", -10, 10, 0)
with col2:
    speed = st.slider("⚡ Speed", 0.7, 1.5, 1.0, 0.05)

st.divider()


# ===== PROPER LO-FI FUNCTION (FAST + HIGH QUALITY) =====
def make_lofi(song, speed_factor, vol_boost):
    """
    Proper Lo-fi remix:
    1. Pitch down (frame rate change - FAST method)
    2. Low pass filter (muffled sound)
    3. Warmth add (slight bass boost)
    4. Soft volume
    5. Fade in/out
    """
    # Step 1: Slow down + Pitch down using frame rate trick (SUPER FAST!)
    # Ye method speedup() se 10x fast hai
    new_frame_rate = int(song.frame_rate * speed_factor)
    slow_song = song._spawn(song.raw_data, overrides={
        "frame_rate": new_frame_rate
    }).set_frame_rate(song.frame_rate)

    # Step 2: Low pass filter - muffled/warm sound (Lo-fi signature)
    lofi = low_pass_filter(slow_song, 2500)

    # Step 3: Warmth - slight bass boost
    bass = low_pass_filter(slow_song, 300) + 3
    lofi = lofi.overlay(bass)

    # Step 4: High pass - remove rumble
    lofi = high_pass_filter(lofi, 80)

    # Step 5: Volume adjust (Lo-fi is soft)
    lofi = lofi + (-2 + vol_boost)

    # Step 6: Smooth fade
    lofi = lofi.fade_in(3000).fade_out(4000)

    return lofi


# ===== EDM FUNCTION =====
def make_edm(song, speed_factor, vol_boost):
    new_frame_rate = int(song.frame_rate * speed_factor)
    fast_song = song._spawn(song.raw_data, overrides={
        "frame_rate": new_frame_rate
    }).set_frame_rate(song.frame_rate)

    result = fast_song + (6 + vol_boost)
    result = result.fade_in(1000).fade_out(2000)
    return result


# ===== BASS BOOSTED FUNCTION =====
def make_bass_boosted(song, vol_boost):
    bass_layer = low_pass_filter(song, 200) + 10
    mid_layer = low_pass_filter(song, 500) + 3
    result = song.overlay(bass_layer).overlay(mid_layer)
    result = result + vol_boost
    result = result.fade_in(1000).fade_out(2000)
    return result


# ===== SLOWED + REVERB FUNCTION =====
def make_slowed_reverb(song, speed_factor, vol_boost):
    # Slow down
    new_frame_rate = int(song.frame_rate * speed_factor)
    slow_song = song._spawn(song.raw_data, overrides={
        "frame_rate": new_frame_rate
    }).set_frame_rate(song.frame_rate)

    # Reverb effect (echo layers)
    echo1 = slow_song - 7
    echo2 = slow_song - 12
    echo3 = slow_song - 18

    result = slow_song.overlay(echo1, position=200)
    result = result.overlay(echo2, position=450)
    result = result.overlay(echo3, position=700)

    result = result + vol_boost
    result = result.fade_in(3000).fade_out(4000)
    return result


# ===== TRAP FUNCTION =====
def make_trap(song, speed_factor, vol_boost):
    new_frame_rate = int(song.frame_rate * speed_factor)
    trap_song = song._spawn(song.raw_data, overrides={
        "frame_rate": new_frame_rate
    }).set_frame_rate(song.frame_rate)

    bass_layer = low_pass_filter(trap_song, 200) + 10
    result = trap_song.overlay(bass_layer)
    result = result + vol_boost
    result = result.fade_in(1000).fade_out(2000)
    return result


# ===== ROCK FUNCTION =====
def make_rock(song, speed_factor, vol_boost):
    new_frame_rate = int(song.frame_rate * speed_factor)
    rock_song = song._spawn(song.raw_data, overrides={
        "frame_rate": new_frame_rate
    }).set_frame_rate(song.frame_rate)

    treble = high_pass_filter(rock_song, 800) + 5
    result = rock_song.overlay(treble)
    result = result + vol_boost
    result = result.fade_in(1000).fade_out(2000)
    return result


# ===== GENERATE BUTTON =====
if st.button("🚀 Remix Banao!"):
    if uploaded_file is None:
        st.error("❌ Pehle song upload karo!")
    else:
        progress = st.progress(0)
        status = st.empty()

        try:
            with tempfile.TemporaryDirectory() as tmp:

                # Load
                status.text("📥 Song load ho raha hai...")
                progress.progress(10)

                input_path = os.path.join(tmp, "input.mp3")
                with open(input_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                status.text("🎵 Audio process ho raha hai...")
                progress.progress(25)

                song = AudioSegment.from_file(input_path)

                song_length_sec = len(song) // 1000
                song_min = song_length_sec // 60
                song_sec = song_length_sec % 60
                status.text(f"🎵 Song: {song_min}m {song_sec}s | Remix apply ho raha hai...")
                progress.progress(40)

                # Apply remix
                result = None

                if "EDM" in remix_choice:
                    result = make_edm(song, 1.2 * speed, volume_boost)

                elif "Lo-fi" in remix_choice:
                    result = make_lofi(song, 0.85 * speed, volume_boost)

                elif "Bass" in remix_choice:
                    result = make_bass_boosted(song, volume_boost)

                elif "Slowed" in remix_choice:
                    result = make_slowed_reverb(song, 0.78 * speed, volume_boost)

                elif "Trap" in remix_choice:
                    result = make_trap(song, 0.95 * speed, volume_boost)

                elif "Rock" in remix_choice:
                    result = make_rock(song, 1.05 * speed, volume_boost)

                progress.progress(70)
                status.text("💾 Remix save ho raha hai (320kbps)...")

                # Export
                output_path = os.path.join(tmp, "remix.mp3")
                result.export(output_path, format="mp3", bitrate="320k")

                with open(output_path, "rb") as f:
                    remix_data = f.read()

                progress.progress(100)
                status.text("✅ Done!")

                # Success
                st.success("🎉 Tera FULL Remix Ready Hai!")
                st.balloons()

                # Info
                remix_length_sec = len(result) // 1000
                remix_min = remix_length_sec // 60
                remix_sec = remix_length_sec % 60
                remix_size = len(remix_data) / (1024 * 1024)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("⏱️ Length", f"{remix_min}m {remix_sec}s")
                with col2:
                    st.metric("📦 Size", f"{remix_size:.1f} MB")
                with col3:
                    st.metric("🎵 Quality", "320kbps")

                st.audio(remix_data, format="audio/mp3")

                name = uploaded_file.name.replace(".mp3", "").replace(".wav", "")
                st.download_button(
                    "⬇️ Full Remix Download Karo",
                    remix_data,
                    file_name=f"{name}_lofi_remix.mp3",
                    mime="audio/mp3"
                )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 MP3 file use karo | File 15MB se chhoti rakho")
