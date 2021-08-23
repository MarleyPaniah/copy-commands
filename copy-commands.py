'''
copy-commands
GUI to add and copy command lines easily

'''

import os
import platform
import tkinter as tk
from tkinter import Canvas, ttk, PhotoImage, Scrollbar, StringVar, Tk, Label, Button, Entry, Frame, Text

import copy_commands_utils as cu

# MainApplication
## >> in MainApplication Frame
MT_ROW = 0 # Main title row
MT_COL = 0 # Main title column

NE_ROW = 1 # New entry row
NE_COL = 0 # New entry column

TC_ROW = 2 # Tab navigator row
TC_COL = 0 # Tab navigator column

### >> in TabControl
VC_ROW = 0 # View canvas row
VC_COL = 0 # View canvas column

#### >> in ViewCanvas
LL_ROW = 0 # Lines list row
LL_COL = 0 # Lines list column

##### >> in LinesListFrame
SB_ROW = 0 # Scrollbar row
SB_COL = 1 # Scrollbar column

# SL_ROWS_DISP = 10 # Saved lines rows simultaneously displayed
# SL_COLS_DISP = 4 # Saved lines columns simultaneously displayed


dir_name = os.path.dirname(__file__)

class MainApplication:
    def __init__(self, master):
        self.master = master
        master.title("copy-commands")
        master.geometry("850x700")

        # Main title
        self.main_title = Label(width=20, height=2, text="copy-commands", font=('Courier', 20))

        # Tab
        self.tabs = TabControl(self.master)
        #TODO: move the canvas and list frame logic into the tabs themselves
        # Watch out for newentryframe, that needs to be passed a list_frame,
        # which can be retrieved by accessing the selected tab

        self.new_entry_frame = NewEntryFrame(self.master, self.tabs)    

        # Grid management
        self.main_title.grid(row=MT_ROW, column=MT_COL, padx=(0, 0), sticky=tk.NW)
        self.new_entry_frame.grid(row=NE_ROW, column=NE_COL, padx=(50, 0), pady=(0, 0), sticky=tk.NW)
        self.tabs.grid(row=TC_ROW, column=TC_COL, padx = (50, 0), pady= (10, 0), sticky=tk.NW)

class NewEntryFrame(Frame):
    def __init__(self, master, tab_control):
        Frame.__init__(self, master)
        self["bg"] = "#559bfa"
        self.tab_control = tab_control
        

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
        #self.close_button = Button(self, text="Close", command=master.quit)

        # Grid
        self.name_entry.grid(row=0, column=0)
        self.line_entry.grid(row=0, column=1)
        self.add_button.grid(row=0, column=2)
        self.paste_button.grid(row=0, column=3)
        self.reset_button.grid(row=0, column=4)
        
    def add_line(self, event=None):
        com_id = cu.add_to_json(self.name_entry.get(), self.line_entry.get(), ["all"])
        list_frame = self.tab_control.get_current_list_frame()
        line_block = SavedLineFrame(list_frame, com_id, self.name_entry.get(), self.line_entry.get())
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

