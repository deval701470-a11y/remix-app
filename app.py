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
import struct
import math
import random
from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter
from pydub.generators import WhiteNoise
import tempfile

st.set_page_config(
    page_title="Lo-fi Music Maker",
    page_icon="🎧",
    layout="centered"
)

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 50%, #0a0a0a 100%);
    }
    .stButton>button {
        background: linear-gradient(90deg, #6a0dad, #ff6b6b);
        color: white;
        border-radius: 25px;
        padding: 15px 40px;
        font-size: 18px;
        width: 100%;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #ff6b6b, #6a0dad);
    }
    .stProgress > div > div {
        background: linear-gradient(90deg, #6a0dad, #ff6b6b);
    }
    h1 {
        color: #ff6b6b !important;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("# 🎧 Lo-fi Music Maker")
st.markdown("##### ✨ Koi bhi song ko ASLI Lo-fi mein badlo - Professional Quality!")
st.divider()


# ===== VINYL CRACKLE GENERATOR =====
def generate_vinyl_crackle(duration_ms, volume=-25):
    """
    Purane vinyl record jaisi crackle sound banata hai
    - Random clicks aur pops
    - Continuous soft hiss
    - Authentic vintage feel
    """
    sample_rate = 44100
    num_samples = int(sample_rate * duration_ms / 1000)

    samples = []
    for i in range(num_samples):
        # Base hiss (bohot halka)
        hiss = random.uniform(-0.003, 0.003)

        # Random clicks (thode thode gap pe)
        click = 0
        if random.random() < 0.0008:  # Rare clicks
            click = random.uniform(-0.15, 0.15)

        # Small pops
        pop = 0
        if random.random() < 0.0003:  # Very rare pops
            pop = random.uniform(-0.3, 0.3)

        # Combine
        sample = hiss + click + pop
        sample = max(-1, min(1, sample))
        samples.append(sample)

    # Convert to bytes
    raw_data = b""
    for s in samples:
        packed = struct.pack("<h", int(s * 32767))
        raw_data += packed

    crackle = AudioSegment(
        data=raw_data,
        sample_width=2,
        frame_rate=sample_rate,
        channels=1
    )

    # Volume adjust
    crackle = crackle + volume

    # Make stereo
    crackle = crackle.set_channels(2)

    return crackle


# ===== RAIN SOUND GENERATOR =====
def generate_rain_sound(duration_ms, volume=-22):
    """
    Baarish jaisi soothing sound banata hai
    - Filtered white noise
    - Soft pattering effect
    - Calming background
    """
    sample_rate = 44100
    num_samples = int(sample_rate * duration_ms / 1000)

    samples = []
    prev_sample = 0

    for i in range(num_samples):
        # Brown noise (softer than white noise)
        white = random.uniform(-1, 1)
        brown = (prev_sample + (0.02 * white)) / 1.02
        prev_sample = brown

        # Rain drops (random sharp sounds)
        drop = 0
        if random.random() < 0.001:
            drop = random.uniform(0.05, 0.2) * math.sin(
                2 * math.pi * random.uniform(2000, 6000) * i / sample_rate
            )

        sample = brown * 0.5 + drop
        sample = max(-1, min(1, sample))
        samples.append(sample)

    raw_data = b""
    for s in samples:
        packed = struct.pack("<h", int(s * 32767))
        raw_data += packed

    rain = AudioSegment(
        data=raw_data,
        sample_width=2,
        frame_rate=sample_rate,
        channels=1
    )

    # Low pass filter for realistic rain
    rain = low_pass_filter(rain, 4000)

    # Volume
    rain = rain + volume

    # Stereo
    rain = rain.set_channels(2)

    return rain


# ===== MAIN LO-FI MAKER =====
def make_professional_lofi(song, add_vinyl, add_rain, vinyl_vol, rain_vol):
    """
    PROFESSIONAL Lo-fi Production:
    1. Slow down + Pitch down
    2. Heavy muffled filter
    3. Warm bass boost
    4. Remove harsh frequencies
    5. Add reverb/echo
    6. Vinyl crackle (optional)
    7. Rain sound (optional)
    8. Soft volume
    9. Smooth fade in/out
    """

    duration_ms = len(song)

    # ===== STEP 1: Slow + Pitch Down =====
    # 0.82x speed = perfect lo-fi feel
    new_frame_rate = int(song.frame_rate * 0.82)
    lofi = song._spawn(song.raw_data, overrides={
        "frame_rate": new_frame_rate
    }).set_frame_rate(song.frame_rate)

    new_duration = len(lofi)

    # ===== STEP 2: Heavy Muffled Sound =====
    # Double low pass for extra warmth
    lofi = low_pass_filter(lofi, 2500)
    lofi = low_pass_filter(lofi, 3500)

    # ===== STEP 3: Warm Bass Boost =====
    bass = low_pass_filter(lofi, 250) + 4
    sub_bass = low_pass_filter(lofi, 100) + 2
    lofi = lofi.overlay(bass).overlay(sub_bass)

    # ===== STEP 4: Remove Harsh Frequencies =====
    lofi = high_pass_filter(lofi, 60)

    # ===== STEP 5: Reverb (Dreamy Echo) =====
    echo1 = lofi - 8
    echo2 = lofi - 14
    echo3 = lofi - 20
    lofi = lofi.overlay(echo1, position=250)
    lofi = lofi.overlay(echo2, position=500)
    lofi = lofi.overlay(echo3, position=800)

    # ===== STEP 6: Vinyl Crackle =====
    if add_vinyl:
        crackle = generate_vinyl_crackle(new_duration, volume=vinyl_vol)
        # Match length
        if len(crackle) < new_duration:
            times = (new_duration // len(crackle)) + 1
            crackle = crackle * times
        crackle = crackle[:new_duration]
        lofi = lofi.overlay(crackle)

    # ===== STEP 7: Rain Sound =====
    if add_rain:
        rain = generate_rain_sound(new_duration, volume=rain_vol)
        if len(rain) < new_duration:
            times = (new_duration // len(rain)) + 1
            rain = rain * times
        rain = rain[:new_duration]
        lofi = lofi.overlay(rain)

    # ===== STEP 8: Soft Volume =====
    lofi = lofi - 3

    # ===== STEP 9: Smooth Fade =====
    fade_in_duration = min(5000, new_duration // 4)
    fade_out_duration = min(6000, new_duration // 3)
    lofi = lofi.fade_in(fade_in_duration).fade_out(fade_out_duration)

    return lofi


# ===== UI =====

# Upload
uploaded_file = st.file_uploader(
    "📁 Song Upload Karo (MP3 / WAV)",
    type=["mp3", "wav"]
)

if uploaded_file is not None:
    file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
    st.info(f"📄 {uploaded_file.name} | {file_size:.1f} MB")

st.divider()

# Lo-fi Options
st.markdown("### 🎛️ Lo-fi Settings")

col1, col2 = st.columns(2)

with col1:
    add_vinyl = st.toggle("🎵 Vinyl Crackle", value=True,
                           help="Purane record jaisi crackling awaaz")

with col2:
    add_rain = st.toggle("🌧️ Rain Sound", value=True,
                          help="Baarish ki soothing awaaz")

# Volume controls for effects
if add_vinyl or add_rain:
    st.markdown("#### 🔊 Effects Volume")
    cols = st.columns(2)
    if add_vinyl:
        with cols[0]:
            vinyl_vol = st.slider("Vinyl Volume", -35, -15, -25,
                                   help="Zyada negative = halka")
    else:
        vinyl_vol = -25

    if add_rain:
        with cols[1]:
            rain_vol = st.slider("Rain Volume", -30, -12, -20,
                                  help="Zyada negative = halka")
    else:
        rain_vol = -20
else:
    vinyl_vol = -25
    rain_vol = -20

st.divider()

# Lo-fi info
st.markdown("### 🎧 Ye Sab AUTOMATIC Hoga:")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("```\n✅ Slow + Pitch Down\n✅ Muffled Sound\n✅ Warm Bass\n```")
with col2:
    st.markdown("```\n✅ Dreamy Reverb\n✅ Soft Volume\n✅ Smooth Fade\n```")
with col3:
    st.markdown("```\n✅ Vinyl Crackle\n✅ Rain Sound\n✅ 320kbps Export\n```")

st.divider()

# Generate
if st.button("🎧 Lo-fi Banao!"):
    if uploaded_file is None:
        st.error("❌ Pehle song upload karo!")
    else:
        progress = st.progress(0)
        status = st.empty()

        try:
            with tempfile.TemporaryDirectory() as tmp:

                # Load
                status.text("📥 Song load ho raha hai...")
                progress.progress(8)

                input_path = os.path.join(tmp, "input.mp3")
                with open(input_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                status.text("🎵 Audio read ho raha hai...")
                progress.progress(15)

                song = AudioSegment.from_file(input_path)

                song_len = len(song) // 1000
                st.info(f"🎵 Original: {song_len//60}m {song_len%60}s")

                # Process
                status.text("🎧 Lo-fi magic apply ho raha hai...")
                progress.progress(25)

                status.text("🎚️ Slow + Pitch Down...")
                progress.progress(30)

                status.text("🔇 Muffled warm sound...")
                progress.progress(40)

                status.text("🎵 Bass boost + Reverb...")
                progress.progress(50)

                # MAKE LO-FI
                result = make_professional_lofi(
                    song,
                    add_vinyl=add_vinyl,
                    add_rain=add_rain,
                    vinyl_vol=vinyl_vol,
                    rain_vol=rain_vol
                )

                progress.progress(70)

                if add_vinyl:
                    status.text("🎵 Vinyl crackle add ho raha hai...")
                    progress.progress(80)

                if add_rain:
                    status.text("🌧️ Rain sound mix ho raha hai...")
                    progress.progress(85)

                # Export
                status.text("💾 Lo-fi save ho raha hai (320kbps)...")
                progress.progress(90)

                output_path = os.path.join(tmp, "lofi_output.mp3")
                result.export(output_path, format="mp3", bitrate="320k")

                with open(output_path, "rb") as f:
                    lofi_data = f.read()

                progress.progress(100)
                status.text("✅ Done!")

                # Success
                st.success("🎧 Tera Professional Lo-fi Ready Hai!")
                st.balloons()

                # Info
                r_len = len(result) // 1000
                r_size = len(lofi_data) / (1024 * 1024)

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("⏱️ Length", f"{r_len//60}m {r_len%60}s")
                with col2:
                    st.metric("📦 Size", f"{r_size:.1f} MB")
                with col3:
                    st.metric("🎵 Quality", "320kbps")
                with col4:
                    effects = []
                    if add_vinyl:
                        effects.append("Vinyl")
                    if add_rain:
                        effects.append("Rain")
                    st.metric("🎛️ Effects", "+".join(effects) if effects else "None")

                # Player
                st.audio(lofi_data, format="audio/mp3")

                # Download
                name = uploaded_file.name.replace(".mp3","").replace(".wav","")
                st.download_button(
                    "⬇️ Lo-fi Download Karo",
                    lofi_data,
                    file_name=f"{name}_lofi.mp3",
                    mime="audio/mp3"
                )

                # Tips
                st.divider()
                st.markdown("### 💡 YouTube Upload Tips:")
                st.markdown("""
                - 🖼️ **Thumbnail:** Anime/Rain wallpaper lagao
                - 🔁 **Loop:** CapCut mein 10 baar loop karke 10min video banao
                - 📝 **Title:** "Song Name - Lo-fi Version [Chill/Study/Sleep]"
                - 🏷️ **Tags:** lofi, chill, study music, rain, relax
                """)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 MP3 use karo | 15MB se chhoti file rakho")
