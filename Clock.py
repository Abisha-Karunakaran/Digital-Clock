"""
Advanced Digital Clock
-----------------------
A Tkinter desktop app with:
    - Live digital clock (time + date)
    - Dark/Light theme toggle
    - Alarm (checks every second against entered HH:MM)
    - Stopwatch (start/reset)
    - World clock (timezone lookup)
    - Voice announcement of current time (text-to-speech)
    - Simple calendar display (today's date)
"""

import tkinter as tk
from tkinter import messagebox
from time import strftime
import datetime
import pytz
import pyttsx3


# ================= VOICE ENGINE =================

# Text-to-speech engine used for the "Speak Current Time" button and alarm alert
engine = pyttsx3.init()


# ================= MAIN WINDOW =================

root = tk.Tk()
root.title("Advanced Digital Clock")
root.geometry("650x700")
root.resizable(False, False)   # fixed size window, looks cleaner

# Tracks whether the app is currently in dark mode (used by change_theme)
dark_mode = True


# ================= CLOCK =================

def update_clock():
    """Refresh the time and date labels every second."""
    current_time = strftime("%I:%M:%S %p")   # e.g. 09:30:15 PM
    time_label.config(text=current_time)

    current_date = strftime("%A, %d %B %Y")  # e.g. Saturday, 20 June 2026
    date_label.config(text=current_date)

    # Schedule this function to run again after 1000ms (1 second)
    root.after(1000, update_clock)


# ================= THEME =================

def change_theme():
    """Toggle between dark and light color schemes."""
    global dark_mode

    if dark_mode:
        # Switch to light mode
        root.configure(bg="white")
        time_label.config(bg="white", fg="black")
        date_label.config(bg="white", fg="black")
        dark_mode = False
    else:
        # Switch to dark mode
        root.configure(bg="black")
        time_label.config(bg="black", fg="cyan")
        date_label.config(bg="black", fg="white")
        dark_mode = True


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

    # Keep checking every second
    root.after(1000, check_alarm)


# ================= STOPWATCH =================

stopwatch_seconds = 0   # total elapsed seconds
running = True          # stopwatch is always running in this version


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
    """
    Look up the current time in the timezone entered by the user
    (e.g. 'Asia/Tokyo'). Shows 'Invalid Timezone' if the name is wrong.
    """
    try:
        timezone = country_entry.get()
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
    calendar_label.config(text=today.strftime("%d %B %Y\n%A"))


# ================= GUI LAYOUT =================

root.configure(bg="black")

# --- Time display ---
time_label = tk.Label(root, font=("Arial", 45, "bold"), bg="black", fg="cyan")
time_label.pack(pady=20)

# --- Date display ---
date_label = tk.Label(root, font=("Arial", 20), bg="black", fg="white")
date_label.pack()

# --- Theme toggle button ---
tk.Button(root, text="🌙 Dark / Light Mode", command=change_theme).pack(pady=10)

# --- Alarm section ---
tk.Label(root, text="Alarm Time (24 Hour HH:MM)").pack()
alarm_entry = tk.Entry(root)
alarm_entry.pack()

# --- Stopwatch section ---
tk.Label(root, text="Stopwatch").pack()
stopwatch_label = tk.Label(root, text="00:00:00", font=("Arial", 25))
stopwatch_label.pack()
tk.Button(root, text="Reset Stopwatch", command=reset_stopwatch).pack()

# --- World clock section ---
tk.Label(root, text="World Clock Timezone").pack()
tk.Label(root, text="Example: Asia/Tokyo").pack()
country_entry = tk.Entry(root)
country_entry.pack()
tk.Button(root, text="Show World Time", command=show_world_time).pack()
world_label = tk.Label(root, font=("Arial", 20))
world_label.pack()

# --- Voice button ---
tk.Button(root, text="🔊 Speak Current Time", command=speak_time).pack(pady=10)

# --- Calendar section ---
tk.Button(root, text="📅 Show Calendar", command=show_calendar).pack()
calendar_label = tk.Label(root, font=("Arial", 18))
calendar_label.pack()


# ================= START BACKGROUND TASKS =================

update_clock()     # start updating clock every second
check_alarm()       # start checking alarm every second
stopwatch()         # start stopwatch counting

root.mainloop()