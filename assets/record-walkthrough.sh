#!/bin/bash
# Drives the Valenox app through every screen used in the ad, while adb screenrecord
# captures the session. Dwell times are generous; exact beat timing is cut later.
set -e
export PATH="$PATH:/Users/dippu/Library/Android/sdk/platform-tools"

T() { adb shell input tap "$1" "$2"; sleep "${3:-2}"; }
BACK() { adb shell input keyevent 4; sleep 1.4; }
MORE() { adb shell input tap 1106 2509; sleep 1.6; }

adb shell screenrecord --size 1080x2400 --bit-rate 12M /sdcard/vx_rec.mp4 &
REC_PID=$!
sleep 2

# home dashboard
T 112 2509 4
adb shell input swipe 610 1800 610 1150 900; sleep 3     # scroll to steps / water
adb shell input swipe 610 1150 610 1800 900; sleep 2     # back to top

# health score detail (tap the score ring)
T 632 450 5
BACK

# food scanner
T 360 2509 6

# medicine reminders
MORE
T 632 550 5
BACK

# trends
T 609 2509 6

# heart rate
MORE
T 632 711 5
BACK

# lab reports
MORE
T 632 1170 4
BACK

# vaccinations
MORE
T 632 1331 4
BACK

# home remedies
MORE
T 632 1629 4
BACK

# family records
MORE
T 632 1009 4
BACK

# privacy
MORE
T 632 2249 5
BACK

# back to home
T 112 2509 3

adb shell pkill -INT screenrecord || true
sleep 3
wait $REC_PID 2>/dev/null || true
adb pull /sdcard/vx_rec.mp4 /Users/dippu/Documents/projects/kumardippu-site/valenox/assets/raw/walkthrough.mp4
echo "RECORDING_DONE"
