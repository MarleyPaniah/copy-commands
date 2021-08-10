'''
copy-commands
GUI to add and copy command lines easily

'''

import os
from tkinter import Canvas, ttk, PhotoImage, Scrollbar, StringVar, Tk, Label, Button, Entry, Frame, Text

import copy_commands_utils as cu


dir_name = os.path.dirname(__file__)

class MainApplication:
    def __init__(self, master):
        self.master = master
        master.title("copy-commands")
        master.geometry("1100x500")

        self.main_title = Label(width=20, height=2, text="copy-commands", font=('Courier', 20))

        # Frame
        self.new_entry_frame = NewEntryFrame(self.master)

        # Tab
        self.tabs = ParentTab(self.master)
        
        # Grid
        self.main_title.grid(row=0, column=1)
        self.new_entry_frame.grid(row=0, column=0, padx=(20, 0))
        self.tabs.grid(row=1, column=0)


class NewEntryFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self["bg"] = "#559bfa"
        

        self.list_frame = LinesListFrame(self.master)

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

class ParentTab(ttk.Notebook):
    def __init__(self, master):
        ttk.Notebook.__init__(self, master)
        # THIS KINDA WORKS
        # self.tabs = []
        # self.tabs.append(LinesListFrame(master))
        # for tab in self.tabs:
        #     self.add(tab, text="test")
        
        # self.grid(row=0, column=1)


class LinesListFrame(Canvas):
    def __init__(self, master):
        Canvas.__init__(self, master)
        self["height"] = 450
        self["width"] = 700
        #self["bg"] = "red"

        self.commands_dict = cu.recover_json() # dictionary
        
        self.initialize_saved_lines()

        # self.sb = Scrollbar(self, orient="vertical")
        # self.sb.grid(row=0, column=1)
        # self.config(yscrollcommand=self.sb.set)
        # self.sb.config(command=self.xview)
        # self.sb.config(scrollregion=self.bbox("all"))

        self.grid_propagate(False)
        self.grid(row=1, column=0, sticky="nw", padx=(20, 0))

    def initialize_saved_lines(self):
        for com_id, attributes in self.commands_dict.items():
            line_block = SavedLineFrame(self, attributes["name"], attributes["line"], com_id)

class SavedLineFrame(Frame):
    def __init__(self, list_frame, name, line, com_id):
        Frame.__init__(self, list_frame)
        self["height"] = 100
        self["width"] = 300
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
        
        self.grid()
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
            Interediate function for saving edited line and destroy over_entry widget
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