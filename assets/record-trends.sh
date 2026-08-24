#!/bin/bash
# Trends Today / Weekly / Monthly — uses only bottom-nav taps, no BACK presses,
# since BACK from a tab-root screen in this app exits to the previous task.
set -e
export PATH="$PATH:/Users/dippu/Library/Android/sdk/platform-tools"

T() { adb shell input tap "$1" "$2"; sleep "${3:-2}"; }

adb shell screenrecord --size 1080x2400 --bit-rate 12M /sdcard/vx_trends.mp4 &
REC_PID=$!
sleep 2

T 112 2509 2   # home tab, to guarantee a known starting point
T 609 2509 3   # trends tab
T 233 409 4    # today
T 609 409 4    # weekly
T 985 409 4    # monthly
adb shell input swipe 610 1900 610 900 900; sleep 4   # scroll down to BPM chart

adb shell pkill -INT screenrecord || true
sleep 3
wait $REC_PID 2>/dev/null || true
adb pull /sdcard/vx_trends.mp4 /Users/dippu/Documents/projects/kumardippu-site/valenox/assets/raw/trends.mp4
echo "RECORDING_DONE"
