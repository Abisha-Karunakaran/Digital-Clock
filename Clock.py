"""
Advanced Digital Clock
-----------------------
A Tkinter desktop app with:
    - Live digital clock (time + date)
    - Dark/Light theme toggle
    - Alarm (checks every second against entered HH:MM)
    - Stopwatch (start/reset)
    - World clock (pick a timezone from a dropdown)
    - Voice announcement of current time (text-to-speech)
    - Simple calendar display (today's date)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from time import strftime
import datetime
import math
import threading
import pytz
import pyttsx3

try:
    import winsound          # built-in on Windows only
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


# ================= VOICE ENGINE =================

# Text-to-speech engine used for the "Speak Current Time" button and alarm alert
engine = pyttsx3.init()


# ================= COLOR THEMES =================

THEMES = {
    "dark": {
        "bg": "#1c121a",      # deep plum-black background
        "card": "#2f1e2c",    # slightly lighter plum card
        "text": "#f2f2f2",
        "accent": "#a87ea0",  # lightened #5e3c58 so it's visible on dark bg
        "muted": "#9c8a98",
    },
    "light": {
        "bg": "#efeced",      # soft plum-tinted white
        "card": "#ffffff",
        "text": "#2a1b27",
        "accent": "#5e3c58",  # requested brand color
        "muted": "#7c6078",
    },
}

# Common timezones for the World Clock dropdown (Sri Lanka listed first / default)
TIMEZONES = [
    "Asia/Colombo (Sri Lanka)",
    "Asia/Kolkata",
    "Asia/Tokyo",
    "Asia/Dubai",
    "Asia/Singapore",
    "Europe/London",
    "Europe/Paris",
    "America/New_York",
    "America/Los_Angeles",
    "Australia/Sydney",
    "UTC",
]

dark_mode = True  # tracks current theme


# ================= MAIN WINDOW =================

root = tk.Tk()
root.title("Advanced Digital Clock")
root.geometry("560x1180")
root.minsize(480, 900)
root.resizable(True, True)

FONT_FAMILY = "Segoe UI"


# ================= CLOCK =================

def update_clock():
    """Refresh the time and date labels every second."""
    time_label.config(text=strftime("%I:%M:%S %p"))
    date_label.config(text=strftime("%A, %d %B %Y"))
    root.after(1000, update_clock)


# ---- Analog clock face ----

ANALOG_RADIUS = 80
ANALOG_CENTER = (ANALOG_RADIUS + 10, ANALOG_RADIUS + 10)


def draw_analog_clock():
    """Redraw the round analog clock face with moving hour/minute/second hands."""
    canvas.delete("all")
    cx, cy = ANALOG_CENTER
    theme = THEMES["dark"] if dark_mode else THEMES["light"]

    # Outer circle (clock face)
    canvas.create_oval(
        cx - ANALOG_RADIUS, cy - ANALOG_RADIUS,
        cx + ANALOG_RADIUS, cy + ANALOG_RADIUS,
        outline=theme["accent"], width=3, fill=theme["card"]
    )

    # Hour tick marks (12 of them, every 30 degrees)
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        x1 = cx + (ANALOG_RADIUS - 8) * math.cos(angle)
        y1 = cy + (ANALOG_RADIUS - 8) * math.sin(angle)
        x2 = cx + (ANALOG_RADIUS - 1) * math.cos(angle)
        y2 = cy + (ANALOG_RADIUS - 1) * math.sin(angle)
        canvas.create_line(x1, y1, x2, y2, fill=theme["muted"], width=2)

    now = datetime.datetime.now()
    hours = now.hour % 12
    minutes = now.minute
    seconds = now.second

    # Hand angles: each unit advances the hand by a fixed number of degrees,
    # offset by -90 so 12 o'clock points straight up.
    sec_angle = math.radians(seconds * 6 - 90)
    min_angle = math.radians(minutes * 6 + seconds * 0.1 - 90)
    hour_angle = math.radians(hours * 30 + minutes * 0.5 - 90)

    # Hour hand (short + thick)
    canvas.create_line(
        cx, cy,
        cx + (ANALOG_RADIUS * 0.5) * math.cos(hour_angle),
        cy + (ANALOG_RADIUS * 0.5) * math.sin(hour_angle),
        fill=theme["text"], width=5, capstyle=tk.ROUND
    )

    # Minute hand (longer + medium)
    canvas.create_line(
        cx, cy,
        cx + (ANALOG_RADIUS * 0.75) * math.cos(min_angle),
        cy + (ANALOG_RADIUS * 0.75) * math.sin(min_angle),
        fill=theme["text"], width=3, capstyle=tk.ROUND
    )

    # Second hand (longest + thin, accent color)
    canvas.create_line(
        cx, cy,
        cx + (ANALOG_RADIUS * 0.85) * math.cos(sec_angle),
        cy + (ANALOG_RADIUS * 0.85) * math.sin(sec_angle),
        fill=theme["accent"], width=2, capstyle=tk.ROUND
    )

    # Center pin
    canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill=theme["accent"], outline="")

    root.after(1000, draw_analog_clock)


# ================= THEME =================

def apply_theme():
    """Repaint every widget using the colors for the current theme."""
    theme = THEMES["dark"] if dark_mode else THEMES["light"]

    root.configure(bg=theme["bg"])
    container.configure(bg=theme["bg"])

    for card in cards:
        card.configure(bg=theme["card"])

    canvas.configure(bg=theme["card"])

    time_label.configure(bg=theme["card"], fg=theme["accent"])
    date_label.configure(bg=theme["card"], fg=theme["muted"])
    stopwatch_label.configure(bg=theme["card"], fg=theme["text"])
    world_label.configure(bg=theme["card"], fg=theme["accent"])
    calendar_label.configure(bg=theme["card"], fg=theme["text"])

    for widget in section_titles:
        widget.configure(bg=theme["card"], fg=theme["muted"])

    for widget in hint_labels:
        widget.configure(bg=theme["card"], fg=theme["muted"])

    style.configure("TButton", background=theme["accent"], foreground="#ffffff")
    style.configure("TEntry", fieldbackground=theme["bg"])
    style.configure("TCombobox", fieldbackground=theme["bg"])

    theme_button.config(text="☀️  Light Mode" if dark_mode else "🌙  Dark Mode")


def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()


# ================= ALARM =================

def ring_alarm_tone():
    """
    Play an actual audible alarm tone (not just a popup).
    Runs in a background thread so the GUI doesn't freeze while beeping.
    """
    def _ring():
        if HAS_WINSOUND:
            for _ in range(6):
                winsound.Beep(1000, 350)   # 1000Hz tone for 350ms
        else:
            # Non-Windows fallback: no winsound, so speak the alert instead
            engine.say("Alarm! Alarm! Alarm!")
            engine.runAndWait()

    threading.Thread(target=_ring, daemon=True).start()


last_alarm_trigger = None  # remembers the HH:MM the alarm last fired for


def check_alarm():
    """
    Compare the alarm time entered by the user (HH:MM, 24-hour format)
    with the current system time. If they match, play a ringing tone,
    speak an alert out loud, and show a popup. Only fires once per minute.
    """
    global last_alarm_trigger

    alarm_time = alarm_entry.get()
    current_time = strftime("%H:%M")

    if alarm_time and alarm_time == current_time and last_alarm_trigger != current_time:
        last_alarm_trigger = current_time
        ring_alarm_tone()
        engine.say("Your alarm is ringing")
        engine.runAndWait()
        messagebox.showinfo("Alarm", "⏰ Alarm Ringing!")

    root.after(1000, check_alarm)


# ================= STOPWATCH =================

stopwatch_seconds = 0
running = True


def stopwatch():
    """Increment the stopwatch counter every second and update the label."""
    global stopwatch_seconds

    if running:
        stopwatch_seconds += 1
        hours = stopwatch_seconds // 3600
        minutes = (stopwatch_seconds % 3600) // 60
        seconds = stopwatch_seconds % 60
        stopwatch_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")

    stopwatch_label.after(1000, stopwatch)


def reset_stopwatch():
    """Reset the stopwatch back to 00:00:00."""
    global stopwatch_seconds
    stopwatch_seconds = 0
    stopwatch_label.config(text="00:00:00")


# ================= WORLD CLOCK =================

def show_world_time():
    """Look up the current time in the timezone picked from the dropdown."""
    try:
        # The dropdown shows a friendly label, e.g. "Asia/Colombo (Sri Lanka)"
        # — only the part before the space is a real pytz timezone name.
        timezone = timezone_combo.get().split(" ")[0]
        location_time = datetime.datetime.now(pytz.timezone(timezone))
        world_label.config(text=location_time.strftime("%H:%M:%S"))
    except Exception:
        world_label.config(text="Invalid Timezone")


# ================= VOICE TIME =================

def speak_time():
    """Read the current time out loud using text-to-speech."""
    current_time = strftime("The current time is %I %M %p")
    engine.say(current_time)
    engine.runAndWait()


# ================= CALENDAR =================

def show_calendar():
    """Display today's full date and day name."""
    today = datetime.date.today()
    calendar_label.config(text=today.strftime("%d %B %Y  •  %A"))


