# Tap Testing Procedure Guide

This guide explains how to properly perform a tap test and interpret the results.

## Table of Contents

- [Before Testing](#before-testing)
- [During Testing](#during-testing)
- [Interpretation](#interpretation)
- [Tips & Best Practices](#tips--best-practices)
- [Common Issues](#common-issues)

---

## Before Testing

### 1. Hardware Preparation

<img width="896" height="1195" alt="Generated Image July 18, 2026 - 3_27AM" src="https://github.com/user-attachments/assets/ed3159db-4dae-419f-b05f-a24e9720565a" />
This shows the hardware I use, small touch screen 7 inch monitor not included.  The device on very right is not needed, just the middle sensor.

- ✓ Verify the MPU-6050 is **rigidly mounted** to the tool holder or spindle nose
- ✓ Ensure all I2C wires are **secure and undamaged**
- ✓ **Stop the spindle** completely (zero RPM)
- ✓ Disable any automatic coolant or chip evacuation systems
- ✓ Ensure the work area is **clear and safe**
- ✓ Have an **impact hammer** ready (dead-blow hammer recommended)


### 2. Software Preparation

```bash
# Activate virtual environment
source env/bin/activate

# Navigate to project directory
cd ~/path/to/PiModal-CNC

# Start the program
python tap_test.py
```

You should see:
```
=== CNC Tap Test Program ===
Press Enter to capture data, or type Q then Enter to quit.
Start new measurement (Enter) or quit (Q):
```

### 3. Accelerometer Orientation

Note the orientation of your accelerometer:
- **X-axis:** Usually points toward the machine bed (horizontal)
- **Y-axis:** Usually points toward one side (horizontal)
- **Z-axis:** Usually points upward (vertical)

**Keep this orientation consistent** between tests!

---

## During Testing

<img width="1260" height="832" alt="Generated Image July 18, 2026 - 3_26AM" src="https://github.com/user-attachments/assets/f6b3597b-7521-4a9e-bff1-f5f1f461258d" />

### Step 1: Position for Impact

1. Locate the most flexible part of your tool setup (usually the tool tip)
2. Plan to tap **perpendicular to the surface** for best results
3. For end mills: tap from the side (radial direction)
4. For drills: tap axially (along the tool axis)

### Step 2: Start Data Capture

When ready to tap:

```
Start new measurement (Enter) or quit (Q):
```

Press **Enter** ⏎ to start capturing data.

The program will begin recording. You'll see:
```
Capturing 8.0 s of data... (saving to tap_20260622_163222.csv)
```

### Step 3: Perform the Tap

**Immediately after starting capture:**

1. Deliver a **firm, controlled tap** with your impact hammer
2. Tap should be a **single clean impact** (not multiple hits)
3. Contact should be **perpendicular to the tool** or holder surface
4. Tap force should be **moderate** (not too light, not too hard)
   - Too light: signal may be too small to analyze
   - Too hard: may damage the accelerometer or tool

**Example tap locations:**
- End mill: tap the side of the flute
- Drill: tap axially on the tool shank
- Tool holder: tap near the tool interface

### Step 4: Ring Down

After the tap:

1. **Do not disturb the system** for the remainder of the capture
2. Let the tool **vibrate freely** for 3-5 seconds
3. Allow oscillations to **decay naturally** (do not dampen)
4. The capture will automatically stop after 8 seconds

### Step 5: Data Saved

Once capture is complete:

```
Data capture complete.
Analyze the last run? (Y/N):
```

Type **Y** to proceed with FFT analysis, or **N** to skip and take another measurement.

---

## Interpretation

### Understanding the Output

When you analyze a test, you'll receive:

#### 1. FFT Spectrum Plots

Three plots (one per axis) showing:

- **X-axis:** Frequency (Hz)
- **Y-axis:** Magnitude (amplitude)
- **Red dashed line:** Dominant (peak) frequency

**Example interpretation:**

```
Axis X: Peak ~26.8 Hz
Axis Y: Peak ~62.7 Hz
Axis Z: Peak ~80.9 Hz
```

The **lowest frequency** typically indicates the most problematic chatter mode.

#### 2. RMS Vibration Level

Root-Mean-Square acceleration in **g's**

- **< 0.5 g:** Normal, well-damped system
- **0.5 - 1.0 g:** Moderate vibration, acceptable
- **> 1.0 g:** High vibration, loose tooling or worn bearings

```
Axis X: RMS 0.941 g   ← High (something might be loose)
Axis Y: RMS 0.770 g   ← Moderate
Axis Z: RMS 0.450 g   ← Good
```

#### 3. Damping Ratio (ζ)

Indicates how quickly oscillations decay

- **ζ = 0.05:** Very lightly damped (sharp, sustained oscillations)
- **ζ = 0.10:** Lightly damped
- **ζ = 0.20+:** Well damped (quick decay)

```
Axis X: ζ = 0.0600   ← Light damping (precision system)
Axis Y: ζ = 0.1102   ← Moderate damping
Axis Z: ζ = 0.0846   ← Light damping
```

#### 4. Frequency Interpretation

**Different frequency ranges indicate different sources:**

| Frequency Range | Typical Source |
|-----------------|---|
| 15-50 Hz | Spindle bearing preload, tool holder, spindle nose runout |
| 50-150 Hz | Tool geometry, holder stiffness, spindle/holder combinations |
| 150-300 Hz | Tool material properties, small diameter tools |
| 300+ Hz | Measurement noise or very small tool vibrations |

#### 5. Primary Chatter Axis

The program selects the **lowest significant flexible mode:**

```
Primary chatter axis selected: Axis X (lowest significant flexible mode at ~26.8 Hz)
Recommendation: Avoid speeds causing ~27 Hz vibration.
(For a 2-flute tool, ~803 RPM may excite this mode.)
```

This means: **Operating near 803 RPM with a 2-flute tool is likely to cause chatter.**

---

## Tips & Best Practices

### ✓ Do This

- **Use consistent tap locations** between tests
- **Keep the accelerometer rigidly mounted** throughout testing
- **Perform multiple tests** (at least 3) to verify consistency
- **Document tool geometry** (diameter, material, flutes, holder type)
- **Test different tool holders** if chatter is problematic
- **Compare results** before and after tightening components
- **Archive results** in a project folder for future reference

### ✗ Don't Do This

- ❌ Tap while the spindle is rotating
- ❌ Use an excessively light tap (signal too small)
- ❌ Tap multiple times in quick succession
- ❌ Move or vibrate the machine during capture
- ❌ Remount the accelerometer between related tests
- ❌ Ignore warnings about loose tooling
- ❌ Use results from poorly mounted accelerometers

---

## Common Issues

### Issue: Very High RMS Levels (> 2.0 g)

**Possible causes:**
- Loose tool holder or runout
- Worn spindle bearings
- Eccentric tool
- Incorrect tap force (too hard)

**Solutions:**
1. Check tool holder for looseness
2. Verify spindle runout with dial indicator
3. Inspect for worn bearings
4. Try a softer tap
5. Clean and re-tighten all connections

### Issue: No Clear Peak Frequency

**Possible causes:**
- Tap force too light
- System too heavily damped
- Accelerometer not making good contact
- Loose I2C wiring

**Solutions:**
1. Tap harder (but not too hard!)
2. Check accelerometer mounting
3. Verify I2C connection with `i2cdetect -y 1`
4. Try a different location on the tool holder

### Issue: Different Results Each Time

**Possible causes:**
- Inconsistent tap force or location
- Accelerometer orientation changed
- Loose mounting hardware
- Temperature changes affecting sensor

**Solutions:**
1. Mark the tap location with tape
2. Use consistent tap force (practice helps!)
3. Re-verify accelerometer orientation
4. Tighten all mounting screws
5. Allow system to stabilize between tests

### Issue: Chatter Still Occurs at Recommended RPM

This can happen if:
- **Multiple modes present:** The system may have multiple resonances. Try avoiding several frequency ranges.
- **Mode complexity:** Real machine tools have complex dynamics. The recommended RPM avoids the *primary* mode but may excite secondary modes.
- **Surface finish issues:** May be caused by cutting forces, not spindle speed alone. Adjust depth of cut, feed rate, or tool geometry.
- **Tool wear:** Replace cutting tools regularly.

---

## Advanced: Multiple Tests for a Tool Profile

To build a complete tool profile:

### Test 1: Tool + Holder Combination
Tap the assembled tool in its normal state.

### Test 2: Tool Only
Remove the tool from the holder and tap it alone.

### Test 3: Holder Only
Tap the empty holder.

**Analysis:** Peaks unique to Test 1 indicate machine/spindle modes. Peaks in Test 2 indicate tool-specific issues.

---

## Next Steps

After performing tap tests:

1. **Record your data:** Save CSV files and plots
2. **Compare results:** Check multiple tools and holders
3. **Document findings:** Note which speeds cause chatter
4. **Adjust operations:** Use avoidance chart to select safe spindle speeds
5. **Share results:** Help others by posting your findings!

---

## Reference: Expected Results

### Well-Tuned Rigid Setup
- **Peak frequencies:** 100-300 Hz
- **RMS levels:** < 0.5 g
- **Damping ratios:** ζ > 0.10
- **Primary mode well above typical operating speeds**

### Typical CNC Machine
- **Peak frequencies:** 30-150 Hz
- **RMS levels:** 0.5-1.0 g
- **Damping ratios:** ζ = 0.05-0.15
- **Primary mode requires RPM selection**

### Loose or Worn Setup
- **Peak frequencies:** < 30 Hz
- **RMS levels:** > 1.0 g
- **Damping ratios:** ζ < 0.05
- **Multiple competing modes**
- **Recommendation:** Check for mechanical issues before increasing spindle speed

---

## Questions?

Refer to:
- [Main README](README.md) for theory and features
- [Installation Guide](INSTALLATION.md) for setup help
- [GitHub Issues](https://github.com/rzega02/PiModal-CNC---Raspberry-Pi-CNC-Tap-Tester/issues) for technical support

Happy testing! 🔧
