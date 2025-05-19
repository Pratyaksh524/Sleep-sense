import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button

plt.ion()  # Interactive mode on
fig, axs = plt.subplots(6, 1, figsize=(10, 12))
plt.subplots_adjust(bottom=0.15)  # Make space for buttons

# Initialize data containers
time_data, spo2_data, pulse_data, body_pos_data = [], [], [], []
pleth_data, flow_data, snore_data = [], [], []

file_path = r"C:\Users\DELL\Documents\Workday1\sleepsense\DATA1623.TXT"

# Body Position mapping to arrow directions
def bodypos_to_arrow_dir(pos):
    if pos == 10:
        return (0, 1)   # Up
    elif pos == 20:
        return (0, -1)  # Down
    elif pos == 30:
        return (-1, 0)  # Left
    elif pos == 40:
        return (1, 0)   # Right
    else:
        return (0, 0)

highlight_times = [10, 20, 30, 40, 50]  # in whatever units original data is

# Set column names once
columns = [
    "Time", "Pleth", "SpO2", "Pulse", "Flow",
    "BodyPos", "Snore", "C4", "C5", "C6"
]

time_unit = "minutes"  # default mode

def convert_time(t):
    # Convert time from raw data units (assumed ms) to desired unit
    if time_unit == "minutes":
        return t / 60000  # ms to minutes
    else:
        return t / 1000   # ms to seconds

def update_plots():
    x = [convert_time(t) for t in time_data]

    # Determine x-axis limits for zooming
    if time_unit == "seconds":
        if len(x) > 0:
            max_x = x[-1]
            min_x = max(0, max_x - 60)  # last 60 seconds window
        else:
            min_x, max_x = 0, 60
    else:
        if len(x) > 0:
            min_x, max_x = min(x), max(x)
        else:
            min_x, max_x = 0, 1

    # Plot all except body pos
    plot_data = [
        (axs[0], spo2_data, 'blue', 'o', "SpO2 (%)", "SpO2 over Time"),
        (axs[1], pulse_data, 'red', 's', "Pulse (BPM)", "Pulse over Time"),
        (axs[2], pleth_data, 'purple', '', "Pleth", "Pleth Waveform"),
        (axs[3], flow_data, 'orange', '', "Flow", "Flow Waveform"),
        (axs[4], snore_data, 'brown', '', "Snore", "Snoring Waveform"),
    ]

    for ax, y_data, color, marker, y_label, title in plot_data:
        ax.cla()
        if marker:
            ax.plot(x, y_data, color=color, marker=marker)
        else:
            ax.plot(x, y_data, color=color)
        ax.set_xlim(min_x, max_x)
        ax.set_title(title)
        ax.set_ylabel(y_label)
        ax.set_xlabel(f"Time ({time_unit})")
        ax.grid(True)

        # Highlight vertical lines
        highlight_x = [convert_time(t) for t in highlight_times]
        for hx in highlight_x:
            ax.axvline(x=hx, color='gray', linestyle='--', alpha=0.5)

    # Body position plot with arrows, use index as x-axis
    axs[5].cla()
    body_x = np.arange(len(body_pos_data))
    y = np.array(body_pos_data)
    U, V = zip(*[bodypos_to_arrow_dir(pos) for pos in body_pos_data])
    axs[5].quiver(body_x, y, U, V, angles='xy', scale_units='xy', scale=1.5, color='green')
    axs[5].set_ylim(5, 45)
    axs[5].set_title("Body Position over Time (Arrows)")
    axs[5].set_xlabel("Index")
    axs[5].set_ylabel("BodyPos")
    axs[5].grid(True)

    # Highlight lines on body pos plot by index
    for t in highlight_times:
        if t in time_data:
            idx = time_data.index(t)
            axs[5].axvline(x=idx, color='gray', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.draw()
    plt.pause(0.1)

def toggle_time_unit(event):
    global time_unit
    time_unit = "seconds" if time_unit == "minutes" else "minutes"
    update_plots()
    btn.label.set_text(f"View in {time_unit}")
    plt.draw()

# Create toggle button
ax_button = plt.axes([0.4, 0.05, 0.2, 0.05])
btn = Button(ax_button, f"View in {time_unit}")
btn.on_clicked(toggle_time_unit)

try:
    for chunk in pd.read_csv(file_path, header=None, names=columns, chunksize=1):
        row = chunk.iloc[0]
        try:
            time_val = int(row["Time"])
            spo2_val = float(row["SpO2"])
            pulse_val = float(row["Pulse"])
            bodypos_val = int(row["BodyPos"])
            pleth_val = float(row["Pleth"])
            flow_val = float(row["Flow"])
            snore_val = float(row["Snore"])
        except (ValueError, TypeError):
            continue

        # Filter values based on expected ranges
        if not (85 <= spo2_val <= 100):
            continue
        if not (49 <= pulse_val <= 170):
            continue
        if not (5 <= bodypos_val <= 45):
            continue
        if pleth_val < 0 or pleth_val > 1000:
            continue
        if flow_val < -100 or flow_val > 100:
            continue
        if snore_val < 0 or snore_val > 1000:
            continue
        if time_val < 0:
            continue

        time_data.append(time_val)
        spo2_data.append(spo2_val)
        pulse_data.append(pulse_val)
        body_pos_data.append(bodypos_val)
        pleth_data.append(pleth_val)
        flow_data.append(flow_val)
        snore_data.append(snore_val)

        update_plots()

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    plt.ioff()
    plt.show()
