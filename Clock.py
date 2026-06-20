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
import pytz
import pyttsx3


# ================= VOICE ENGINE =================

# Text-to-speech engine used for the "Speak Current Time" button and alarm alert
engine = pyttsx3.init()


# ================= COLOR THEMES =================

THEMES = {
    "dark": {
        "bg": "#1e1f29",
        "card": "#272935",
        "text": "#f2f2f2",
        "accent": "#00e0ff",
        "muted": "#9aa0ad",
    },
    "light": {
        "bg": "#f4f5f7",
        "card": "#ffffff",
        "text": "#1e1f29",
        "accent": "#0078d4",
        "muted": "#5b6270",
    },
}

# Common timezones for the World Clock dropdown
TIMEZONES = [
    "Asia/Colombo",
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
root.geometry("480x760")
root.resizable(False, False)

FONT_FAMILY = "Segoe UI"


# ================= CLOCK =================

def update_clock():
    """Refresh the time and date labels every second."""
    time_label.config(text=strftime("%I:%M:%S %p"))
    date_label.config(text=strftime("%A, %d %B %Y"))
    root.after(1000, update_clock)


# ================= THEME =================

def apply_theme():
    """Repaint every widget using the colors for the current theme."""
    theme = THEMES["dark"] if dark_mode else THEMES["light"]

    root.configure(bg=theme["bg"])
    container.configure(bg=theme["bg"])

    for card in cards:
        card.configure(bg=theme["card"])

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

def check_alarm():
    """
    Compare the alarm time entered by the user (HH:MM, 24-hour format)
    with the current system time. If they match, show a popup and
    speak an alert out loud.
    """
    alarm_time = alarm_entry.get()
    current_time = strftime("%H:%M")

    if alarm_time == current_time:
        messagebox.showinfo("Alarm", "⏰ Alarm Ringing!")
        engine.say("Your alarm is ringing")
        engine.runAndWait()

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
        timezone = timezone_combo.get()
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
check_alarm()          # start checking alarm every second
stopwatch()            # start stopwatch counting

root.mainloop()