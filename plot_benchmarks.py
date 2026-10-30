# plot_benchmarks.py
# ─────────────────────────────────────────────────────────────────────────────
# Visualizes FocusLock telemetry from data/logs/gaze_log.csv using Pandas & Matplotlib.
#
# Generates a 3-panel scientific benchmark chart:
#   1. Noise Reduction: Raw X vs Filtered X over time
#   2. Intent & Zones: Calibrated X over time with trigger zones & action markers
#   3. 2D Trajectory: Raw (jittery scatter) vs Filtered (smoothed line)
#
# Output saved to: data/logs/gaze_benchmark.png
# ─────────────────────────────────────────────────────────────────────────────

import os
import pandas as pd
import matplotlib.pyplot as plt
from config import LOG_DIR, LOG_FILE, ZONE_WIDTH_FRAC


def plot_gaze_benchmarks():
    csv_path = os.path.join(LOG_DIR, LOG_FILE)

    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        print(f"[ERROR] No log file found at {csv_path}. Run FocusLock first to generate logs.")
        return

    print(f"[FocusLock Benchmark] Reading telemetry from: {csv_path}")
    df = pd.read_csv(csv_path)

    if len(df) < 10:
        print("[WARNING] Fewer than 10 frames recorded. Run FocusLock longer to collect more data.")
        return

    # Convert numeric columns
    for col in ["raw_x", "raw_y", "filtered_x", "filtered_y", "calibrated_x", "calibrated_y"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop frames where face was not detected
    valid_df = df.dropna(subset=["raw_x", "filtered_x"]).copy()
    if len(valid_df) == 0:
        print("[ERROR] No valid gaze tracking frames found in log.")
        return

    # Normalize timestamp to start from 0.0 seconds
    t0 = valid_df["timestamp"].iloc[0]
    valid_df["rel_time"] = valid_df["timestamp"] - t0

    # ── Create Matplotlib Figure ──────────────────────────────────────────────
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(3, 1, figsize=(11, 10))
    fig.suptitle("FocusLock Telemetry & Signal Benchmark", fontsize=15, fontweight="bold", y=0.98)

    # ── Panel 1: Filter Jitter Reduction ──────────────────────────────────────
    ax1 = axes[0]
    ax1.plot(valid_df["rel_time"], valid_df["raw_x"], color="tomato", alpha=0.55, label="Raw Sensor Gaze X (Noisy)", linewidth=1.2)
    ax1.plot(valid_df["rel_time"], valid_df["filtered_x"], color="forestgreen", label="Moving-Average Filtered X (N=7)", linewidth=2.0)
    ax1.set_title("1. Jitter Reduction: Raw vs Filtered Eye-Socket Ratio", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Normalized X [0..1]")
    ax1.set_ylim(-0.05, 1.05)
    ax1.legend(loc="upper right", frameon=True)

    # ── Panel 2: Calibrated Gaze & Intent Triggers ────────────────────────────
    ax2 = axes[1]
    calib_valid = valid_df.dropna(subset=["calibrated_x"])
    if len(calib_valid) > 0:
        ax2.plot(calib_valid["rel_time"], calib_valid["calibrated_x"], color="royalblue", label="Calibrated Screen X", linewidth=1.8)

        # Highlight trigger zones
        ax2.axhspan(0.0, ZONE_WIDTH_FRAC, color="orange", alpha=0.18, label=f"Left Zone: PREV (0-{int(ZONE_WIDTH_FRAC*100)}%)")
        ax2.axhspan(1.0 - ZONE_WIDTH_FRAC, 1.0, color="deepskyblue", alpha=0.18, label=f"Right Zone: NEXT ({int((1-ZONE_WIDTH_FRAC)*100)}-100%)")

        # Mark trigger action events
        actions = valid_df[valid_df["action"].notna() & (valid_df["action"] != "")]
        for _, row in actions.iterrows():
            act_color = "darkgreen" if row["action"] == "NEXT_SLIDE" else "purple"
            ax2.axvline(x=row["rel_time"], color=act_color, linestyle="--", linewidth=1.8, alpha=0.85)
            ax2.text(row["rel_time"], 0.5, f" {row['action']}", rotation=90, color=act_color, fontweight="bold", fontsize=9)

    ax2.set_title("2. Calibrated Screen Coordinate & Action Triggers", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Screen X [0..1]")
    ax2.set_ylim(-0.05, 1.05)
    ax2.legend(loc="upper right", frameon=True)

    # ── Panel 3: 2D Spatial Trajectory ────────────────────────────────────────
    ax3 = axes[2]
    ax3.scatter(valid_df["raw_x"], valid_df["raw_y"], color="tomato", alpha=0.25, s=15, label="Raw Gaze Samples (Spatial Scatter)")
    ax3.plot(valid_df["filtered_x"], valid_df["filtered_y"], color="forestgreen", linewidth=1.6, label="Filtered Trajectory Path")
    ax3.set_title("3. 2D Spatial Gaze Trajectory (X vs Y)", fontsize=11, fontweight="bold")
    ax3.set_xlabel("Elapsed Time (seconds) [Panels 1 & 2] / Normalized X [Panel 3]")
    ax3.set_ylabel("Normalized Y [0..1]")
    ax3.invert_yaxis()  # Invert so (0,0) is top-left like screen coordinates
    ax3.legend(loc="upper right", frameon=True)

    plt.tight_layout()

    out_file = os.path.join(LOG_DIR, "gaze_benchmark.png")
    fig.savefig(out_file, dpi=200)
    plt.close()
    print(f"[FocusLock Benchmark] Successfully saved benchmark graph: {out_file}")


if __name__ == "__main__":
    plot_gaze_benchmarks()
