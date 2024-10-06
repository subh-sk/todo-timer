import json
import os
import threading
import time
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

from tkcalendar import Calendar

# File to store permanent tasks
TASK_FILE = "tasks.json"

# Initialize task list
tasks = []

# Load tasks from the file
def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, 'r') as file:
            return json.load(file)
    return []

# Save tasks to the file
def save_tasks():
    permanent_tasks = [task for task in tasks if task['type'] == 'permanent']
    with open(TASK_FILE, 'w') as file:
        json.dump(permanent_tasks, file)

# Add task to the list with start and end time
def add_task():
    task = task_entry.get()
    start_time = start_time_entry.get()
    end_time = end_time_entry.get()
    task_type = 'permanent' if task_type_var.get() == 1 else 'temporary'
    
    if task and start_time and end_time:
        task_data = {
            'task': task,
            'start_time': start_time,
            'end_time': end_time,
            'type': task_type,
            'status': 'pending'
        }
        tasks.append(task_data)
        display_tasks()
        task_entry.delete(0, tk.END)
        start_time_entry.delete(0, tk.END)
        end_time_entry.delete(0, tk.END)
        start_timer_thread(start_time, end_time, task)  # Start a timer for the task
        if task_type == 'permanent':
            save_tasks()
    else:
        messagebox.showwarning("Input Error", "Please fill in all fields!")

# Display tasks in the listbox
def display_tasks():
    tasks_listbox.delete(0, tk.END)
    for task in tasks:
        status = get_task_status(task['start_time'], task['end_time'])
        tasks_listbox.insert(tk.END, f"{task['task']} (Start: {task['start_time']}, End: {task['end_time']}, Status: {status})")

# Remove the selected task
def remove_task():
    try:
        selected_task_index = tasks_listbox.curselection()[0]
        del tasks[selected_task_index]
        display_tasks()
        save_tasks()
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to remove!")

# Clear all tasks
def clear_tasks():
    tasks.clear()
    display_tasks()
    save_tasks()

# Function to determine the status of a task
def get_task_status(start_time_str, end_time_str):
    current_time = datetime.now()
    start_time = datetime.strptime(start_time_str, "%m/%d/%y %H:%M")
    end_time = datetime.strptime(end_time_str, "%m/%d/%y %H:%M")
    if current_time > end_time:
        return 'completed'
    elif start_time <= current_time <= end_time:
        return 'in progress'
    else:
        return 'pending'

# Start the timer for the task
def start_timer_thread(start_time, end_time, task_name):
    task_thread = threading.Thread(target=task_timer, args=(start_time, end_time, task_name))
    task_thread.start()

