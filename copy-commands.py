'''
copy-commands
GUI to add and copy command lines easily

'''

import os
import tkinter as tk
from tkinter import Canvas, ttk, PhotoImage, Scrollbar, StringVar, Tk, Label, Button, Entry, Frame, Text

import copy_commands_utils as cu

# MainApplication
## >> in MainApplication Frame
MT_ROW = 0 # Main title row
MT_COL = 0 # Main title column

NE_ROW = 1 # New entry row
NE_COL = 0 # New entry column

PT_ROW = 2 # Tab navigator row
PT_COL = 0 # Tab navigator column

### >> in ParentTabs
VC_ROW = 0 # View canvas row
VC_COL = 0 # View canvas column

#### >> in ViewCanvas
LL_ROW = 0 # Lines list row
LL_COL = 0 # Lines list column

SL_ROWS = 10 # Saved lines simultaneous rows
SL_COLS = 4 # Saved lines siultaneous columns


dir_name = os.path.dirname(__file__)

class MainApplication:
    def __init__(self, master):
        self.master = master
        master.title("copy-commands")
        master.geometry("850x700")

        # Main title
        self.main_title = Label(width=20, height=2, text="copy-commands", font=('Courier', 20))

        # Tab
        self.tabs = ParentTabs(self.master)

        # Canvas
        self.canvas = ViewCanvas(self.tabs)

        # Frames
        self.list_frame = LinesListFrame(self.canvas)
        self.new_entry_frame = NewEntryFrame(self.master, self.list_frame)    
        
        # Sending frames to tabs
        self.tabs.setter(self.canvas, self.list_frame)
        
        # Grid management
        self.main_title.grid(row=MT_ROW, column=MT_COL, padx=(0, 0), sticky=tk.NW)
        self.new_entry_frame.grid(row=NE_ROW, column=NE_COL, padx=(50, 0), pady=(0, 0), sticky=tk.NW)
        self.tabs.grid(row=PT_ROW, column=PT_COL, padx = (50, 0), pady= (10, 0), sticky=tk.NW)

class NewEntryFrame(Frame):
    def __init__(self, master, list_frame):
        Frame.__init__(self, master)
        self["bg"] = "#559bfa"
        self.list_frame = list_frame
        

        # Text Entries
        self.name_entry = Entry(self, width=20)
        self.name_entry.insert(0, 'Name')
        self.name_entry.bind('<FocusIn>', lambda args: self.name_entry.selection_range(0, 'end')) #TODO: print name or new Line only if empty
        self.name_entry.bind('<Return>', self.add_line)

        self.line_entry = Entry(self, width=50)
        self.line_entry.insert(0, 'New line...')
        self.line_entry.bind('<FocusIn>', lambda args: self.line_entry.selection_range(0, 'end'))
        self.line_entry.bind('<Return>', self.add_line)

        # Buttons
        self.add_button = Button(self, text="+", command=self.add_line)
        self.paste_button = Button(self, text="Paste", command=lambda: self.paste_from_clip())
        self.reset_button = Button(self, text="Reset", command=lambda: self.reset_entries())
        self.close_button = Button(self, text="Close", command=master.quit)

        # Grid
        self.name_entry.grid(row=0, column=0)
        self.line_entry.grid(row=0, column=1)
        self.add_button.grid(row=0, column=2)
        self.paste_button.grid(row=0, column=3)
        self.reset_button.grid(row=0, column=4)
        
    def add_line(self, event=None):
        com_id = cu.add_to_json(self.name_entry.get(), self.line_entry.get(), ["all"])
        line_block = SavedLineFrame(self.list_frame, self.name_entry.get(), self.line_entry.get(), com_id)
        print(self.line_entry.get())
    
    def paste_from_clip(self, event=None):
        clip = Tk()
        clip.withdraw()
        line = clip.clipboard_get()
        self.line_entry.delete('0', 'end')
        self.line_entry.insert(0, line)
        self.line_entry.icursor("end")
        clip.destroy()
    
    def reset_entries(self):
        self.line_entry.delete('0', 'end')
        self.name_entry.delete('0', 'end')

