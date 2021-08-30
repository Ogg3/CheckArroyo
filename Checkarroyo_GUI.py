"""
Version 0-5-8
github.com/Ogg3/CheckArroyo
"""
from tkinter import filedialog

from Checkarroyo import writeHtmlReport
from lib import *

try:

    root = tk.Tk()
    root.title("Thunder")
    # root.geometry("1300x800")

    try:

        # Set frame and title
        window = tk.Frame(master=root, relief=RAISED, borderwidth=1, bg="blue")
        window.grid()

        mi = tk.Label(window, text="CheckArroyo")
        mi.grid(row=0, column=0, sticky=N + S + E + W)
        mi.config(font=("Courier", "15"))

        # Add logo
        #widget = tk.Label(window, compound='top')
        #widget.p = tk.PhotoImage(file="p.png")
        #widget['text'] = ""
        #widget['image'] = widget.p
        #widget.grid(row=0, column=1, sticky=N + S + E + W)

        # Lable and entry box to add path
        tk.Label(window, text="Enter path here. Ex C:\\folder\\input_file").grid(row=1, column=0, sticky=N + S + E + W)
        input_path = tk.Entry(window, width=40)
        input_path.grid(row=2, column=0, sticky=N + S + E + W)

        # Choose a file
        tk.Button(window, text="Choose a file",
                  command=lambda: ent_insert(input_path, filedialog.askopenfilename())
                  ).grid(row=2, column=1)

        # Output folder
        tk.Label(window, text="Enter path here. Ex C:\\output_folder").grid(row=3, column=0, sticky=N + S + E + W)
        output_path = tk.Entry(window, width=40)
        output_path.grid(row=4, column=0, sticky=N + S + E + W)

        # Choose a output folder
        tk.Button(window, text="Choose a path",
                  command=lambda: ent_insert(output_path, filedialog.askdirectory())
                  ).grid(row=4, column=1)

        # Lable and entry box to add start time
        tk.Label(window, text="Enter start time. Ex 2021-01-01").grid(row=5, column=0, sticky=N + S + E + W)
        time_start = tk.Entry(window, width=40)
        time_start.grid(row=6, column=0, sticky=N + S + E + W)

        # Lable and entry box to add stop time
        tk.Label(window, text="Enter stop time. Ex 2021-01-01").grid(row=7, column=0, sticky=N + S + E + W)
        time_stop = tk.Entry(window, width=40)
        time_stop.grid(row=8, column=0, sticky=N + S + E + W)

        # Lable and entry box for message id
        tk.Label(window, text="Enter conversation id.").grid(row=9, column=0, sticky=N + S + E + W)
        msg_id = tk.Entry(window, width=40)
        msg_id.grid(row=10, column=0, sticky=N + S + E + W)

        # Add text window to display info
        display_window = tk.Text(window)
        display_window.grid(row=0, column=2, sticky=N + S + E + W)

        # Writes html reports
        # input_path, output_path, speed, mode, time_start, time_stop, contentmanager, msg_id, debug_mode
        tk.Button(window, text="Write html reports",
                  command=lambda: writeHtmlReport([return_entry_check(input_path),
                                                   return_entry_check(output_path),
                                                   speed.get(),
                                                   mode.get(),
                                                   return_entry(time_start),
                                                   return_entry(time_stop),
                                                   return_entry(msg_id),
                                                   display_window])
                  ).grid(row=6, column=1)

        # StringVar to hold value to use
        speed = StringVar()

        # StringVar to hold value to use
        mode = StringVar()

        # Radio buttons to select speed
        tk.Label(window, text="Select one").grid(row=2, column=2, sticky=N + S + E + W)
        chkat = Radiobutton(window, text="Don't Check for attachments", variable=speed, value="F")
        chkat.grid(row=3, column=2)
        Dchkat = Radiobutton(window, text="Check for attachments", variable=speed, value="S")
        Dchkat.grid(row=4, column=2)

        # Radio buttons to select mode
        tk.Label(window, text="Select mode").grid(row=6, column=2, sticky=N + S + E + W)
        IOS = Radiobutton(window, text="Mode - iPhone", variable=mode, value="IOS")
        IOS.grid(row=7, column=2)
        ARY = Radiobutton(window, text="Mode - Only Arroyo.db", variable=mode, value="ARY")
        ARY.grid(row=8, column=2)
        AND = Radiobutton(window, text="Mode - Android (Coming soon)", variable=mode, value="AND")
        AND.grid(row=9, column=2)

        # Set default value
        speed.set("S")
        mode.set("IOS")

        # Padding
        tk.Label(window, text="", bg="blue").grid(row=11, column=2, sticky=N + S + E + W)

    except Exception as e:
        messagebox.showinfo("ERROR", traceback.format_exc() + "\n" + e.__doc__)

    root.mainloop()

except Exception as e:
    messagebox.showinfo("ERROR", traceback.format_exc() + "\n" + e.__doc__)