class TabControl(ttk.Notebook):
    def __init__(self, master):
        ttk.Notebook.__init__(self, master)
        self["height"] = 450
        self["width"] = 650

        self.widgets = {}
        self.i = 0

        self.init_default_tabs()

        # Grid management
        self.grid(row=0, column=1)

    def create_tab(self, tab_name="new_tab", add_button=False):
        canvas = ViewCanvas(self)
        list_frame = LinesListFrame(canvas)
        if not add_button:
            print("heh")
            scrollbar = self.set_scrollbar(canvas, list_frame) #TODO: scrollbar referenced before assignment, so change how this tab is created
        else: #+ scrollbar not working properly and bounded to the whole frame. Add print on the "on enter" and "on leave"
            scrollbar = "NO_SCROLLBAR"
        
        self.widgets[tab_name] = { 
            #TODO: utiliser l'id plutôt pour changer facilement le texte
                "canvas": canvas, 
                "list_frame": list_frame, 
                "scrollbar": scrollbar
            }

        self.add(canvas, text=tab_name)

        print(self.tabs())

    def get_current_list_frame(self):
        tab_text = self.tab(self.select(), option="text")
        return self.widgets[tab_text]["list_frame"]
    
    def set_scrollbar(self, canvas, list_frame):
        vsb = Scrollbar(canvas, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.create_window((0,0), window=list_frame, anchor="nw")

        # Scrollbar positioning
        canvas.columnconfigure(0, weight=1)
        canvas.rowconfigure(0, weight=1)    

        # Binding #TODO
        list_frame.bind("<Configure>", self.on_frame_configure)
        list_frame.bind('<Enter>', self.on_enter)
        list_frame.bind('<Leave>', self.on_leave)

        self.bind('<<NotebookTabChanged>>', self.on_tab_change)


        # Grid management
        ## 
        # For a strange reason, griding the list_frame and canvas breaks the scrolling
        # event if they properly display
        # Maybe because grid fixes the position
        #
        #list_frame.grid(row=0, column=0)
        #canvas.grid(row=VC_ROW, column=VC_COL)
        ##
        vsb.grid(row=SB_ROW, column=SB_COL, sticky=tk.NSEW) #note: needs nsew to fill
        return vsb
        
    
    def init_default_tabs(self):
        '''
        Adding default tabs to TabControl
        '''
        self.create_tab(tab_name="all")
        self.create_tab(tab_name="+", add_button=True) # For the "+"/"Add new tab" button
        #TODO: le faire en fonction des catégories enregistrées dans le json

    def on_tab_change(self, event):
        tab_id = self.select()
        tab_text = self.tab(self.select(), option="text")
        if tab_text == "+":
            self.create_tab()
            self.forget(tab_id)
            self.create_tab(tab_name="+", add_button=True)
        else:
            print("NOT +")
            pass
        
        
    def on_frame_configure(self, event):
        '''
        Resets the scroll region to encompass the inner frame
        '''
        current_canvas = self.widgets[self.tab(self.select(), option="text")]["canvas"]
        current_canvas.configure(scrollregion=current_canvas.bbox(tk.ALL))

    def on_mouse_wheel(self, event):
        current_canvas = self.widgets[self.tab(self.select(), option="text")]["canvas"]
        if platform.system() == "Windows":
            current_canvas.yviews_croll(int(-1* (event.delta/120)), "units")
        else:
            if event.num == 4:
                    current_canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                current_canvas.yview_scroll( 1, "units" )


    def on_enter(self, event):
        current_canvas = self.widgets[self.tab(self.select(), option="text")]["canvas"]
        if platform.system() == "Linux":
            current_canvas.bind_all("<Button-4>", self.on_mouse_wheel)
            current_canvas.bind_all("<Button-5>", self.on_mouse_wheel)
        else:
            current_canvas.bind_all('<MouseWheel>', self.on_mouse_wheel)
    
    def on_leave(self, event):
        current_canvas = self.widgets[self.tab(self.select(), option="text")]["canvas"]
        if platform.system() == 'Linux':
            current_canvas.unbind_all('<Button-4')
            current_canvas.unbind_all('<Button-5')
        else:
            current_canvas.unbind_all('<MouseWheel>')
    


class ViewCanvas(Canvas):
    '''
    MainApp -> TabControl -> ViewCanvas\n
    Canvas which holds LinesListFrame and is scrollable
    '''
    def __init__(self, tab_control):
        Canvas.__init__(self, tab_control)
        # Do not put hard-coded height and width, otherwise the scrolling will
        # not work properly and will stick to these parameters
        # self["height"] = 300
        # self["width"] = 200
        self["borderwidth"] = 0
        self["bg"] = "orange"


class LinesListFrame(Frame):
    '''
    MainApp -> TabControl -> ViewCanvas -> LinesListFrame\n
    Frame that holds several SavedLineFrame
    '''
    def __init__(self, canvas_frame):
        Frame.__init__(self, canvas_frame)
        self["bg"] = "red"

        self.canvas_frame = canvas_frame

        self.commands_dict = cu.recover_json() # dictionary of all saved lines/commands
        # Adapter pour que ça n'affiche que quand ça all
        self.initialize_saved_lines() # TODO: this takes too much time

        # Since its loading takes time, it is to prevent that
        self.update_idletasks()

    def initialize_saved_lines(self):
        for com_id, attributes in self.commands_dict.items():
            saved_line = SavedLineFrame(self, com_id, attributes["name"], attributes["line"]) #TODO: adapt according to the frame

class SavedLineFrame(Frame):
    def __init__(self, list_frame, com_id, name, line):
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
        self.grid()
        self.saved_name_label.grid(row=0, column=0)
        self.saved_line_label.grid(row=0, column=1)
        self.copy_button.grid(row=0, column=2)
        self.delete_button.grid(row=0, column=3)


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

    #TODO: refaire la strcture du json
    #TODO: faire un refresh dans all en cas de suppression ailleurs