# ================= GUI LAYOUT =================

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=(FONT_FAMILY, 11, "bold"), padding=8, borderwidth=0)
style.configure("TEntry", font=(FONT_FAMILY, 11), padding=6)
style.configure("TCombobox", font=(FONT_FAMILY, 11), padding=6)

container = tk.Frame(root)
container.pack(fill="both", expand=True, padx=20, pady=20)

cards = []           # all "card" frames, so the theme function can recolor them
section_titles = []  # small section heading labels
hint_labels = []      # small grey hint labels


def make_card(parent, pad_y=(0, 16)):
    """Create a card-style section with consistent spacing."""
    card = tk.Frame(parent, padx=18, pady=16, highlightthickness=0)
    card.pack(fill="x", pady=pad_y)
    cards.append(card)
    return card


def make_section_title(card, text):
    label = tk.Label(card, text=text, font=(FONT_FAMILY, 10, "bold"), anchor="w")
    label.pack(fill="x")
    section_titles.append(label)
    return label


def make_hint(card, text):
    label = tk.Label(card, text=text, font=(FONT_FAMILY, 9), anchor="w")
    label.pack(fill="x", pady=(2, 6))
    hint_labels.append(label)
    return label


# --- Clock card ---
clock_card = make_card(container)
canvas = tk.Canvas(
    clock_card,
    width=(ANALOG_RADIUS + 10) * 2,
    height=(ANALOG_RADIUS + 10) * 2,
    highlightthickness=0,
)
canvas.pack(pady=(4, 10))
time_label = tk.Label(clock_card, font=(FONT_FAMILY, 40, "bold"))
time_label.pack(pady=(4, 0))
date_label = tk.Label(clock_card, font=(FONT_FAMILY, 13))
date_label.pack(pady=(2, 10))
theme_button = ttk.Button(clock_card, command=toggle_theme)
theme_button.pack()

