import tkinter as tk
from voicecontrol.st import StateMachine
import time


def create_root(time_delta=0.05):
    root = tk.Tk()
    root.attributes("-alpha", 0.9)
    root.attributes("-toolwindow", True)
    root.attributes("-topmost", True)
    root.geometry("300x80")
    root.title("Lujy")

    mode_label_var = tk.StringVar()
    mode_label = tk.Label(root, textvariable=mode_label_var)
    mode_label.pack()

    state_label_var = tk.StringVar()
    state_label = tk.Label(root, textvariable=state_label_var)
    state_label.pack()

    chars = "  ".join(f"{i+1} {c}" for i, c in zip(range(1000), ('，', " 。","“”", "！","？","【】","「」","（）")))
    print(chars)
    fix_label_var = tk.StringVar()
    fix_label = tk.Label(root, textvariable=fix_label_var)
    fix_label.pack()

    fix_label_var.set(chars)
    mode_label.setvar("模式")
    state_label.setvar("状态值 NA")

    last = time.time()

    def render_event(st: StateMachine):
        nonlocal last
        mode_label_var.set(f"{st.model.__class__.__name__}")
        state_label_var.set(f"状态值 {st.state}")
        now = time.time()

        if now - last > time_delta:
            last = now
            root.update()

    return render_event
