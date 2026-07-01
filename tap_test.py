from mpu6050 import mpu6050
import time
import csv
import os
import subprocess
from datetime import datetime

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for plots
import matplotlib.pyplot as plt

# Initialize sensor (MPU-6050 at I2C address 0x68)
sensor = mpu6050(0x68)

AXIS_NAMES = ['X', 'Y', 'Z']


def estimate_fs(time_s):
    """
    More robust than using total duration / (N-1), because Pi timestamp spacing can jitter.
    """
    dt = np.diff(time_s)
    dt = dt[dt > 0]
    if len(dt) == 0:
        return 0.0
    return 1.0 / np.median(dt)


def single_sided_fft(x, fs):
    """
    Return frequency vector and single-sided magnitude spectrum.
    """
    N = len(x)
    if N < 2 or fs <= 0:
        return np.array([0.0]), np.array([0.0])

    window = np.hanning(N)
    xw = (x - np.mean(x)) * window

    X = np.fft.rfft(xw)
    freqs = np.fft.rfftfreq(N, d=1.0/fs)

    # Window amplitude correction for a practical spectrum
    mag = (2.0 / np.sum(window)) * np.abs(X)
    return freqs, mag


def fft_bandpass(signal_g, fs, f_center, bandwidth_hz):
    """
    Simple FFT-domain bandpass filter using numpy only.
    """
    N = len(signal_g)
    if N < 2 or fs <= 0:
        return signal_g.copy()

    x = signal_g - np.mean(signal_g)
    X = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(N, d=1.0/fs)

    f_lo = max(0.0, f_center - bandwidth_hz / 2.0)
    f_hi = f_center + bandwidth_hz / 2.0
    mask = (freqs >= f_lo) & (freqs <= f_hi)

    Xf = np.zeros_like(X)
    Xf[mask] = X[mask]
    xf = np.fft.irfft(Xf, n=N)
    return xf


def find_positive_peaks(x, min_separation_samples=1, threshold_ratio=0.10):
    """
    Simple local-maximum finder using numpy only.
    """
    x = np.asarray(x)
    if len(x) < 3:
        return np.array([], dtype=int)

    candidates = np.where((x[1:-1] > x[:-2]) & (x[1:-1] >= x[2:]) & (x[1:-1] > 0))[0] + 1
    if len(candidates) == 0:
        return np.array([], dtype=int)

    thresh = threshold_ratio * np.max(x[candidates])
    candidates = candidates[x[candidates] >= thresh]
    if len(candidates) == 0:
        return np.array([], dtype=int)

    selected = [candidates[0]]
    for idx in candidates[1:]:
        if idx - selected[-1] >= min_separation_samples:
            selected.append(idx)

    return np.array(selected, dtype=int)


def estimate_damping_logdec(time_s, signal_g, fn_hz, cycles_to_use=6, band_fraction=0.30):
    """
    Estimate damping ratio zeta from ring-down using logarithmic decrement.
    """
    fs = estimate_fs(time_s)
    if fs <= 0 or fn_hz <= 0:
        return None

    bw = max(4.0, band_fraction * fn_hz)
    xf = fft_bandpass(signal_g, fs, fn_hz, bw)

    start_idx = int(np.argmax(np.abs(xf)))

    samples_per_period = max(1, int(fs / max(fn_hz, 1e-6)))
    min_sep = max(1, int(0.7 * samples_per_period))
    peak_idx = find_positive_peaks(xf, min_separation_samples=min_sep, threshold_ratio=0.10)

    peak_idx = peak_idx[peak_idx > start_idx]
    if len(peak_idx) < 3:
        return None

    peak_vals = xf[peak_idx]
    peak_times = time_s[peak_idx]

    usable = min(cycles_to_use + 1, len(peak_vals))
    peak_vals = peak_vals[:usable]
    peak_times = peak_times[:usable]

    if len(peak_vals) < 3:
        return None

    if np.any(peak_vals[:-1] <= 0) or np.any(peak_vals[1:] <= 0):
        return None

    deltas = np.log(peak_vals[:-1] / peak_vals[1:])
    deltas = deltas[np.isfinite(deltas) & (deltas > 0)]
    if len(deltas) == 0:
        return None

    delta = np.mean(deltas)
    zeta = delta / np.sqrt((2 * np.pi)**2 + delta**2)

    Td = np.mean(np.diff(peak_times))
    fd = 1.0 / Td if Td > 0 else fn_hz

    return {
        "method": "logdec",
        "zeta": float(zeta),
        "delta": float(delta),
        "fd_hz": float(fd),
        "filtered_signal": xf,
        "peak_indices": peak_idx[:usable],
        "peak_values": peak_vals,
        "peak_times": peak_times
    }


