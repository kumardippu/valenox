#!/bin/bash
# Supplementary capture: heart rate detail, breathing exercise (live animation),
# and Trends Today/Weekly/Monthly — none of these were in the original walkthrough.
set -e
export PATH="$PATH:/Users/dippu/Library/Android/sdk/platform-tools"

T() { adb shell input tap "$1" "$2"; sleep "${3:-2}"; }
BACK() { adb shell input keyevent 4; sleep 1.2; }

adb shell screenrecord --size 1080x2400 --bit-rate 12M /sdcard/vx_extra.mp4 &
REC_PID=$!
sleep 2

# home -> heart rate detail
T 112 2509 2
T 299 1609 5

BACK
sleep 1

# home -> breathing exercise -> start the live breathing animation
T 112 2509 2
T 570 1836 3
T 610 1820 7

BACK
sleep 1
BACK
sleep 1

# home -> trends: today / weekly / monthly
T 112 2509 2
T 609 2509 3
T 233 409 3
T 609 409 3
T 985 409 3
adb shell input swipe 610 1800 610 900 900; sleep 3

BACK
T 112 2509 2

adb shell pkill -INT screenrecord || true
sleep 3
wait $REC_PID 2>/dev/null || true
adb pull /sdcard/vx_extra.mp4 /Users/dippu/Documents/projects/kumardippu-site/valenox/assets/raw/extras.mp4
echo "RECORDING_DONE"
