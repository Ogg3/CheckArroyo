"""
v0-6-0-beta
github.com/Ogg3/CheckArroyo
"""
import tkinter
import tkinter as tk
import traceback
from tkinter import filedialog
from tkinter import messagebox
from tkinter import Radiobutton
from Checkarroyo import displayIOScontentmanagers_GUI
from Checkarroyo import writeHtmlReport


def main():
    try:
        root = tk.Tk()
        root.title("Thunder")
        root.geometry("1920x1080")

        # Insert a value in an entry box and del the existing text
        def ent_insert(ent, var):
            ent.delete(0, 'end')
            ent.insert(0, var)

        # Retrun the value from an entry widget and check if widget is empty
        def return_entry_check(en):
            content = en.get()
            if content == "":
                messagebox.showinfo("ERROR", "ENTRY BOX "+str(en)+"IS EMPTY")
            else:
                return content

        # Retrun the value from an entry widget and check if widget is empty
        def return_entry(en):
            return en.get()

        # Write a list to a text widget
        def write_to_tex(lista, tex):
            try:
                tex.config(state=tk.NORMAL)

                def write_to(strin, tex):
                    s = strin + "\n"
                    tex.insert(tk.END, s)
                    tex.see(tk.END)

                tex.insert(tk.END, "Found content " + str(len(lista)) + " managers.\n")

                for i in range(len(lista)):
                    write_to(str(lista[i][0]), tex)
                    write_to(str(lista[i][1])+" MB", tex)
                    tex.insert(tk.END,"\n")

                tex.config(state=tk.DISABLED)
            except Exception as e:
                messagebox.showinfo("ERROR", traceback.format_exc() + "\n" + e.__doc__)

        # Write a string to a text widget
        def write_string_tex(strin, tex):
            tex.config(state=tk.NORMAL)

            s = str(strin) + "\n"
            tex.insert(tk.END, s)
            tex.see(tk.END)

            tex.config(state=tk.DISABLED)

        # Write a strin to a rapport window
        def write_rapport_tex(lista, tex):
            try:
                def write_to(strin, tex):
                    s = strin + "\n"
                    tex.insert(tk.END, s)
                    tex.see(tk.END)

                for i in range(len(lista)):
                    write_to(str(lista[i]), tex)
                tex.insert(tk.END, "]" + "\n")
                tex.see(tk.END)
            except Exception as e:
                messagebox.showinfo("ERROR", traceback.format_exc() + "\n" + e.__doc__)

        def write_rapport_image_tex(im, tex):
            try:
                tex.insert(tk.END, "[" + "\n")
                tex.see(tk.END)

                s = str(im)
                tex.insert(tk.END, s)
                tex.see(tk.END)

                tex.insert(tk.END, "\n")
                tex.see(tk.END)
            except Exception as e:
                messagebox.showinfo("ERROR", traceback.format_exc() + "\n" + e.__doc__)

        # Retrive the content of a text widget
        def retrieve_input(tex):
            lista = []
            strin = ""
            for i in tex.get("1.0", 'end-1c'):
                if i != "\n":
                    strin = strin + i
                else:
                    lista.append(strin)
                    strin = ""
            return lista

        # Main menu
        def main_menu():

            try:

                # Set frame and title
                window = tk.Frame(root, width=1920, height=1080, bg="blue")
                window.place(x=0, y=0)
                mi = tk.Label(window, text="Snapchat - check console for progress")
                mi.place(relx=.37, rely=.02, anchor="c")
                mi.config(font=("Courier", "44"))

                # Add logo
                widget = tk.Label(window, compound='top')
                widget.p = tk.PhotoImage(file="p.png")
                widget['text'] = ""
                widget['image'] = widget.p
                widget.place(relx=.95, rely=.127, anchor="c")

                # Lable and entry box to add path
                tk.Label(window, text="Enter path here. Ex C:\\folder\\input_file").place(relx=.4, rely=.1)
                input_path = tk.Entry(window, width=40)
                input_path.place(relx=.45, rely=.15, anchor="c")

                # Choose a file
                tk.Button(window, text="Choose a file",
                          command=lambda: ent_insert(input_path, filedialog.askopenfilename())
                          ).place(relx=.55, rely=.13)

                # Output folder
                tk.Label(window, text="Enter path here. Ex C:\\output_folder").place(relx=.4, rely=.18)
                output_path = tk.Entry(window, width=40)
                output_path.place(relx=.45, rely=.22, anchor="c")

                # Choose a output folder
                tk.Button(window, text="Choose a path",
                          command=lambda: ent_insert(output_path, filedialog.askdirectory())
                          ).place(relx=.55, rely=.20)

                # Lable and entry box to add contentmanager
                tk.Label(window, text="Enter path here. Ex Documents/contentmanagerV3_<id>/contentManagerDb.db").place(relx=.4, rely=.25)
                contentmanager = tk.Entry(window, width=40)
                contentmanager.place(relx=.45, rely=.30, anchor="c")

                # Lable and entry box to add start time
                tk.Label(window, text="Enter start time. Ex 2021-01-01").place(
                    relx=.4, rely=.35)
                time_start = tk.Entry(window, width=40)
                time_start.place(relx=.45, rely=.40, anchor="c")

                # Lable and entry box to add stop time
                tk.Label(window, text="Enter stop time. Ex 2021-01-01").place(
                    relx=.4, rely=.45)
                time_stop = tk.Entry(window, width=40)
                time_stop.place(relx=.45, rely=.50, anchor="c")

                # Lable and entry box for message id
                tk.Label(window, text="Enter conversation id.").place(
                    relx=.4, rely=.55)
                msg_id = tk.Entry(window, width=40)
                msg_id.place(relx=.45, rely=.60, anchor="c")

                # Add text window to display info
                display_window = tk.Text(window)
                display_window.place(relx=.02, rely=.05, height=700, width=700)


                # Writes html reports
                # input_path, output_path, speed, mode, time_start, time_stop, contentmanager, msg_id, debug_mode
                tk.Button(window, text="Write html reports",
                          command=lambda: writeHtmlReport([return_entry_check(input_path),
                                                              return_entry_check(output_path),
                                                              speed.get(),
                                                              mode.get(),
                                                              return_entry(time_start),
                                                              return_entry(time_stop),
                                                              return_entry_check(contentmanager),
                                                              return_entry(msg_id),
                                                           False])
                          ).place(relx=.55, rely=.35)

                # Displays content managers
                tk.Button(window, text="Get content managers",
                          command=lambda: write_to_tex(displayIOScontentmanagers_GUI(return_entry_check(input_path)), display_window)
                          ).place(relx=.55, rely=.30)

                # StringVar to hold value to use
                speed = tkinter.StringVar()

                # StringVar to hold value to use
                mode = tkinter.StringVar()

                # Radio buttons to select speed
                txt = Radiobutton(window, text="Speed - Fast", variable=speed, value="F")
                txt.place(relx=.65, rely=.2)
                pdf = Radiobutton(window, text="Speed - Slow", variable=speed, value="S")
                pdf.place(relx=.65, rely=.25)

                # Radio buttons to select mode
                jpg = Radiobutton(window, text="Mode - iPhone", variable=mode, value="IOS")
                jpg.place(relx=.65, rely=.3)
                jif = Radiobutton(window, text="Mode - Only Arroyo.db", variable=mode, value="ARY")
                jif.place(relx=.65, rely=.35)
                doc = Radiobutton(window, text="Mode - Android (Coming soon)", variable=mode, value="AND")
                doc.place(relx=.65, rely=.4)

                # Set default value
                speed.set("F")
                mode.set("IOS")


                # Lable and entry box for message id
                tk.Label(window, text="""
                How to:
                1 - Choose a input file
                2 - Choose output folder
                3 - Select a speed
                4 - Select a mode
                5 - Click on "Get content managers"
                6 - Copy paste one of the paths to the text window for content managers
                7 - Click write html reports
                
                Optional filters
                Select a start and stop time
                Select a conversation ID
                """).place(
                    relx=.6, rely=.55)

                """# Lable and entry box to add files of interest
                tk.Label(window, text="Enter path here. Ex C:\\folder\\input_file").place(relx=.4, rely=.62)
                filesof_int = tk.Entry(window, width=40)
                filesof_int.place(relx=.45, rely=.65, anchor="c")

                # Choose a file
                tk.Button(window, text="Choose a file",
                          command=lambda: ent_insert(filesof_int, filedialog.askopenfilename())
                          ).place(relx=.55, rely=.65)"""


            except Exception as e:
                messagebox.showinfo("ERROR", traceback.format_exc() + "\n" + e.__doc__)

        main_menu()
        root.mainloop()

    except Exception as e:
        messagebox.showinfo("ERROR", traceback.format_exc() + "\n" + e.__doc__)


if __name__ == '__main__':
    main()
