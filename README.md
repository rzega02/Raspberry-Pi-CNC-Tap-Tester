# CNC Tap Test Analyzer for Raspberry Pi

A low-cost CNC machine resonance and chatter analysis system built using a Raspberry Pi 4 and MPU-6050 accelerometer.

The project allows CNC machinists, manufacturing engineers, and hobbyists to perform machine-tool tap testing, identify vibration frequencies, estimate damping ratios, and generate spindle-speed avoidance recommendations using inexpensive hardware.

---

# Overview

Machine chatter remains one of the most common productivity and quality problems in CNC machining.

Commercial modal analysis and tap-testing systems often cost several thousand dollars.

This project demonstrates how a Raspberry Pi 4B and a low-cost MPU-6050 accelerometer can be used to perform:

- Impact (tap) testing
- FFT vibration analysis
- Resonance identification
- Damping ratio estimation
- Chatter-axis identification
- RPM avoidance chart generation

The goal is to provide actionable spindle-speed recommendations based on measured tool dynamics instead of trial-and-error testing.

---

# Features

Current capabilities include:

✅ Raspberry Pi 4B platform

✅ MPU-6050 3-axis accelerometer

✅ Real-time vibration capture

✅ CSV data logging

✅ FFT spectrum analysis

✅ RMS vibration calculations

✅ Automatic dominant frequency detection

✅ Logarithmic decrement damping calculations

✅ Half-power bandwidth damping estimation

✅ Automatic chatter-axis selection

✅ Spectrum plot generation

✅ RPM avoidance chart generation

✅ Automatic report creation

✅ Headless operation support

---

# Example Output

Typical output:

Axis X: Peak ~160 Hz
Axis Y: Peak ~47 Hz
Axis Z: Peak ~99 Hz

Primary chatter axis: Y

Recommendation:
Avoid speeds causing ~47 Hz vibration.

For a 2 flute cutter:

Critical RPM ≈ 1417 RPM

The program also generates:

- FFT Spectrum Plot
- RPM Avoidance Chart
- Text Summary Report

---

# Hardware Requirements

## Required Components

| Component | Approximate Cost |
|------------|-------------|
| Raspberry Pi 4B | $50 |
| MPU-6050 Accelerometer | $5 |
| MicroSD Card | $10 |
| Mounting Hardware | $10 |
| Impact Hammer | Existing Shop Tool |

Estimated total cost:

~ $75

---

# Wiring Diagram

MPU-6050 → Raspberry Pi

VCC → 3.3V

GND → GND

SDA → GPIO2 (SDA)

SCL → GPIO3 (SCL)

I2C must be enabled in Raspberry Pi Configuration.

---

# Software Requirements

## Operating System

Tested on:

Raspberry Pi OS Bullseye

---

## Python Version

Python 3.x

---

## Required Packages

```bash
pip install mpu6050-raspberrypi numpy matplotlib
```

---

# Setup Procedure

## Create Python Virtual Environment

```bash
python3 -m venv ~/venvs/mpu6050-env
```

Activate:

```bash
source ~/venvs/mpu6050-env/bin/activate
```

Install dependencies:

```bash
pip install mpu6050-raspberrypi numpy matplotlib
```

---

# Running the Program

Start the application:

```bash
python tap_test.py
```

Follow the prompts:

1. Mount accelerometer.
2. Tap tool or holder.
3. Capture vibration data.
4. View FFT results.
5. View RPM avoidance chart.

---

# Theory of Operation

## Step 1 – Impact Excitation

The cutter, holder, or machine structure is struck with a light tap.

This excites the natural frequencies of the system.

---

## Step 2 – Data Acquisition

The MPU-6050 records vibration acceleration in:

- X axis
- Y axis
- Z axis

Acceleration data is stored in CSV format.

---

## Step 3 – Signal Conditioning

The program:

- Removes DC offset
- Applies a Hanning window
- Prepares data for FFT analysis

---

## Step 4 – FFT Analysis

The Fast Fourier Transform converts:

Time Domain

into

Frequency Domain

allowing dominant vibration frequencies to be identified.

---

## Step 5 – Resonance Detection

The program identifies:

- Dominant frequency
- Dominant axis
- RMS vibration level

for each measurement axis.

---

## Step 6 – Damping Estimation

Two damping estimation methods are used:

### Logarithmic Decrement

Uses free-decay vibration peaks to estimate damping ratio.

### Half-Power Bandwidth

Uses resonance peak width in the FFT spectrum.

---

## Step 7 – Chatter Prediction

The lowest significant flexible mode is selected as the primary chatter mode.

RPM avoidance zones are calculated from:

RPM = (Frequency × 60) / Number of Flutes

---

# Mathematical Background

## RMS

RMS vibration level:

RMS = sqrt(sum(x²)/N)

---

## FFT

FFT converts acceleration data from the time domain to the frequency domain.

---

## Logarithmic Decrement

δ = (1/n) × ln(x1/xn)

---

## Damping Ratio

ζ = δ / sqrt(4π² + δ²)

---

## Tooth Passing Frequency

TPF = RPM × Flutes / 60

When tooth passing frequency matches a structural resonance:

Chatter may occur.

---

# Example Use Cases

This project may be useful for:

- CNC Milling
- CNC Turning
- Toolholder Testing
- Fixture Testing
- Educational Modal Analysis
- Manufacturing Engineering
- Machine Dynamics Research

---

# Known Limitations

Current version does not create a full industrial Stability Lobe Diagram.

A complete SLD would require:

- Instrumented impact hammer
- Frequency Response Function (FRF)
- Modal stiffness estimation
- Cutting force coefficients

Current implementation provides practical spindle-speed avoidance guidance.

---

# Future Enhancements

Planned improvements:

- Instrumented hammer support
- Full FRF analysis
- Stability lobe generation
- Touchscreen interface
- Local web dashboard
- Wireless sensor support
- AI-assisted chatter detection
- Machine database for tool libraries

---

# Project Status

Current Status:

Working Prototype

Validated on CNC machine tap tests.

---

# Contributing

Suggestions, bug reports, and pull requests are welcome.

---

# License

MIT License

---

# Author

Robert Zega

President

Miyama USA, Inc

Manufacturing Engineer and Raspberry Pi Enthusiast

Louisville, Kentucky USA

---