def estimate_damping_half_power(freqs, mag, fn_hz):
    """
    Estimate damping ratio from half-power bandwidth around fn_hz.
    """
    freqs = np.asarray(freqs)
    mag = np.asarray(mag)

    if len(freqs) < 3 or len(mag) < 3 or fn_hz <= 0:
        return None

    i0 = int(np.argmin(np.abs(freqs - fn_hz)))
    peak = mag[i0]
    if peak <= 0:
        return None

    hp = peak / np.sqrt(2.0)

    i1 = i0
    while i1 > 0 and mag[i1] > hp:
        i1 -= 1
    if i1 == 0:
        return None

    i2 = i0
    while i2 < len(mag) - 1 and mag[i2] > hp:
        i2 += 1
    if i2 == len(mag) - 1:
        return None

    f1 = np.interp(hp, [mag[i1], mag[i1 + 1]], [freqs[i1], freqs[i1 + 1]])
    f2 = np.interp(hp, [mag[i2 - 1], mag[i2]], [freqs[i2 - 1], freqs[i2]])

    if f2 <= f1:
        return None

    zeta = (f2 - f1) / (2.0 * fn_hz)

    return {
        "method": "half_power",
        "zeta": float(zeta),
        "f1_hz": float(f1),
        "f2_hz": float(f2),
        "bandwidth_hz": float(f2 - f1)
    }


def choose_primary_axis(axis_results):
    """
    Choose the chatter-driving axis:
    - keep axes with peak mag >= 60% of strongest peak mag
    - from those, choose lowest dominant frequency
    - fallback to highest RMS
    """
    if not axis_results:
        return 0

    peak_mags = np.array([r["peak_mag"] for r in axis_results], dtype=float)
    rms_vals = np.array([r["rms_g"] for r in axis_results], dtype=float)

    max_peak = np.max(peak_mags) if len(peak_mags) else 0.0
    if max_peak > 0:
        candidates = [i for i, r in enumerate(axis_results)
                      if r["peak_mag"] >= 0.60 * max_peak and r["dom_freq"] > 0]
        if candidates:
            best = min(candidates, key=lambda i: axis_results[i]["dom_freq"])
            return best

    return int(np.argmax(rms_vals))


def plot_rpm_avoidance_chart(fn_hz, z_flutes, zeta=None, max_rpm=12000, lobes=6,
                             filename="rpm_avoidance_chart.png"):
    """
    Practical RPM avoidance / resonance chart.
    This is NOT a full depth-of-cut stability lobe diagram.
    """
    rpm = np.linspace(1, max_rpm, 3000)
    f_tp = rpm * z_flutes / 60.0

    plt.figure(figsize=(10, 5))
    plt.plot(rpm, f_tp, label="Tooth-passing frequency")
    plt.axhline(fn_hz, color="red", linestyle="-", linewidth=1.5, label=f"Mode ~{fn_hz:.1f} Hz")

    for k in range(lobes):
        rpm_k = 60.0 * fn_hz / (z_flutes * (k + 1))
        if rpm_k <= max_rpm:
            plt.axvline(rpm_k, linestyle="--", alpha=0.7, color="darkorange")
            plt.text(rpm_k, fn_hz * 1.02, f"{rpm_k:.0f} RPM", rotation=90,
                     va='bottom', ha='center', fontsize=8)

            if zeta is not None and zeta > 0:
                band_frac = max(0.01, min(0.08, 2.0 * zeta))
                low = rpm_k * (1.0 - band_frac)
                high = rpm_k * (1.0 + band_frac)
                plt.axvspan(low, high, alpha=0.12, color='red')

    plt.xlabel("Spindle speed (RPM)")
    plt.ylabel("Tooth-passing frequency (Hz)")
    plt.title("Avoid-These-Speeds Chart")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()


