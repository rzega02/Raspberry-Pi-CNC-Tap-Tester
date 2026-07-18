# PiModal CNC - CNC Tap Test Analyzer for Raspberry Pi

A low-cost CNC machine resonance and chatter analysis system built using a Raspberry Pi 4 and MPU-6050 accelerometer.

<img width="1024" height="1024" alt="Generated Image July 18, 2026 - 3_18AM" src="https://github.com/user-attachments/assets/98e70e16-9dd0-4c10-995a-5ffae03e51b4" />

[![License-Apache-2.0](https://img.shields.io/badge/Apache-2.0-grey?style=flat-square)](License)
[![Python 3.7+](https://img.shields.io/badge/Python-3.7+-green.svg)](https://www.python.org/downloads/)
[![Raspberry Pi 4B](https://img.shields.io/badge/Raspberry_Pi-4B-red.svg)](https://www.raspberrypi.org/)

The project allows CNC machinists, manufacturing engineers, and hobbyists to perform machine-tool tap testing, identify vibration frequencies, estimate damping ratios, and generate spindle-speed avoidance recommendations. In the picture the raspberry pi has a breakout board on it to make wiring easier and it also has a small 7 inch touch screen monitor on the front of it.  This is optional but a good idea for shop floor use.
---
## 🚀 Quick Start (5 Minutes)

## Get up and running in minutes:

```bash
# 1. Clone the repository
git clone https://github.com/rzega02/PiModal-CNC---Raspberry-Pi-CNC-Tap-Tester.git
cd PiModal-CNC---Raspberry-Pi-CNC-Tap-Tester

# 2. Create virtual environment
python3 -m venv env
source env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify hardware connection
i2cdetect -y 1
# Should show "68" in the output

# 5. Run the program
python tap_test.py
```

**Next:** Press **Enter** to start a tap test, tap your tool with a hammer, and get instant vibration analysis! 

For detailed setup instructions, see [INSTALLATION.md](INSTALLATION.md).

---

## 📊 Real-World Example

Here's actual data from a CNC spindle with a 2-flute endmill:

**Test Data File:** `tap_20260622_163222.csv`  
**Duration:** ~4.0 seconds of vibration capture  
**Sample Rate:** ~333 Hz

### Analysis Results

| Axis | Peak Frequency | RMS Level | Damping Ratio (ζ) | Interpretation |
|------|---|---|---|---|
| **X** | 26.8 Hz | 0.941 g | 0.0600 | **Primary chatter mode** (lowest = worst) |
| Y | 62.7 Hz | 0.770 g | 0.1102 | Secondary mode |
| Z | 80.9 Hz | 0.450 g | 0.0846 | Higher frequency mode |

### Recommendation

**Avoid speeds causing ~27 Hz vibration:**
- For a 2-flute tool: ~**803 RPM** excites this mode
- Better choices: >1000 RPM or <600 RPM
- Use the generated avoidance chart to select safe speeds

**Generated Outputs:**
- ✅ FFT spectrum plots (PNG)
- ✅ RPM avoidance chart (PNG)
- ✅ Analysis summary (TXT)
- ✅ Raw data (CSV)

<img width="700" height="1200" alt="FFT Spectrum" src="https://github.com/user-attachments/assets/f3cec547-9b3d-4b5c-9b97-6190cb24440b" />

<img width="1500" height="750" alt="RPM Avoidance Chart" src="https://github.com/user-attachments/assets/41d3616d-a029-4636-bed0-38aebea43cee" />

---

## 📷 Hardware Assembly

### Complete System Cost: ~$75

Your accelerometer is mounted directly on the spindle or tool holder for accurate measurements.

### Wiring

```
MPU-6050 Pin → Raspberry Pi GPIO
─────────────────────────────────
VCC        → 3.3V (Pin 1)
GND        → GND (Pin 6, 9, 14, 20, 25, 30, 34, 39)
SDA (GPIO2)  → Pin 3
SCL (GPIO3)  → Pin 5
INT (Optional) → Pin 7 (GPIO 4)
```

**See [INSTALLATION.md](INSTALLATION.md#hardware-setup) for complete wiring diagrams and assembly instructions.**

---

## ✨ Features

Current capabilities include:

✅ **Raspberry Pi 4B platform**  
✅ **MPU-6050 3-axis accelerometer**  
✅ **Real-time vibration capture**  
✅ **CSV data logging**  
✅ **FFT spectrum analysis with windowing**  
✅ **RMS vibration calculations**  
✅ **Automatic dominant frequency detection**  
✅ **Logarithmic decrement damping calculations**  
✅ **Half-power bandwidth damping estimation**  
✅ **Automatic chatter-axis selection**  
✅ **Spectrum plot generation (PNG)**  
✅ **RPM avoidance chart generation**  
✅ **Automatic report creation (TXT)**  
✅ **Headless operation support**  

---

## 📋 Requirements

### Hardware

| Component | Approx Cost | Purpose |
|-----------|---|---|
| Raspberry Pi 4B | $50 | Main processor |
| MPU-6050 Accelerometer | $5 | 3-axis vibration sensor |
| MicroSD Card | $10 | OS storage |
| USB Power Supply | $10 | Power delivery |
| Mounting Hardware | $5 | Accelerometer mounting |
| **Total** | **~$75** | **Complete system** |

### Software

- **OS:** Raspberry Pi OS Bullseye (or newer)
- **Python:** 3.7+
- **Dependencies:** See [requirements.txt](requirements.txt)

---

## 🔧 Installation

### Option 1: Quick Installation (Recommended)

```bash
git clone https://github.com/rzega02/PiModal-CNC---Raspberry-Pi-CNC-Tap-Tester.git
cd PiModal-CNC---Raspberry-Pi-CNC-Tap-Tester
python3 -m venv env && source env/bin/activate
pip install -r requirements.txt
```

### Option 2: Step-by-Step Installation

See **[INSTALLATION.md](INSTALLATION.md)** for:
- Detailed setup procedures
- Hardware wiring diagrams
- I2C configuration
- Troubleshooting guide
- Permission fixes
- Display configuration

---

## 📖 Using the Program

### Starting a Test

```bash
python tap_test.py
```

### Test Procedure

1. **Press Enter** to start data capture
2. **Tap your tool** firmly with a hammer
3. **Let it ring down** for 3-5 seconds
4. **Press Y** to analyze the results
5. **Enter number of flutes** (e.g., 2, 3, or 4)
6. **View the results:**
   - FFT spectrum plots
   - RPM avoidance chart
   - Analysis summary

See **[TESTING_GUIDE.md](TESTING_GUIDE.md)** for:
- Proper tap procedure
- Interpretation of results
- Best practices
- Troubleshooting common issues
- Advanced testing techniques

---

## 🔬 How It Works

### Step 1: Impact Excitation
The tool or holder is tapped with a hammer, exciting natural frequencies.

### Step 2: Data Acquisition
The MPU-6050 records acceleration on three axes (X, Y, Z) and saves to CSV.

### Step 3: Signal Conditioning
- Remove DC offset
- Apply Hanning window
- Prepare for FFT

### Step 4: FFT Analysis
Fast Fourier Transform converts time-domain data to frequency-domain.

### Step 5: Resonance Detection
Identifies dominant frequencies and RMS vibration levels on each axis.

### Step 6: Damping Estimation
Uses two methods:
- **Logarithmic Decrement:** Analyzes free-decay oscillation peaks
- **Half-Power Bandwidth:** Uses resonance peak width in FFT

### Step 7: Chatter Prediction
Selects the lowest flexible mode (primary chatter driver) and calculates RPM avoidance zones:

```
Critical RPM = (Frequency × 60) / Number of Flutes
```

---

## 📚 Theory & Mathematics

### RMS Vibration Level
```
RMS = √(Σx² / N)
```
Measures overall acceleration in g's.

### FFT (Fast Fourier Transform)
Converts acceleration from time domain to frequency domain.

### Logarithmic Decrement
```
δ = (1/n) × ln(x₁/xₙ)
```
Measures rate of amplitude decay in oscillations.

### Damping Ratio
```
ζ = δ / √(4π² + δ²)
```
Dimensionless measure of system damping (0 = undamped, 1 = critically damped).

### Tooth Passing Frequency
```
TPF = RPM × Flutes / 60
```
When TPF matches a structural resonance, chatter occurs.

For complete theory, see the [Technical Whitepaper](./Technical%20Whitepaper%20-%20CNC%20Tap%20Testing.pdf).

---

## 💡 Use Cases

This project is useful for:

- **CNC Milling:** Identify spindle speed limitations
- **CNC Turning:** Characterize tool holder dynamics
- **Toolholder Testing:** Compare different holders
- **Fixture Testing:** Analyze workholding stiffness
- **Educational Modal Analysis:** Learn vibration mechanics
- **Manufacturing Engineering:** Optimize cutting parameters
- **Machine Dynamics Research:** Baseline system characterization

---

## ⚠️ Known Limitations

**Current version provides practical RPM avoidance guidance, not full industrial-grade analysis:**

- ❌ No full Stability Lobe Diagram (simplified zones only)
- ❌ Single-axis tap testing (no multi-axis FRF)
- ❌ No instrumented hammer support
- ❌ No cutting force integration
- ❌ No phase information

**To create a full Stability Lobe Diagram would require:**
- Instrumented impact hammer
- Frequency Response Function (FRF) analysis
- Modal stiffness estimation
- Cutting force coefficients

See [Future Enhancements](#-future-enhancements) for planned improvements.

---

## 🔮 Future Enhancements

Planned improvements for future versions:

- [ ] Instrumented hammer support
- [ ] Full Frequency Response Function (FRF) analysis
- [ ] Complete Stability Lobe generation
- [ ] Touchscreen interface for Raspberry Pi
- [ ] Local web dashboard
- [ ] Wireless sensor network support
- [ ] Machine learning chatter detection
- [ ] Tool library database
- [ ] Integration with CNC control software
- [ ] AI-assisted troubleshooting

---

## 🐛 Troubleshooting

### Quick Fixes

**"I2C device not found"**
```bash
i2cdetect -y 1  # Should show "68" in output
```
Check wiring (GPIO2/GPIO3 pins).

**"No module named mpu6050"**
```bash
source env/bin/activate
pip install -r requirements.txt
```

**"Permission denied"**
```bash
sudo usermod -aG i2c $USER
sudo usermod -aG gpio $USER
newgrp i2c
```

For complete troubleshooting, see **[INSTALLATION.md#troubleshooting](INSTALLATION.md#troubleshooting)**.

---

## 📝 Project Status

**Status:** ✅ Working Prototype  
**Last Updated:** 2026-07-17  
**Validated on:** CNC machine tap tests with endmills and drills  

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## 🤝 Contributing

Suggestions, bug reports, and pull requests are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under **Apache 2.0** - see [LICENSE](LICENSE) file for details.

---

## 👨‍💼 Author

**Robert Zega**  
President, Miyama USA, Inc.  
Manufacturing Engineer and Raspberry Pi Enthusiast  
Louisville, Kentucky USA  

---

## 📞 Support & Documentation

- **Installation Guide:** [INSTALLATION.md](INSTALLATION.md)
- **Testing Procedure:** [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Version History:** [CHANGELOG.md](CHANGELOG.md)
- **Issues & Discussions:** [GitHub Issues](https://github.com/rzega02/PiModal-CNC---Raspberry-Pi-CNC-Tap-Tester/issues)

---

## 🎯 Getting Started

1. **Install:** Follow [INSTALLATION.md](INSTALLATION.md)
2. **Learn:** Read [TESTING_GUIDE.md](TESTING_GUIDE.md)
3. **Test:** Run `python tap_test.py`
4. **Share:** Post your results!

---

**Happy tap testing! 🔧**
