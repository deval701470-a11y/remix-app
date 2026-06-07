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
import random
import struct
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
    h1 { color: #ff6b6b !important; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.markdown("# 🎧 Lo-fi Music Maker")
st.markdown("##### ✨ Professional Lo-fi - FAST!")
st.divider()


# ===== FAST VINYL CRACKLE (10x faster!) =====
def fast_vinyl_crackle(duration_ms, volume=-25):
    """1 second ka crackle banao, phir loop karo = SUPER FAST"""
    sample_rate = 44100
    # Sirf 1 second generate karo
    one_sec_samples = sample_rate
    
    samples = []
    for i in range(one_sec_samples):
        hiss = random.uniform(-0.003, 0.003)
        click = random.uniform(-0.15, 0.15) if random.random() < 0.001 else 0
        sample = max(-1, min(1, hiss + click))
        samples.append(int(sample * 32767))
    
    raw = struct.pack(f"<{len(samples)}h", *samples)
    
    one_sec = AudioSegment(
        data=raw, sample_width=2,
        frame_rate=sample_rate, channels=1
    )
    
    # Loop karke full duration banao
    times = (duration_ms // 1000) + 2
    crackle = one_sec * times
    crackle = crackle[:duration_ms]
    crackle = crackle + volume
    crackle = crackle.set_channels(2)
    return crackle


# ===== FAST RAIN SOUND (10x faster!) =====
def fast_rain_sound(duration_ms, volume=-20):
    """White noise + filter = rain sound FAST"""
    # WhiteNoise use karo (built-in = fast!)
    rain = WhiteNoise().to_audio_segment(duration=duration_ms)
    
    # Filter lagao = rain jaisi sound
    rain = low_pass_filter(rain, 3000)
    rain = high_pass_filter(rain, 200)
    
    # Volume
    rain = rain + volume
    rain = rain.set_channels(2)
    return rain


# ===== FAST LO-FI MAKER =====
def make_lofi_fast(song, add_vinyl, add_rain, vinyl_vol, rain_vol):
    """Professional Lo-fi - OPTIMIZED FOR SPEED"""
    
    # 1. Slow + Pitch Down (INSTANT - frame rate trick)
    new_frame_rate = int(song.frame_rate * 0.82)
    lofi = song._spawn(song.raw_data, overrides={
        "frame_rate": new_frame_rate
    }).set_frame_rate(song.frame_rate)
    
    duration = len(lofi)
    
    # 2. Muffled Sound (FAST - single filter)
    lofi = low_pass_filter(lofi, 2800)
    
    # 3. Warm Bass (FAST)
    bass = low_pass_filter(lofi, 250) + 4
    lofi = lofi.overlay(bass)
    
    # 4. Remove rumble
    lofi = high_pass_filter(lofi, 60)
    
    # 5. Light Reverb (FAST - sirf 2 echo)
    echo1 = lofi - 8
    echo2 = lofi - 15
    lofi = lofi.overlay(echo1, position=250)
    lofi = lofi.overlay(echo2, position=550)
    
    # 6. Vinyl Crackle (FAST method)
    if add_vinyl:
        crackle = fast_vinyl_crackle(duration, vinyl_vol)
        lofi = lofi.overlay(crackle)
    
    # 7. Rain Sound (FAST method)
    if add_rain:
        rain = fast_rain_sound(duration, rain_vol)
        lofi = lofi.overlay(rain)
    
    # 8. Soft volume
    lofi = lofi - 3
    
    # 9. Fade
    fade_in = min(4000, duration // 4)
    fade_out = min(5000, duration // 3)
    lofi = lofi.fade_in(fade_in).fade_out(fade_out)
    
    return lofi


# ===== UI =====
uploaded_file = st.file_uploader(
    "📁 Song Upload Karo (MP3/WAV)", type=["mp3", "wav"]
)

if uploaded_file is not None:
    size = len(uploaded_file.getvalue()) / (1024*1024)
    st.info(f"📄 {uploaded_file.name} | {size:.1f} MB")
    if size > 10:
        st.warning("⚠️ File badi hai! 10MB se chhoti file fast banega!")

st.divider()

st.markdown("### 🎛️ Lo-fi Effects")
col1, col2 = st.columns(2)
with col1:
    add_vinyl = st.toggle("🎵 Vinyl Crackle", value=True)
with col2:
    add_rain = st.toggle("🌧️ Rain Sound", value=True)

if add_vinyl or add_rain:
    st.markdown("#### 🔊 Effects Volume")
    cols = st.columns(2)
    vinyl_vol = -25
    rain_vol = -20
    if add_vinyl:
        with cols[0]:
            vinyl_vol = st.slider("Vinyl", -35, -15, -25)
    if add_rain:
        with cols[1]:
            rain_vol = st.slider("Rain", -30, -12, -20)
else:
    vinyl_vol = -25
    rain_vol = -20

st.divider()

st.markdown("### ✅ Automatic Features:")
st.markdown("""
✅ Slow + Pitch Down | ✅ Muffled Sound | ✅ Warm Bass
✅ Reverb | ✅ Soft Volume | ✅ Smooth Fade | ✅ 320kbps
""")

st.divider()

# GENERATE
if st.button("🎧 Lo-fi Banao! (Fast Mode ⚡)"):
    if uploaded_file is None:
        st.error("❌ Pehle song upload karo!")
    else:
        progress = st.progress(0)
        status = st.empty()
        
        try:
            with tempfile.TemporaryDirectory() as tmp:
                
                status.text("📥 Loading...")
                progress.progress(10)
                
                path = os.path.join(tmp, "input.mp3")
                with open(path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                status.text("🎵 Reading audio...")
                progress.progress(20)
                
                song = AudioSegment.from_file(path)
                slen = len(song) // 1000
                st.info(f"🎵 Original: {slen//60}m {slen%60}s")
                
                status.text("🎧 Lo-fi ban raha hai... (1-2 min)")
                progress.progress(30)
                
                # MAKE LO-FI (FAST!)
                result = make_lofi_fast(
                    song, add_vinyl, add_rain,
                    vinyl_vol, rain_vol
                )
                
                progress.progress(75)
                status.text("💾 Saving (320kbps)...")
                
                out = os.path.join(tmp, "lofi.mp3")
                result.export(out, format="mp3", bitrate="320k")
                
                with open(out, "rb") as f:
                    data = f.read()
                
                progress.progress(100)
                status.text("✅ Done!")
                
                st.success("🎧 Lo-fi Ready Hai!")
                st.balloons()
                
                # Info
                rlen = len(result) // 1000
                rsize = len(data) / (1024*1024)
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("⏱️", f"{rlen//60}m {rlen%60}s")
                with c2:
                    st.metric("📦", f"{rsize:.1f} MB")
                with c3:
                    st.metric("🎵", "320kbps")
                
                st.audio(data, format="audio/mp3")
                
                name = uploaded_file.name.replace(".mp3","").replace(".wav","")
                st.download_button(
                    "⬇️ Download Lo-fi",
                    data,
                    file_name=f"{name}_lofi.mp3",
                    mime="audio/mp3"
                )
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Chhoti MP3 file try karo (5-10MB)")