# --- Alarm card ---
alarm_card = make_card(container)
make_section_title(alarm_card, "⏰  ALARM")
make_hint(alarm_card, "Enter time in 24-hour format, e.g. 21:45")
alarm_entry = ttk.Entry(alarm_card)
alarm_entry.pack(fill="x")

# --- Stopwatch card ---
stopwatch_card = make_card(container)
make_section_title(stopwatch_card, "⏱  STOPWATCH")
stopwatch_label = tk.Label(stopwatch_card, text="00:00:00", font=(FONT_FAMILY, 26, "bold"))
stopwatch_label.pack(pady=(6, 10))
ttk.Button(stopwatch_card, text="Reset", command=reset_stopwatch).pack()

# --- World clock card ---
world_card = make_card(container)
make_section_title(world_card, "🌍  WORLD CLOCK")
make_hint(world_card, "Select a city / timezone")
timezone_combo = ttk.Combobox(world_card, values=TIMEZONES, state="readonly")
timezone_combo.set(TIMEZONES[0])
timezone_combo.pack(fill="x", pady=(0, 10))
ttk.Button(world_card, text="Show World Time", command=show_world_time).pack()
world_label = tk.Label(world_card, font=(FONT_FAMILY, 22, "bold"))
world_label.pack(pady=(10, 0))

# --- Voice + calendar card ---
extra_card = make_card(container, pad_y=(0, 0))
btn_row = tk.Frame(extra_card)
btn_row.pack(fill="x")
btn_row.columnconfigure(0, weight=1)
btn_row.columnconfigure(1, weight=1)
ttk.Button(btn_row, text="🔊 Speak Time", command=speak_time).grid(row=0, column=0, sticky="ew", padx=(0, 6))
ttk.Button(btn_row, text="📅 Calendar", command=show_calendar).grid(row=0, column=1, sticky="ew", padx=(6, 0))
calendar_label = tk.Label(extra_card, font=(FONT_FAMILY, 12))
calendar_label.pack(pady=(12, 0))


# ================= START =================

apply_theme()        # paint the initial theme
update_clock()        # start updating clock every second
draw_analog_clock()    # start drawing the round analog clock
check_alarm()          # start checking alarm every second
stopwatch()            # start stopwatch counting

root.mainloop()