class ParentTabs(ttk.Notebook):
    def __init__(self, master):
        ttk.Notebook.__init__(self, master)
        self["height"] = 400
        self["width"] = 650
        self.grid(row=0, column=1)

    def setter(self, canvas, list_frame):
        '''
        To externally create canvas and list frame
        '''
        self.canvas = canvas
        self.list_frame = list_frame
        self.set_scrollbar()
    
    def set_scrollbar(self):
        self.vsb = Scrollbar(self.canvas, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.canvas.create_window((0,0), window=self.list_frame, anchor="nw")

        # Binding
        self.list_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Grid management
        self.vsb.grid(row=3, column=3, sticky=tk.NE)
        self.canvas.grid(row=VC_ROW, column=VC_COL, sticky=tk.NW)

        # Add tab
        self.add(self.canvas, text="alltest")
        
        
    def on_frame_configure(self, event):
        bbox = self.canvas.bbox(tk.ALL)
        w, h = bbox[2]-bbox[1], bbox[3]-bbox[1]
        dw, dh = int((w/6) * 4), int((h/10) * 3)
        self.canvas.configure(scrollregion=bbox)
    
    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(-1 * int((event.delta / 120)), "units")





        # THIS KINDA WORKS
        # self.tabs = []
        # self.tabs.append(LinesListFrame(master))
        # for tab in self.tabs:
        #     self.add(tab, text="test")
        
        # self.grid(row=0, column=1)

class ViewCanvas(Canvas):
    '''
    MainApp -> ParentTabs -> ViewCanvas\n
    Canvas which holds LinesListFrame and is scrollable
    '''
    def __init__(self, parent_tab):
        Canvas.__init__(self, parent_tab)
        # Do not put hard-coded height and width, otherwise the scrolling will
        # not work properly and will stick to these parameters
        self["borderwidth"] = 0
        self["bg"] = "orange"

class LinesListFrame(Frame):
    '''
    MainApp -> ParentTabs -> ViewCanvas -> LinesListFrame\n
    Frame that holds several SavedLineFrame
    '''
    def __init__(self, canvas_frame):
        Frame.__init__(self, canvas_frame)
        self["bg"] = "red"

        self.canvas_frame = canvas_frame

        self.commands_dict = cu.recover_json() # dictionary of all saved lines/commands
        self.initialize_saved_lines()

    def initialize_saved_lines(self):
        for com_id, attributes in self.commands_dict.items():
            line_block = SavedLineFrame(self, attributes["name"], attributes["line"], com_id)

class SavedLineFrame(Frame):
    def __init__(self, list_frame, name, line, com_id):
        Frame.__init__(self, list_frame)
        self["bg"] = "#00c450"

        self.com_id = com_id

        self.name = StringVar()
        self.line = StringVar()
        self.name.set(name)
        self.line.set(line)

        self.saved_name_label = Label(self, textvariable=self.name, width=20)
        self.saved_line_label = Label(self, textvariable=self.line, width=50)

        self.saved_name_label.bind('<Double-Button-1>', lambda event: self.edit_label(com_id=self.com_id, field='name'))
        self.saved_line_label.bind('<Double-Button-1>', lambda event: self.edit_label(com_id=self.com_id, field='line'))


        sub = 20 #for subsampling i.e. resizing
        self.copy_icon = PhotoImage(file=os.path.join(dir_name, "copy_icon.png")).subsample(sub) #note: PhotoImage object have to be an attribute otherwise they're removed
        self.copy_button = Button(self, text="COPY", image=self.copy_icon, command=lambda: self.copy_line(self.line.get())) #TODO: change THAT
        self.delete_icon = PhotoImage(file=os.path.join(dir_name, "delete_icon.png")).subsample(sub)
        self.delete_button = Button(self, text="DELETE", image=self.delete_icon, command=self.delete_line)
        
        # Grid management
        self.grid(sticky="news")
        self.saved_name_label.grid(row=0, column=0)
        self.saved_line_label.grid(row=0, column=1)
        self.copy_button.grid(row=0, column=2)
        self.delete_button.grid(row=0, column=3)

        # Adding widget to the list of parent ListLinesFrame
        #list_frame.lines_list.append(self)


    def edit_label(self, com_id, field):
        '''
        Changes label of an already saved line
        
        Inputs:
        - field: widget type, either a name or line entry
        '''
        if field == 'name':
            var = self.name
            width = 20
            column = 0
        elif field == 'line':
            var = self.line
            width = 50
            column = 1
        else:
            print("Error", field)
        
        # Creation of an Entry widget on top of the label one
        self.over_entry = Entry(self, width=width, textvariable=var) # StringVar will be updated automatically
        self.over_entry.icursor("end") # put cursor at the end
        self.over_entry.selection_range(0, 'end')
        self.over_entry.grid(row=0, column=column)
        self.over_entry.focus() # put cursor focus on the entry
        self.over_entry.bind('<Return>', lambda event: save_destroy())

        def save_destroy(event=None):
            '''
            Intermediate function for saving edited line and destroy over_entry widget
            '''
            cu.edit_saved_json(com_id, field, self.over_entry.get())
            self.over_entry.destroy()


        
    def copy_line(self, text):
        clip = Tk()
        clip.withdraw()
        clip.clipboard_clear()
        clip.clipboard_append(text)
        clip.destroy()
        print("copied")

    def delete_line(self):
        self.grid_forget()
        self.destroy() # (remoove if I want to be able to undo the deletion)
        cu.delete_from_json(self.com_id)
        
        
    
    
if __name__=="__main__":
    root = Tk()
    main = MainApplication(root)
    root.mainloop()