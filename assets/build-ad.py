#!/usr/bin/env python3
"""Builds the Valenox YouTube ad.

Each segment = one voiceover beat: a 1920x1080 branded plate with the real app
recording composited into the phone bezel. Segment lengths are derived from the
measured voiceover timings, so cuts land in the gaps between spoken lines.
"""
import json
import os
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

# Three source recordings, each re-encoded to constant 30fps so seeks land
# exactly on the intended screen (screenrecord's native VFR output does not).
FOOTAGE = {
    "walk":    ("raw/walkthrough.mp4", "ad_build/walkthrough_kf.mp4"),
    "extras":  ("raw/extras.mp4",      "ad_build/extras_kf.mp4"),
    "trends":  ("raw/trends.mp4",      "ad_build/trends_kf.mp4"),
}
OUT = "valenox-ad-1080p.mp4"
SCREEN_X, SCREEN_Y, SCREEN_W, SCREEN_H = 1268, 110, 387, 860

# plate, footage key, source start, usable footage length, segment length
# Source windows sit inside the screen intervals found by scene detection, so
# the clone-padded tail freezes on the intended screen, never the next one:
#   walk:   home 0.0-4.1 | scrolled 4.1-8.1 | home 8.1-11.2 | score 11.2-16.2
#           scan 17.7-23.8 | medicines 25.5-30.5 | lab 48.1-52.2 | vaccines 55.4-59.5
#           remedies 62.7-66.8 | family 70.0-74.0 | privacy 77.2-82.3
#   extras: heart rate 3.8-8.9 | breathing (live countdown) 16.4-23.5
#   trends: today (BPM chart) 4.0-11.2 | weekly/monthly (bar charts) 11.2-15.2
SEGMENTS = [
    ("plate0",  "walk",   0.5, 3.50, 4.12),   # home dashboard
    ("plate1",  "walk",  18.1, 5.30, 6.46),   # food scanner
    ("plate2",  "walk",   4.3, 3.40, 3.44),   # steps / water
    ("plate3",  "extras", 4.1, 4.60, 4.60),   # heart rate detail
    ("plate4",  "extras", 16.7, 6.60, 6.60),  # breathing (live countdown)
    ("plate5",  "walk",  25.9, 4.20, 4.47),   # medicines
    ("plate6",  "walk",  11.6, 4.20, 4.58),   # health score
    ("plate7",  "trends", 4.3, 3.60, 3.60),   # trends today (BPM chart)
    ("plate8",  "trends", 11.6, 3.40, 3.40),  # trends weekly/monthly (bars)
    ("plate9",  "walk",  48.5, 1.74, 1.7425), # lab reports
    ("plate9",  "walk",  55.8, 1.74, 1.7425), # vaccinations
    ("plate9",  "walk",  63.0, 1.74, 1.7425), # home remedies
    ("plate9",  "walk",  70.3, 1.74, 1.7425), # family records
    ("plate10", "walk",  77.7, 4.30, 4.55),   # privacy
    ("plate11", None, None, None, 6.41),      # end card
]


def run(args):
    subprocess.run(args, check=True)


def build_segment(idx, plate, footage_key, src_start, src_len, out_len):
    dst = f"ad_build/seg{idx:02d}.mp4"
    if src_start is None:
        run(["ffmpeg", "-y", "-loop", "1", "-i", f"ad_build/{plate}.png",
             "-t", f"{out_len}", "-r", "30", "-pix_fmt", "yuv420p",
             "-c:v", "libx264", "-crf", "18", "-preset", "medium",
             "-vf", "scale=1920:1080,setsar=1", dst, "-loglevel", "error"])
        return dst

    _, kf = FOOTAGE[footage_key]
    pad = max(0.0, out_len - src_len) + 0.5
    fc = (
        f"[1:v]trim=duration={src_len},setpts=PTS-STARTPTS,"
        f"scale={SCREEN_W}:{SCREEN_H},setsar=1,fps=30,"
        f"tpad=stop_mode=clone:stop_duration={pad}[v];"
        f"[2:v]format=gray,scale={SCREEN_W}:{SCREEN_H}[m];"
        f"[v][m]alphamerge[va];"
        f"[0:v]scale=1920:1080,setsar=1,fps=30[bg];"
        f"[bg][va]overlay={SCREEN_X}:{SCREEN_Y}[out]"
    )
    run(["ffmpeg", "-y",
         "-loop", "1", "-i", f"ad_build/{plate}.png",
         "-ss", f"{src_start}", "-i", kf,
         "-i", "ad_build/mask.png",
         "-filter_complex", fc, "-map", "[out]",
         "-t", f"{out_len}", "-r", "30", "-pix_fmt", "yuv420p",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         dst, "-loglevel", "error"])
    return dst


for raw, kf in FOOTAGE.values():
    if not os.path.exists(kf):
        run(["ffmpeg", "-y", "-i", raw, "-vf", "fps=30", "-fps_mode", "cfr",
             "-c:v", "libx264", "-crf", "16", "-preset", "fast",
             "-g", "15", "-keyint_min", "15", "-an", kf, "-loglevel", "error"])

segs = [build_segment(i, *s) for i, s in enumerate(SEGMENTS)]
print(f"built {len(segs)} segments")

with open("ad_build/concat.txt", "w") as f:
    for s in segs:
        f.write(f"file '{os.path.basename(s)}'\n")

# Background music bed: royalty-free Apple Loops stems (cleared for use in any
# video by Apple's license), mixed and looped to the exact ad length. No voiceover.
AD_DUR = sum(s[-1] for s in SEGMENTS)
STEMS = ["Contrails Bass", "Contrails Synth", "Contrails Lead Guitar"]
LOOP_DIR = "/Library/Audio/Apple Loops/Apple/07 Chillwave"
os.makedirs("music", exist_ok=True)
if not os.path.exists("music/bed.m4a"):
    wavs = []
    for stem in STEMS:
        wav = f"music/{stem.replace(' ', '_')}.wav"
        run(["ffmpeg", "-y", "-i", f"{LOOP_DIR}/{stem}.caf", "-ar", "48000", "-ac", "2",
             wav, "-loglevel", "error"])
        wavs.append(wav)
    args = ["ffmpeg", "-y"]
    for w in wavs:
        args += ["-i", w]
    args += ["-filter_complex", f"amix=inputs={len(wavs)}:duration=first:dropout_transition=0,volume=1.4[mixed]",
              "-map", "[mixed]", "music/loop_mixed.wav", "-loglevel", "error"]
    run(args)
    run(["ffmpeg", "-y", "-stream_loop", "5", "-i", "music/loop_mixed.wav", "-t", f"{AD_DUR}",
         "-af", f"afade=t=in:st=0:d=1.2,afade=t=out:st={AD_DUR - 2.0}:d=2.0,loudnorm=I=-20:TP=-2:LRA=9",
         "-c:a", "aac", "-b:a", "192k", "music/bed.m4a", "-loglevel", "error"])

run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "ad_build/concat.txt",
     "-i", "music/bed.m4a",
     "-map", "0:v", "-map", "1:a",
     "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
     OUT, "-loglevel", "error"])

dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "default=noprint_wrappers=1:nokey=1", OUT],
                     capture_output=True, text=True).stdout.strip()
print(f"{OUT}: {float(dur):.2f}s")
