#uses python3.4

import datetime
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox
from functools import partial

import cProfile

__author__ = "Nate Fehrenbach"


run_num = 36


class pvsk_gui:
    """
    Custom tkinter class definition for pvsk_gui
    """
    def __init__(self):
        """
        Initializes the custom tkinter root object
        """
        self.version_num = "1.1"
        self.name = "PVSK QC Annotator "
        self.num_options = [1, 1+run_num, 1+(2*run_num), 1+(3*run_num)]
        self.save_path = ""
        # Main Tk Objects
        self.root = Tk()
        self.canvas = tk.Canvas(self.root, width=1050, height=600)
        self.canvas.pack(side=tk.LEFT, expand=True, fill='both')
        self.scrollbar = tk.Scrollbar(self.root, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill='y')
        self.root.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.mainframe = self.initialize_rootframe(self.canvas)
        self.mainframe.bind('<Configure>', self.on_configure)
        self.canvas.create_window((0, 0), window=self.mainframe, anchor='nw')
        # Naming lists, note that they are modified     # (Note from Mark): Wouldn't it be just as easy to define these at insertion time?
        self.name_list = ["name_" + str(a+1) for a in range(run_num)]
        self.beg_list = ["begin_" + str(x+1) for x in range(run_num)]
        self.end_list = ["end_" + str(y+1) for y in range(run_num)]
        self.proj_list = ["proj_" + str(b+1) for b in range(run_num)]
        self.qual_list = ["qual_" + str(z+1) for z in range(run_num)]
        self.note_list = ["note_" + str(w+1) for w in range(run_num)]
        self.clr_list = ["clear_" + str(c+1) for c in range(run_num)]
        self.chk_on_list = ["chk_on_" + str(d+1) for d in range(run_num)]
        self.chk_off_list = ["chk_off_" + str(e+1) for e in range(run_num)]
        # Gui Objects
        self.string_vars = self.init_string_vars()
        self.buttons = self.init_buttons()
        self.fields = self.init_fields()
        self.labels = self.init_labels()
        self.drops = self.init_drops()
        self.checks = self.init_chk()
        #print('init_string_vars took: '+str(timeit.timeit('self.string_vars = self.init_string_vars()', number = 1, globals={"self":self})))
        #print('init_buttons took: '+str(timeit.timeit('self.buttons = self.init_buttons()', number = 1, globals={"self":self})))
        #print('init_fields took: '+str(timeit.timeit('self.fields = self.init_fields()', number = 1, globals={"self":self})))
        #print('init_labels took: '+str(timeit.timeit('self.labels = self.init_labels()', number = 1, globals={"self":self})))
        #print('init_drops took: '+str(timeit.timeit('self.drops = self.init_drops()', number = 1, globals={"self":self})))
        #print('init_chk took: '+str(timeit.timeit('self.checks = self.init_chk()', number = 1, globals={"self":self})))
        # Place gui objects
        self.place_objects()

    def init_buttons(self) -> dict:
        """
        Initialize the buttons
        :return: dict
        """
        bd = {'submit': ttk.Button(self.mainframe, text="Submit", command=self.submit),
              'save_as': ttk.Button(self.mainframe, text="Save As", command=self.save_config)}
        for begin in self.beg_list:
            text = begin[0:1].upper() + begin[1:begin.find("_")] + " Time " + begin[begin.find("_") + 1:]
            bd[begin] = ttk.Button(self.mainframe, text=text, command=partial(self.timestamp, begin))
        for end in self.end_list:
            text = end[0:1].upper() + end[1:end.find("_")] + " Time " + end[end.find("_") + 1:]
            bd[end] = ttk.Button(self.mainframe, text=text, command=partial(self.timestamp, end), state=DISABLED)
        for clear, name in zip(self.clr_list, self.name_list):
            bd[clear] = ttk.Button(self.mainframe, textvariable=self.string_vars[clear],
                                   command=partial(self.clear, name))
        return bd

    def init_string_vars(self) -> dict:
        """
        Return dict of StringVar and BooleanVar objects for the gui
        :return: dict
        """
        str_vr = {'date': StringVar(), 'time': StringVar(),
                  'experiment': StringVar(), "number": StringVar(),
                  'save_loc': StringVar(), "next_layer": StringVar()}
        str_vr['save_loc'].set("C:\\")
        # Add StringVar objects for the timestamp inputs and quality inputs
        n = 0
        for item in self.name_list:
            str_vr[item] = StringVar()
            str_vr[item].set("Sub " + str(n+1))
            n += 1
        for item in self.proj_list:
            str_vr[item] = StringVar()
            str_vr[item].set("Never")
        for item in self.beg_list:
            str_vr[item] = StringVar()
        for item in self.end_list:
            str_vr[item] = StringVar()
        for item in self.qual_list:
            str_vr[item] = StringVar()
        for item in self.note_list:
            str_vr[item] = StringVar()
        for item in self.clr_list:
            str_vr[item] = StringVar()
            synth_name = "name_" + item[item.find("_")+1:]
            str_vr[item].set("Clear " + str_vr[synth_name].get())
        for item in self.chk_on_list:
            str_vr[item] = BooleanVar()
            str_vr[item].set(False)
        for item in self.chk_off_list:
            str_vr[item] = BooleanVar()
            str_vr[item].set(True)
        return str_vr

    def initialize_rootframe(self, root: object) -> object:
        """
        Initializes the root Tk object, initializes and returns frame object
        :param root: tkinter.Tk object
        :return: object
        """
        self.root.title(self.name + "v." + self.version_num)
        frame = ttk.Frame(root, padding="12 12 12 12", relief="raised")
        frame.grid(column=0, row=0, sticky=(N, W, E, S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        return frame

    def on_configure(self, event) -> None:
        """
        Update scroll region for the frame on scrollbar event
        :param event: Scrollbar interaction event
        :return: None
        """
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def on_mouse_wheel(self, event) -> None:
        """
        Scrolls everything with the mouse wheel
        :param event: mouse wheel event
        :return: None
        """
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter#comment4471062_4140988
    def validateTime(self, d, i, P, s, S, v, V, W):
        example = "2018/01/01 15:07:58"
        try:
            datetime.datetime.strptime(P+example[len(P):],"%Y/%m/%d %H:%M:%S")
            return True
        except:
            return False

    def init_fields(self) -> dict:
        """
        Initialize the entry fields and put them into a dict
        :return: dict
        """
        fd = {'experiment': ttk.Entry(self.mainframe, textvariable=self.string_vars['experiment'], width=5)}
        fd['experiment'].bind('<Key>', self.set_series)
        validate = (self.root.register(self.validateTime),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        for note in self.note_list:
            fd[note] = ttk.Entry(self.mainframe, textvariable=self.string_vars[note], width=15)
        for begin in self.beg_list:
            fd[begin] = ttk.Entry(self.mainframe, textvariable=self.string_vars[begin], width=20, validate="key", validatecommand=validate)
        for end in self.end_list:
            fd[end] = ttk.Entry(self.mainframe, textvariable=self.string_vars[end], width=20, validate="key", validatecommand=validate)
        return fd

    def init_labels(self) -> dict:
        """
        Initialize the label objects and put them into a dict
        :return: dict
        """
        ld = {'instruction':
                  ttk.Label(self.mainframe,
                            text="Enter the cell run's series and select the starting series number to begin:"),
              'save_loc': ttk.Label(self.mainframe, textvariable=self.string_vars['save_loc']),
              'save_lbl': ttk.Label(self.mainframe, text="Current save location:\t"),
              'experiment': ttk.Label(self.mainframe, text="Series ID:\t"),
              'number': ttk.Label(self.mainframe, text="First Substrate in series:\t"),
              'empty': ttk.Label(self.mainframe, text=""),
              'empty2': ttk.Label(self.mainframe, text="Projected\nAnneal\nCompletion"),
              'quality': ttk.Label(self.mainframe, text="Quality:"),
              'quality2': ttk.Label(self.mainframe, text="Next Layer\nQuality:"),
              'note': ttk.Label(self.mainframe, text="Notes:"),
              'b_lock': ttk.Label(self.mainframe, text="Begin\nUnlocked\n/Locked"),
              'e_lock': ttk.Label(self.mainframe, text="End\nUnlocked\n/Locked"),
              'next_layer': ttk.Label(self.mainframe, text="Next Layer:")}
        for n in range(36):
            ld["time" + str(n)] = ttk.Label(self.mainframe, text="Timestamps:\t")
        #for begin in self.beg_list:
        #    ld[begin] = ttk.Label(self.mainframe, textvariable=self.string_vars[begin], width=20)
        #for end in self.end_list:
        #    ld[end] = ttk.Label(self.mainframe, textvariable=self.string_vars[end], width=20)
        for name in self.name_list:
            ld[name] = ttk.Label(self.mainframe, textvariable=self.string_vars[name], width=7)
        for proj in self.proj_list:
            ld[proj] = ttk.Label(self.mainframe, textvariable=self.string_vars[proj], width=20)
        target = ["target_" + str(n+1) for n in range(36)]
        for t in target:
            ld[t] = ttk.Label(self.mainframe, text="Target Time: ")
        return ld

    def init_drops(self) -> dict:
        """
        Initialize drop down menus
        :return: dict
        """
        dd = {'number': ttk.Combobox(self.mainframe, textvariable=self.string_vars['number'], values=self.num_options,
                                     state='readonly', width=5)}
        dd['number'].set(self.num_options[0])
        dd['number'].bind("<Button-1>", self.set_series)
        quality = ["", "Good", "Bad", "OK", "Pass", "Fail"]
        nextLayers = ["", "Spiro"]
        dd["next_layer"] = ttk.Combobox(self.mainframe, textvariable=self.string_vars["next_layer"],
                                       values=nextLayers, width=10)
        dd["next_layer"].set(nextLayers[1])
        for qual in self.qual_list:
            dd[qual] = ttk.Combobox(self.mainframe, textvariable=self.string_vars[qual],
                                    values=quality, state='readonly', width=10)
            dd[qual].set(quality[0])
            qual2 = "qual2_"+(qual.split("_")[1])
            dd[qual2] = ttk.Combobox(self.mainframe, textvariable=StringVar(),
                                    values=quality, state='readonly', width=10)
            dd[qual2].set(quality[0])
        return dd

    def init_chk(self) -> dict:
        """
        Initialize check boxes for locking and unlocking timestamp buttons into a dictionary containing all the objects
        :return: dict
        """
        cd = {}
        for chk in self.chk_on_list:
            cd[chk] = ttk.Checkbutton(self.mainframe, text="", variable=self.string_vars[chk],
                                      command=partial(self.lock, chk))
        for chk in self.chk_off_list:
            cd[chk] = ttk.Checkbutton(self.mainframe, text="", variable=self.string_vars[chk],
                                      command=partial(self.lock, chk))
        return cd

    def place_objects(self) -> None:
        """
        Place labels, checkboxes, buttons, entry fields, and drop down menus(comboboxes)
        :return: None
        """
        self.labels['instruction'].grid(column=0, row=0, columnspan=4)
        self.labels['save_lbl'].grid(column=1, row=1)
        self.labels['save_loc'].grid(column=2, row=1)
        self.buttons['save_as'].grid(column=3, row=1)
        self.labels['experiment'].grid(column=0, row=2)
        self.fields['experiment'].grid(column=1, row=2)
        self.labels['number'].grid(column=3, row=2)
        self.drops['number'].grid(column=4, row=2)
        self.labels['empty'].grid(column=7, row=4)
        self.labels['empty2'].grid(column=4, row=5)
        self.labels['b_lock'].grid(column=3, row=5)
        self.labels['quality'].grid(column=7, row=5)
        self.labels['quality2'].grid(column=8, row=5)
        self.labels['note'].grid(column=9, row=5)
        self.labels['e_lock'].grid(column=6, row=5)
        self.labels['next_layer'].grid(column=8, row=1)
        self.drops['next_layer'].grid(column=8, row=2)
        start = 5
        col = 0
        # Column 0
        n = start
        for key, gui in self.buttons.items():
            if key.find("clear") != -1:
                gui.grid(column=col, row=n*2)
                n += 1
        # Column 1
        # Column 1, odd rows
        col += 1
        n = start
        for key, gui in self.labels.items():
            if key.find("time") != -1:
                self.labels["time"+str(n-start)].grid(column=col, row=(2 * n) + 1)
                n += 1
        n = start
        # Column 1, even rows
        for key, gui in self.labels.items():
            if key.find("name") != -1:
                gui.grid(column=col, row=2 * n)
                n += 1
        n = start
        # Column 2
        col += 1
        for key, gui in self.fields.items():
            if key.find("begin") != -1:
                gui.grid(column=col, row=(2 * n) + 1)
                n += 1
        n = start
        for key, gui in self.buttons.items():
            # print(key)
            if key.find("begin") != -1:
                gui.grid(column=col, row=2 * n)
                n += 1
        # Column 3
        col += 1
        n = start
        for key, gui in self.checks.items():
            if key.find("chk_on") != -1:
                gui.grid(column=col, row=2*n)
                n += 1
        n = start
        # Column 4
        col += 1
        # for key, gui in self.labels.items():
        #     if key.find("target") != -1:
        #         gui.grid(column=col, row=2*n)
        #         n += 1
        n = start
        # Column 5
        # col += 1
        for key, gui in self.labels.items():
            if key.find("proj") != -1:
                gui.grid(column=col, row=2*n)
                n += 1
        n = start
        # Column 4b
        col += 1
        # Column 4b, odd rows
        n = start
        for key, gui in self.fields.items():
            if key.find("end") != -1:
                gui.grid(column=col, row=(2 * n) + 1)
                n += 1
        n = start
        # Column 4b, even rows
        for key, gui in self.buttons.items():
            if key.find("end") != -1:
                gui.grid(column=col, row=2*n)
                n += 1
        n = start
        # Column 5b
        col += 1
        for key, gui in self.checks.items():
            if key.find("chk_off") != -1:
                gui.grid(column=col, row=2*n)
                n += 1
        n = start
        # Column 6b
        col += 1
        for key, gui in self.drops.items():
            if key.find("qual_") != -1:
                gui.grid(column=col, row=2*n)
                key2 = key.split("_")
                key2 = key2[0]+"2_"+key2[1]
                self.drops[key2].grid(column=col+1, row=2*n)
                n += 1
        n = start
        # Column 7b
        # col += 1
        # Column 8b
        col += 2
        for key, gui in self.fields.items():
            if key.find("note") != -1:
                gui.grid(column=col, row=2*n)
                n += 1
        self.buttons["submit"].grid(column=3, row=2*n)

    def get_gui_objects(self, name: str) -> dict:
        """
        Get dictionary with keys=begin, begin_b, end, end_b, chk_on_v, check_on, chk_off_v, chk_off, qual, note
        :param name:
        :return:
        """
        number = name[name.find("_")+1:]
        begin = "begin_" + number
        end = "end_" + number
        chk_on = "chk_on_" + number
        chk_off = "chk_off_" + number
        qual = "qual_" + number
        note = "note_" + number
        proj = "proj_" + number
        obj = {"begin": self.string_vars[begin], "begin_b": self.buttons[begin],
               "end": self.string_vars[end], "end_b": self.buttons[end],
               "chk_on_v": self.string_vars[chk_on], "chk_on": self.checks[chk_on],
               "chk_off_v": self.string_vars[chk_off], "chk_off": self.checks[chk_off],
               "qual": self.string_vars[qual], 'qual_c': self.drops[qual],
               "note": self.string_vars[note], 'note_f': self.fields[note],
               "proj": self.string_vars[proj]}
        return obj

    def set_series(self, event) -> None:
        """
        Call set_names for entry field
        :param event: event
        :return: None
        """
        self.set_names()

    def set_names(self) -> None:
        """
        Update labels and buttons to include the name of the substrate they refer to.
        :return: None
        """
        series = self.string_vars["experiment"].get()
        if len(series) < 1:
            series = "Sub"
        try:
            number = int(self.string_vars["number"].get())
        except ValueError:
            messagebox.showerror("Integer Required", "Please enter an integer!")
        num = number
        for name in self.name_list:
            self.string_vars[name].set(series + " " + str(num))
            num += 1
        num = number
        for clear in self.clr_list:
            self.string_vars[clear].set("Clear " + series + " " + str(num))
            num += 1
        self.root.after(100, self.set_names)

    def clear(self, name: str) -> None:
        """
        Clear the variables captured for the substrate
        :param name: str, key to a dict to identify the substrate
        :return: None
        """
        obj = self.get_gui_objects(name)
        obj['begin'].set("")
        obj['begin_b'].config(state='normal')
        obj['end'].set("")
        obj['end_b'].config(state='disabled')
        obj['chk_on_v'].set(False)
        obj['chk_on'].config(state='normal')
        obj['chk_off_v'].set(True)
        obj['qual'].set("")
        obj['qual_c'].set("")
        obj['note'].set("")
        obj['proj'].set("Never")
        # obj['note_f'].set("")

    def lock(self, name: str) -> None:
        """
        Lock or unlock the timestamp buttons for the corresponding name in the substrate dictionary
        :param name: str, key for check dictionary relating to checkbox clicked
        :return: None
        """
        temp = name.find("_")
        temp2 = name[temp+1:].find("_")
        num = int(name[temp+temp2+2:])
        # print(name)
        if name.find("on") != -1:
            on = True
        else:
            on = False
        if on:
            if not self.string_vars[name].get():
                self.buttons["begin_" + str(num)].config(state='normal')
                self.fields["begin_" + str(num)].config(state='normal')
            else:
                self.buttons["begin_" + str(num)].config(state='disabled')
                self.fields["begin_" + str(num)].config(state='disabled')
                # print("disabled")
        else:
            if not self.string_vars[name].get():
                self.buttons["end_" + str(num)].config(state='normal')
                self.fields["end_" + str(num)].config(state='normal')
            else:
                self.buttons["end_" + str(num)].config(state='disabled')
                self.fields["end_" + str(num)].config(state='disabled')
                # print("disabled off")

    def timestamp(self, string: str) -> None:
        """
        Collect timestamp and assign to StringVar() indicated by dict reference to string_vars attribute
        :param string: str, key to a dict to identify which variable to capture the timestamp into
        :return: None
        """
        num = string[string.find("_")+1:]
        current_time = datetime.datetime.now()
        self.string_vars[string].set(self.frmt(current_time))
        if string.find("begin") != -1:
            self.string_vars["chk_on_" + num].set(True)
            self.string_vars["proj_" + num].set(self.frmt(current_time + datetime.timedelta(minutes=60)))
            self.labels["proj_"+num].after(3300000, self.labels["proj_"+num].config,{"foreground":"#F00"})      # Turns the label red after 55 minutes. Likely not the best way....
            self.string_vars["chk_off_" + num].set(False)
            self.lock("chk_on_" + num)
            self.lock("chk_off_" + num)
        else:
            self.string_vars["end_" + num].set(self.frmt(current_time))
            self.string_vars["chk_off_" + num].set(True)
            self.lock("chk_on_" + num)
            self.lock("chk_off_" + num)

    def frmt(self, time: datetime) -> str:
        """
        Reformat the string of a datetime object for increased legibility
        :param time: datetime, to be reformatted
        :return: str
        """
        #date = str(time.year) + "/" + str(time.month) + "/" + str(time.day)
        #hour = str("%02d" % (time.hour,))
        #min = str("%02d" % (time.minute,))
        #sec = str("%02d" % (time.second,))
        #return date + " " + hour + ":" + min + ":" + sec
        return time.strftime("%Y/%m/%d %H:%M:%S")

    def un_frmt(self, timestamp: str) -> datetime:
        """
        Turn a StringVar value into a datetime
        :param timestamp: str, of the format from the frmt method output
        :return: datetime
        """
        temp = timestamp
        year = int(timestamp[:timestamp.find("/")])
        temp = timestamp[timestamp.find("/")+1:]
        month = int(temp[:temp.find("/")])
        temp = temp[temp.find("/")+1:]
        day = int(temp[:temp.find(" ")])
        temp = temp[temp.find(" ")+1:]
        hour = int(temp[:temp.find(":")])
        temp = temp[temp.find(":")+1:]
        minute = int(temp[:temp.find(":")])
        temp = temp[temp.find(":")+1:]
        second = int(temp[:temp.find(":")])
        ts = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
        return ts

    def save_config(self) -> None:
        """
        Configure the save configuration settings
        :return: None
        """
        path = filedialog.asksaveasfile(mode='w', defaultextension=".csv",
                                        filetypes=[('Comma-separated Values', '*.csv'), ('All Files', '*.*')])
        # print("This is the path: " + path.name)
        if path is None:
            self.save_path = ""
        else:
            self.save_path = path.name

    def submit(self) -> None:
        """
        Submit the collected data with defaults for unedited fields
        :return: None
        """
        confirm = messagebox.askokcancel("Submit", "Are you sure you want to submit this form?", icon='question')
        # print(confirm)
        # if confirm:
            # print("It's a bool")
        # else:
            # print("It's a string")
        if confirm:
            self.write_csv()

    def write_csv(self) -> None:
        """
        Write csv file from input fields and captured time stamps
        :return: None
        """
        if self.save_path == "":
            self.save_config()
        names = [self.string_vars[x].get() for x in self.name_list]
        begin = [self.string_vars[x].get() for x in self.beg_list]
        end = [self.string_vars[x].get() for x in self.end_list]
        qual = [self.string_vars[x].get() for x in self.qual_list]
        qual2 = [self.drops["qual2_"+str(x)].get() for x in range(1,run_num+1)]
        note = [self.string_vars[x].get() for x in self.note_list]
        order = self.get_order(names, begin)
        try:
            new_file = open(self.save_path, mode='w')
            new_file.write("Substrate,PVSK Order,Pass/Fail,On,Off,Crater,Point Defect,Notes,HTL_qual,HTL_name\n")   # @TODO Not sure what to name second layer column, so named it HTL_name
            for n in range(len(names)):
                line = str(names[n]) + "," + str(order[n]) + "," + str(qual[n]) + "," + str(begin[n]) + "," + \
                       str(end[n]) + ",,," + str(note[n]) + "," + str(qual2[n]) + "," + self.drops["next_layer"].get() + "\n"
                new_file.write(line)
            new_file.close()
            messagebox.showinfo("Success!", "Your form was saved successfully!")
        except PermissionError:
            messagebox.showerror("Error!", "File permission error, try closing the file and trying again!")
            self.write_csv()

    def get_order(self, names: list, timestamps: list) -> list:  # (Note from Mark) This function is confusing and seems inefficient.
        """
        Get the corresponding index for the order of the names as they are related to the timestamps
        :param names: list, of substrate names
        :param timestamps: list, of timestamps corresponding to each substrate
        :return: list, of the order in which the substrate was coated
        """
        temp = []
        now_time = datetime.datetime.now() + datetime.timedelta(days=365)
        # print(names)
        # print(timestamps)
        for time in timestamps:
            if len(time) == 19:
                # print("Current: " + str(time))
                temp.append(datetime.datetime(year=int(time[:4]), month=int(time[5:7]), day=int(time[8:10]),
                                              hour=int(time[11:13]), minute=int(time[14:16]), second=int(time[17:])))
            else:
                temp.append(now_time)
        matrix = [[names[x], temp[x]] for x in range(len(temp))]
        # sort according to timestamp value
        matrix.sort(key=lambda x: x[1])
        order = []
        num = []
        n = 1
        for set in matrix:
            if set[1] < now_time:
                order.append(n)
            else:
                order.append("")
            number = int(set[0][set[0].find(" ") + 1:])
            num.append(number)
            n += 1
            # print(str(set[0]) + " " + str(set[1]) + " " + str(order[n-2]))
        true_order = []
        for n in range(len(order)):
            matrix[n].append(order[n])
            matrix[n].append(num[n])
        matrix.sort(key=lambda x: x[3])
        for set in matrix:
            true_order.append(set[2])
        return true_order

    def run(self) -> None:
        """
        Runs the gui
        :return: None
        """
        self.root.mainloop()

if __name__ == "__main__":
    gui = pvsk_gui()
    gui.run()
    #cProfile.run('gui.run()')