# Handle the timer, progress, and popup window
def task_timer(start_time_str, end_time_str, task_name):
    start_time = datetime.strptime(start_time_str, "%m/%d/%y %H:%M")
    end_time = datetime.strptime(end_time_str, "%m/%d/%y %H:%M")

    # Wait for the system time to match the start time
    while True:
        current_time = datetime.now()
        if current_time >= start_time:
            break
        time.sleep(1)

    # Create a popup window to display the task progress
    popup = tk.Toplevel()
    popup.title(f"Task: {task_name}")
    popup.geometry("300x200")
    popup.attributes("-topmost", True)  # Always on top
    popup.protocol("WM_DELETE_WINDOW", lambda: None)  # Override the close button
    popup.config(bg="#2e2d2d")  # Background color

    # Responsive resizing
    popup.columnconfigure(0, weight=1)
    popup.rowconfigure([0, 1, 2, 3, 4], weight=1)  # Added row for the button

    # Task name label
    task_label = tk.Label(popup, text=task_name, font=("Helvetica", 14), bg="#2e2d2d", fg="white")
    task_label.grid(row=0, column=0, pady=10, padx=10)

    # Calculate and display remaining hours
    remaining_label = tk.Label(popup, text="", bg="#2e2d2d", fg="white")
    remaining_label.grid(row=1, column=0, pady=5)

    # Progress bar for time tracking
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(popup, variable=progress_var, maximum=100)
    progress_bar.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    # Current time label
    current_time_label = tk.Label(popup, text="", bg="#2e2d2d", fg="white")
    current_time_label.grid(row=3, column=0, padx=10, pady=10)

    # Button to extract the progress bar
    extract_button = tk.Button(popup, text="Extract", command=lambda: extract_progress(popup, progress_bar, extract_button, task_name, progress_var, remaining_label))
    extract_button.grid(row=4, column=0, pady=10)

    # Timer loop to update the progress and time until the end time
    total_time = (end_time - start_time).total_seconds()

    while True:
        current_time = datetime.now()
        elapsed_time = (current_time - start_time).total_seconds()
        progress = (elapsed_time / total_time) * 100
        progress_var.set(progress)

        remaining_time = end_time - current_time
        remaining_hours = int(remaining_time.total_seconds() // 3600)
        remaining_minutes = int((remaining_time.total_seconds() % 3600) // 60)
        remaining_seconds = int(remaining_time.total_seconds() % 60)

        remaining_label.config(text=f"Remaining Time: {remaining_hours}h {remaining_minutes}m {remaining_seconds}s")
        current_time_label.config(text=f"Current Time: {current_time.strftime('%H:%M:%S')}")
        popup.update()

        if current_time >= end_time:
            break
        time.sleep(1)

    # Close the popup window once time is up
    popup.destroy()

# Extract progress bar into a frameless window with resizing and black background
def extract_progress(popup, progress_bar, extract_button, task_name, progress_var, remaining_label):
    # Create a new window to show the progress bar, without any frame
    extract_window = tk.Toplevel()
    extract_window.title(f"Extracted: {task_name}")
    extract_window.geometry("150x80")
    extract_window.attributes("-topmost", True)
    extract_window.overrideredirect(True)  # Remove the close/minimize/maximize buttons
    extract_window.config(bg="#2e2d2d")  # Set background to black

    # Allow resizing of the extracted window
    extract_window.resizable(True, True)

    # Add task name above the progress bar, show only the first 3 words followed by '...'
    truncated_task_name = ' '.join(task_name.split()[:3]) + "..." if len(task_name.split()) > 3 else task_name
    task_label = tk.Label(extract_window, text=truncated_task_name, font=("Helvetica", 10), bg="#2e2d2d", fg="white")
    task_label.pack(pady=1)

    # Add remaining time label to the new window
    extracted_remaining_time = tk.Label(extract_window, text=remaining_label.cget("text").replace("Remaining Time: ", ""), font=("Helvetica", 10), bg="#2e2d2d", fg="white")
    extracted_remaining_time.pack(pady=2)

    # Create a frame to hold the progress bar
    progress_frame = tk.Frame(extract_window, bg="#2e2d2d")
    progress_frame.pack(expand=True, fill="x", padx=10, pady=10)

    # Add progress bar to the new window
    extracted_progress = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
    extracted_progress.pack(expand=True, fill="x", padx=0, pady=0)

    # Update remaining time periodically in the extracted window
    def update_remaining_time():
        extracted_remaining_time.config(text=remaining_label.cget("text").replace("Remaining Time: ", ""))
        extract_window.after(1000, update_remaining_time)  # Update every second

    update_remaining_time()

    # Make window draggable
    make_draggable(extract_window)

    # Hide original progress bar
    progress_bar.grid_forget()

    # Change button text to "Undo"
    extract_button.config(text="Undo", command=lambda: undo_extract(popup, progress_bar, extract_window, extract_button, task_name, progress_var, remaining_label))

# Undo extraction and return progress bar to the original window
def undo_extract(popup, progress_bar, extract_window, extract_button, task_name, progress_var, remaining_label):
    # Close the extracted window
    extract_window.destroy()

    # Return the progress bar back to the original window
    progress_bar.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    # Change the button text back to "Extract"
    extract_button.config(text="Extract", command=lambda: extract_progress(popup, progress_bar, extract_button, task_name, progress_var, remaining_label))

# Make a window draggable
def make_draggable(widget):
    widget.bind("<Button-1>", lambda event: start_move(event, widget))
    widget.bind("<B1-Motion>", lambda event: move_window(event, widget))

def start_move(event, widget):
    widget.x = event.x
    widget.y = event.y

def move_window(event, widget):
    x = widget.winfo_x() - widget.x + event.x
    y = widget.winfo_y() - widget.y + event.y
    widget.geometry(f"+{x}+{y}")



# Function to check for in-progress tasks and open their windows on script start
def check_in_progress_tasks():
    for task in tasks:
        status = get_task_status(task['start_time'], task['end_time'])
        if status == 'in progress':
            start_timer_thread(task['start_time'], task['end_time'], task['task'])


# Function to open the calendar and time picker for start time
def select_start_time():
    # Clear existing input in the entry field
    start_time_entry.delete(0, tk.END)

    top = tk.Toplevel(root)
    top.title("Select Start Date and Time")

    cal = Calendar(top, selectmode='day')
    cal.pack(pady=10)

    def grab_date_time():
        date = cal.get_date()
        time_input = f"{hour_dropdown.get()}:{minute_dropdown.get()}"
        start_time_entry.insert(0, f"{date} {time_input}")
        top.destroy()

    hour_dropdown = ttk.Combobox(top, values=list(range(0, 25)), width=5)
    hour_dropdown.set(0)  # Default to 0
    hour_dropdown.pack(side=tk.LEFT, padx=(60, 2))

    minute_dropdown = ttk.Combobox(top, values=list(range(0, 60)), width=5)
    minute_dropdown.set(0)  # Default to 0
    minute_dropdown.pack(side=tk.LEFT)

    select_button = tk.Button(top, text="Select", command=grab_date_time)
    select_button.pack(pady=10)


# Function to open the calendar and time picker for end time
def select_end_time():
    # Clear existing input in the entry field
    end_time_entry.delete(0, tk.END)

    top = tk.Toplevel(root)
    top.title("Select End Date and Time")

    cal = Calendar(top, selectmode='day')
    cal.pack(pady=10)

    def grab_date_time():
        date = cal.get_date()
        time_input = f"{hour_dropdown.get()}:{minute_dropdown.get()}"
        end_time_entry.insert(0, f"{date} {time_input}")
        top.destroy()

    hour_dropdown = ttk.Combobox(top, values=list(range(0, 24)), width=5)
    hour_dropdown.set(0)  # Default to 0
    hour_dropdown.pack(side=tk.LEFT, padx=(60, 2))

    minute_dropdown = ttk.Combobox(top, values=list(range(0, 60)), width=5)
    minute_dropdown.set(0)  # Default to 0
    minute_dropdown.pack(side=tk.LEFT)

    select_button = tk.Button(top, text="Select", command=grab_date_time)
    select_button.pack(pady=10)



# Initialize Tkinter window
root = tk.Tk()
root.title("Custom To-Do List with Timer")
root.geometry("500x750")
root.config(bg="#2e2d2d")  # Background color



# Task Label and Entry
task_label = tk.Label(root, text="Task:", bg="#f2f2f2")
task_label.pack(pady=5)

task_entry = tk.Entry(root, width=40)
task_entry.pack(pady=5)

# Start Time Label and Entry
start_time_label = tk.Label(root, text="Start Time:", bg="#f2f2f2")
start_time_label.pack(pady=5)

start_time_entry = tk.Entry(root, width=40)
start_time_entry.pack(pady=5)

# Start Time Button
start_time_button = tk.Button(root, text="Select Start Time", command=select_start_time)
start_time_button.pack(pady=5)

# End Time Label and Entry
end_time_label = tk.Label(root, text="End Time:", bg="#f2f2f2")
end_time_label.pack(pady=5)

end_time_entry = tk.Entry(root, width=40)
end_time_entry.pack(pady=5)

# End Time Button
end_time_button = tk.Button(root, text="Select End Time", command=select_end_time)
end_time_button.pack(pady=5)

# Task Type (Permanent / Temporary)
task_type_var = tk.IntVar(value=1)  # Default to permanent
task_type_frame = tk.Frame(root, bg="#f2f2f2")
task_type_frame.pack(pady=5)

task_type_permanent = tk.Radiobutton(task_type_frame, text="Permanent", variable=task_type_var, value=1, bg="#f2f2f2")
task_type_permanent.pack(side=tk.LEFT, padx=10)

task_type_temporary = tk.Radiobutton(task_type_frame, text="Temporary", variable=task_type_var, value=2, bg="#f2f2f2")
task_type_temporary.pack(side=tk.LEFT, padx=10)

# Add Task Button
add_task_button = tk.Button(root, text="Add Task", command=add_task)
add_task_button.pack(pady=5)

# Tasks Listbox with Scrollbar
tasks_frame = tk.Frame(root)
tasks_frame.pack(pady=10)

tasks_listbox = tk.Listbox(tasks_frame, width=60, height=20)
tasks_listbox.pack(side=tk.LEFT)

# Create a scrollbar
scrollbar = tk.Scrollbar(tasks_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Attach the scrollbar to the listbox
tasks_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=tasks_listbox.yview)

# Remove Task Button
remove_task_button = tk.Button(root, text="Remove Selected Task", command=remove_task)
remove_task_button.pack(pady=5)

# Clear All Tasks Button
clear_tasks_button = tk.Button(root, text="Clear All Tasks", command=clear_tasks)
clear_tasks_button.pack(pady=5)

# Load existing tasks
tasks = load_tasks()
display_tasks()

# Check for in-progress tasks on startup
check_in_progress_tasks()

# Start the Tkinter event loop
root.mainloop()
