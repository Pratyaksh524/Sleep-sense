import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button

file_path = r"C:\Users\DELL\Documents\Workday1\sleepsense\DATA2304.TXT"
data = pd.read_csv(file_path, header=None)

time = data[0].astype(float) / 1000
body_pos = data[1].astype(int)
pulse = data[2].astype(float)
spo2 = data[3].astype(float)
flow = data[7].astype(float)

def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

body_pos_n = normalize(body_pos)
pulse_n = normalize(pulse)
spo2_n = normalize(spo2)
flow_n = normalize(flow)

arrow_directions = {
    0: (0, 0.5, 'up', 'Up (Supine)'),
    1: (-0.5, 0, 'left', 'Left'),
    2: (0.5, 0, 'right', 'Right'),
    3: (0, -0.5, 'down', 'Down (Prone)')
}

fig, ax = plt.subplots(figsize=(14, 8))
plt.subplots_adjust(bottom=0.15, top=0.85)

offsets = [0, 1.2, 2.4, 3.6]

ax.plot(time, body_pos_n + offsets[0], color='black', label='Body Position')
ax.plot(time, pulse_n + offsets[1], color='red', label='Pulse')
ax.plot(time, spo2_n + offsets[2], color='green', label='SpO2')
ax.plot(time, flow_n + offsets[3], color='black', label='Airflow')

yticks_pos = [np.mean(sig) + offset for sig, offset in zip(
    [body_pos_n, pulse_n, spo2_n, flow_n], offsets)]
yticks_labels = ['Body Position', 'Pulse (BPM)', 'SpO2 (%)', 'Airflow']

ax.set_yticks(yticks_pos)
ax.set_yticklabels(yticks_labels, fontsize=12)
ax.set_ylim(-0.5, max(offsets) + 1)
ax.set_xlabel('Time (s)')
ax.set_title('Sleepsense Plotting with Body Position Arrows')

arrow_y = offsets[0] + 0.5
interval = 5
sampling_step = int(1 / (time[1] - time[0]) * interval)
arrow_indices = time[::sampling_step]

for t in arrow_indices:
    idx = (np.abs(time - t)).argmin()
    pos = body_pos.iloc[idx]
    dx, dy, arrow_char, label = arrow_directions.get(pos, (0, 0, '?', 'Unknown'))
    ax.annotate(
        arrow_char,
        xy=(time.iloc[idx], arrow_y),
        xytext=(time.iloc[idx] + dx, arrow_y + dy),
        fontsize=16,
        color='blue',
        ha='center',
        va='center',
        arrowprops=dict(arrowstyle='->', color='green')
    )

window_size = 10
start_time = time.iloc[0]
end_time = time.iloc[-1]
ax.set_xlim(start_time, start_time + window_size)

slider_ax = plt.axes([0.15, 0.07, 0.7, 0.03])
slider = Slider(slider_ax, 'Time', start_time, end_time - window_size, valinit=start_time)

def update(val):
    t = slider.val
    ax.set_xlim(t, t + window_size)
    fig.canvas.draw_idle()

slider.on_changed(update)

window_sizes = [5, 10, 15, 30, 60, 120, 300]
button_width = 0.08
button_height = 0.04
button_spacing = 0.01
start_x = 0.1
button_y = 0.92
buttons = []

def on_button_clicked(event, size):
    global window_size
    window_size = size
    slider.valmax = end_time - window_size
    slider.ax.set_xlim(slider.valmin, slider.valmax)
    if slider.val > slider.valmax:
        slider.set_val(slider.valmax)
    else:
        update(slider.val)

for i, size in enumerate(window_sizes):
    ax_button = plt.axes([start_x + i*(button_width + button_spacing), button_y, button_width, button_height])
    label = f"{size//60}m" if size >= 60 else f"{size}s"
    button = Button(ax_button, label)
    button.on_clicked(lambda event, s=size: on_button_clicked(event, s))
    buttons.append(button)

plt.show()