print("=== CNC Tap Test Program ===")
print("Press Enter to capture data, or type Q then Enter to quit.")

last_file = None

while True:
    user_input = input("Start new measurement (Enter) or quit (Q): ").strip()
    if user_input.lower() == 'q':
        break

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"tap_{timestamp}.csv"

    capture_duration = 8.0
    print(f"Capturing {capture_duration} s of data... (saving to {csv_filename})")

    with open(csv_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["time_s", "accel_x_g", "accel_y_g", "accel_z_g"])
        start_time = time.time()

        while time.time() - start_time < capture_duration:
            accel = sensor.get_accel_data()
            t = time.time() - start_time
            writer.writerow([
                f"{t:.4f}",
                f"{accel['x']:.4f}",
                f"{accel['y']:.4f}",
                f"{accel['z']:.4f}"
            ])

    print("Data capture complete.")
    last_file = csv_filename

    ans = input("Analyze the last run? (Y/N): ").strip()
    if ans.lower() != 'y':
        print(f"Raw data saved to {csv_filename}. Skipping analysis.")
        continue

    print("Performing FFT and damping analysis...")

    try:
        data = np.loadtxt(last_file, delimiter=',', skiprows=1)
    except Exception as e:
        print(f"Error reading {last_file}: {e}")
        continue

    if data.size == 0 or data.ndim < 2:
        print("No data or insufficient data for analysis.")
        continue

    time_vals = data[:, 0]
    axes_data = data[:, 1:]

    N = len(time_vals)
    if N < 2:
        print("Not enough data points for analysis.")
        continue

    duration = time_vals[-1] - time_vals[0]
    fs = estimate_fs(time_vals)
    dt = 1.0 / fs if fs > 0 else 0

    # Remove DC bias first
    axes_data = axes_data - np.mean(axes_data, axis=0)

    axis_results = []

    fig, axs = plt.subplots(axes_data.shape[1], 1, figsize=(7, 4 * axes_data.shape[1]))
    if axes_data.shape[1] == 1:
        axs = [axs]

    for i in range(axes_data.shape[1]):
        axis_name = AXIS_NAMES[i]
        sig = axes_data[:, i]

        rms_g = float(np.sqrt(np.mean(sig ** 2)))

        freqs, mag = single_sided_fft(sig, fs)

        peak_idx = np.argmax(mag[1:]) + 1 if len(mag) > 1 else 0
        dom_freq = float(freqs[peak_idx]) if len(freqs) > peak_idx else 0.0
        peak_mag = float(mag[peak_idx]) if len(mag) > peak_idx else 0.0

        logdec = estimate_damping_logdec(time_vals, sig, dom_freq, cycles_to_use=6, band_fraction=0.30)
        halfpower = estimate_damping_half_power(freqs, mag, dom_freq)

        if logdec is not None:
            zeta = logdec["zeta"]
            damping_method = "logdec"
        elif halfpower is not None:
            zeta = halfpower["zeta"]
            damping_method = "half-power"
        else:
            zeta = None
            damping_method = "unavailable"

        axis_results.append({
            "axis": axis_name,
            "dom_freq": dom_freq,
            "peak_mag": peak_mag,
            "rms_g": rms_g,
            "zeta": zeta,
            "damping_method": damping_method,
            "logdec": logdec,
            "halfpower": halfpower,
            "freqs": freqs,
            "mag": mag
        })

        axs[i].plot(freqs, mag, linewidth=1.0)
        axs[i].set_title(f"Axis {axis_name} Spectrum")
        axs[i].set_xlabel("Frequency (Hz)")
        axs[i].set_ylabel("Magnitude")
        axs[i].grid(True, alpha=0.3)
        axs[i].axvline(dom_freq, color='r', linestyle='--', label=f"Peak ~{dom_freq:.1f} Hz")

        legend_text = f"Peak ~{dom_freq:.1f} Hz | RMS {rms_g:.3f} g"
        if zeta is not None:
            legend_text += f" | zeta {zeta:.4f} ({damping_method})"
        axs[i].legend([legend_text])

    fig.tight_layout()
    plot_filename = f"tap_{timestamp}.png"
    fig.savefig(plot_filename)
    plt.close(fig)

    primary_axis_index = choose_primary_axis(axis_results)
    primary = axis_results[primary_axis_index]
    primary_axis = primary["axis"]
    primary_freq = primary["dom_freq"]
    primary_zeta = primary["zeta"]

    try:
        flute_str = input("Enter number of flutes on tool (default 4): ").strip()
        flutes = int(flute_str) if flute_str else 4
    except ValueError:
        flutes = 4

    avoid_plot_filename = f"tap_{timestamp}_avoid_chart.png"
    if primary_freq > 0 and flutes > 0:
        crit_rpm = primary_freq * 60.0 / flutes
        plot_rpm_avoidance_chart(
            fn_hz=primary_freq,
            z_flutes=flutes,
            zeta=primary_zeta,
            max_rpm=12000,
            lobes=6,
            filename=avoid_plot_filename
        )
    else:
        crit_rpm = 0.0
        avoid_plot_filename = None

    if os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'):
        try:
            subprocess.Popen(["xdg-open", plot_filename])
            print(f"Opening {plot_filename} in the default image viewer...")
        except Exception as e:
            print(f"Could not auto-open spectrum image: {e}")

        if avoid_plot_filename:
            try:
                subprocess.Popen(["xdg-open", avoid_plot_filename])
                print(f"Opening {avoid_plot_filename} in the default image viewer...")
            except Exception as e:
                print(f"Could not auto-open avoidance chart: {e}")
    else:
        print(f"No GUI display detected. Spectrum plot saved to {plot_filename}.")
        if avoid_plot_filename:
            print(f"Avoidance chart saved to {avoid_plot_filename}.")
        print("You can view these files later on a device with a graphical interface.")

    summary_lines = []
    summary_lines.append(f"File: {last_file} (Duration ~{duration:.3f} s, Fs ~{fs:.1f} Hz)")

    for r in axis_results:
        if r["zeta"] is not None:
            summary_lines.append(
                f"Axis {r['axis']}: Peak ~{r['dom_freq']:.1f} Hz "
                f"(RMS {r['rms_g']:.3f} g, damping zeta {r['zeta']:.4f}, method {r['damping_method']})"
            )
            if r["halfpower"] is not None:
                hp = r["halfpower"]
                summary_lines.append(
                    f"  Half-power check: f1 ~{hp['f1_hz']:.1f} Hz, f2 ~{hp['f2_hz']:.1f} Hz, "
                    f"bandwidth ~{hp['bandwidth_hz']:.1f} Hz"
                )
        else:
            summary_lines.append(
                f"Axis {r['axis']}: Peak ~{r['dom_freq']:.1f} Hz "
                f"(RMS {r['rms_g']:.3f} g, damping unavailable)"
            )

    summary_lines.append(
        f"Primary chatter axis selected: Axis {primary_axis} "
        f"(lowest significant flexible mode at ~{primary_freq:.1f} Hz)"
    )

    if primary_freq > 0 and flutes > 0:
        summary_lines.append(f"Recommendation: Avoid speeds causing ~{primary_freq:.0f} Hz vibration.")
        summary_lines.append(f"(For a {flutes}-flute tool, ~{crit_rpm:.0f} RPM may excite this mode.)")
        if primary_zeta is not None:
            summary_lines.append(f"Estimated damping ratio on primary axis: zeta ~{primary_zeta:.4f}")
        if avoid_plot_filename:
            summary_lines.append(f"Avoid-these-speeds chart saved to: {avoid_plot_filename}")
    else:
        summary_lines.append("Recommendation: N/A (no dominant frequency detected).")

    summary_text = "\n".join(summary_lines)

    print("\n--- Analysis Summary ---")
    print(summary_text)

    txt_filename = f"tap_{timestamp}.txt"
    with open(txt_filename, "w") as f:
        f.write(summary_text + "\n")

    if avoid_plot_filename:
        print(f"(Results saved: {txt_filename}, spectrum: {plot_filename}, avoidance chart: {avoid_plot_filename})")
    else:
        print(f"(Results saved: {txt_filename}, spectrum: {plot_filename})")