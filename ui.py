import tkinter as tk
import os,sys
from tkinter import INSERT, N, OptionMenu,IntVar,_setit,StringVar,messagebox,DISABLED,NORMAL
from pystray import MenuItem
import pystray
import glob
from PIL import Image

from main import base_path, callbacks, quitt,sign_in,log_out,show_data,update_patterns,update_settings

TITLE = 'Rocket bot'
SIZE = '482x300'
root = tk.Tk()


n = 0

icon = None
radio_var = menu_var = None


def update():
    root.update()

def create_window():
    
    global root, icon
    root.iconbitmap(os.path.join(base_path,"icon.ico"))
    root.title(TITLE)
    root.geometry(SIZE)
    root.protocol("WM_DELETE_WINDOW",  quitt)
    


    # Signing in row; the entry supports phone and bot token
    root.sign_in_label = tk.Label(root, text='Loading...',width="16")
    root.sign_in_label.grid(row=3, column=2,stick=tk.W,pady=(90),padx=(80,0))
    root.sign_in_entry = tk.Entry(root)
    root.sign_in_entry.grid(row=3, column=3, sticky=tk.EW)
    root.sign_in_button = tk.Button(root, text='...',
                                            command= lambda: callbacks( sign_in))
    root.sign_in_button.grid(row=3, column=4,sticky=tk.EW,padx =(3,1))
    

    image = Image.open(os.path.join( base_path, "icon.ico"))
    menu = (MenuItem('Close', lambda:os._exit(1)),MenuItem("Show",show_window))
    icon = pystray.Icon('name',image,"Tg bot",menu)       

def alert(message):
    messagebox.showinfo('', message,master=root)

def cursor_pos(event):
    
    try:
        if(root.focus_get().winfo_name()=="!text"):
            pos = root.pattern_entry.index(INSERT)
            line = pos[0]
            col = pos[2:]
            root.pos_label.configure(text="("+line+","+col+")")
            
    except:
        return

root.bind('<Key>',cursor_pos)
root.bind("<Button-1>", cursor_pos)

def hide_window():
    root.withdraw()
    icon.run_detached()
    

def show_window():
    os.execl(sys.executable, sys.executable, *sys.argv)

def quit():
    root.destroy()

def n_pattern(i=False):
    global n
    if(type(i)==int):
         n = i
    else:
        return n

def set_signed_state(state):

    if state == 'signed_in':
        root.sign_in_label.configure(text='Already signed in.')
        root.sign_in_label.grid_forget()
        root.sign_in_label.grid(row=0, columnspan=2,stick=tk.W)
        root.sign_in_entry.configure(state=tk.NORMAL)
        root.sign_in_entry.delete(0, tk.END)
        root.sign_in_entry.grid_remove()
        root.sign_in_entry.configure(state=tk.DISABLED)
        root.sign_in_button.configure(text='Log out',command = lambda: callbacks( log_out))
        root.sign_in_button.grid(row=0, column=4,pady =(1,0),sticky=tk.EW)
        root.hide_button = tk.Button(root, text='Hide window',
                                            command= hide_window)
        root.hide_button.grid(row=0, column=5,pady=(1,0)) 
    
    elif state == 'working':
        root.sign_in_label.configure(text='Working...')
        root.sign_in_entry.configure(state=tk.DISABLED)
    
    else:
        root.sign_in_button.configure(text='Sign in')
        root.sign_in_label.configure(text=state)
        root.sign_in_entry.configure(state=tk.NORMAL)
        root.sign_in_entry.delete(0, tk.END)
        root.sign_in_entry.focus()


def get_sign_value():
    return root.sign_in_entry.get().strip()


def construct_advanced():
    
    global radio_var, menu_var

    radio_var = IntVar()
    radio_var.set(0)
    menu_var = StringVar()
    menu_var.set(0)

    vars = ["Loading"]

    #Upper options
    root.dropdown = OptionMenu(root,menu_var,*vars,command= show_data)
    root.dropdown.config(width=18)
    root.dropdown.grid(row=1,columnspan = 2, padx=(1,1))
    root.button_del = tk.Button(root, text='Delete',
                                            command=lambda: update_patterns('del_seq'))
    root.button_del.grid(row=1, column=2,sticky=tk.EW,padx = (0,1))
    root.button_add_seq = tk.Button(root, text='Rename',
                                            command=lambda: update_patterns('ren_seq'))
    root.button_add_seq.grid(row=1, column=5,sticky=tk.EW)
    root.button_add_seq = tk.Button(root, text='Create new',
                                            command=lambda: update_patterns('add_seq'))
    root.button_add_seq.grid(row=1, column=4,sticky=tk.EW,padx=(2,1))
    root.name_entry_seq = tk.Entry(root,width=10)
    root.name_entry_seq.grid(row=1, column=3, sticky=tk.EW)
    root.name_entry_seq.insert(0,"Name")

    #Settings part

    root.speed_label = tk.Label(root, text='Command, delay, iter:')
    root.speed_label.grid(row=2, columnspan=2)
    root.speed_entry = tk.Entry(root,width=6)
    root.speed_entry.grid(row=2, column=3, sticky=tk.EW)
    root.command_entry = tk.Entry(root,width=6)
    root.command_entry.grid(row=2, column=2, sticky=tk.EW)
    root.iter_entry = tk.Entry(root,width=4)
    root.iter_entry.grid(row=2, column=4, sticky=tk.EW,padx = (0,1))
    root.settings_button = tk.Button(root, text='Set',
                                            command= update_settings,width = 10)
    root.settings_button.grid(row=2, column=5,sticky=tk.EW)

    root.radio_label = tk.Label(root, text='Post method:')
    root.radio_label.grid(row=3, column=2, sticky=tk.EW)
    root.radio_edit = tk.Radiobutton(root, text="Edit", variable = radio_var,value=0,
                  command= update_settings)
    root.radio_edit.grid(row=3, column=3, sticky=tk.EW)
    root.radio_new = tk.Radiobutton(root, text="New", variable = radio_var, value=1,
                  command= update_settings)
    root.radio_new.grid(row=3, column=4, sticky=tk.EW)

    #Pattern part

    root.pattern_label = tk.Label(root, text='Pattern : / ')
    root.pattern_label.grid(row=3, column=0, sticky=tk.W,padx=(5,0))
    root.pattern_entry = tk.Text(root,width=18,height=10)
    root.pattern_entry.grid(row=4,rowspan=2, columnspan=2)
    
    root.button_minus = tk.Button(root, text='<--',
                                            command=lambda: update_patterns('dec'))
    root.button_minus.grid(row=6, column=0)
    root.button_plus = tk.Button(root, text='-->',
                                            command=lambda: update_patterns('inc'))
    root.button_plus.grid(row=6, column=1)
    root.button_add = tk.Button(root, text='Add pattern',
                                            command=lambda: update_patterns('add'))
    root.button_add.grid(row=4, column=2)
    root.button_del = tk.Button(root, text='Delete current',
                                            command=lambda: update_patterns('del'))
    root.button_del.grid(row=4, column=3)
    root.button_save = tk.Button(root, text='Save changes',
                                            command=lambda: update_patterns('save'))
    root.button_save.grid(row=4, column=4)
    root.button_save = tk.Button(root, text='Restore',
                                            command=lambda: update_patterns('restore'))
    root.button_save.grid(row=4, column=5,sticky=tk.EW)

    root.speed_label = tk.Label(root, text='Insert space :')
    root.speed_label.grid(row=5, column=2)

    root.button_thin = tk.Button(root, text='Thin',
                                            command=lambda: insert_space(chr(32)))
    #root.button_thin.grid(row=5, column=3,sticky=tk.EW)
    root.button_small = tk.Button(root, text='Small',
                                            command=lambda: insert_space(chr(5760)))
    #root.button_small.grid(row=5, column=4,sticky=tk.EW)
    root.button_big = tk.Button(root, text='Big',
                                            command=lambda: insert_space("ㅤ"))
    root.button_big.grid(row=5, column=3,sticky=tk.EW)

    root.pos_label = tk.Label(root,text="",width =6)
    root.pos_label.grid(row=3, column=1,sticky=tk.E)


def insert_space(char):

    root.pattern_entry.insert(tk.INSERT,char)
    cursor_pos(1)

def get_settings():

    temp = {}

    temp['delay'] = float(root.speed_entry.get().strip())
    temp['command'] = root.command_entry.get().strip()
    temp['iter'] = int(root.iter_entry.get().strip())
    temp['add_new'] = radio_var.get()


    return temp

def get_new_name():

    return root.name_entry_seq.get().strip()

def get_current_pattern():

    return root.pattern_entry.get("1.0","end").strip()


def display_data(setting,pattern,patt_len,names):
    
    radio_var.set(setting['add_new'])
   
    root.dropdown['menu'].delete(0,"end")
    for name in names :
        root.dropdown['menu'].add_command(label = name, command=_setit(menu_var, name, show_data))


    root.name_entry_seq.delete(0,"end")
    root.name_entry_seq.insert(0,"Name")

    root.speed_entry.delete(0,"end")
    root.command_entry.delete(0,"end")
    root.iter_entry.delete(0,"end")

    root.speed_entry.insert(0,str(setting['delay']))
    root.command_entry.insert(0,setting['command'])
    root.iter_entry.insert(0,str(setting['iter']))

    root.pattern_label.configure(text='Pattern :'+str(n+1)+"/"+str(patt_len))

    root.pattern_entry.delete("1.0","end")
    root.pattern_entry.insert('1.0',pattern)

    if(patt_len ==1):
        root.button_del.configure(state = DISABLED)
    else:
        root.button_del.configure(state=NORMAL)

    cursor_pos(1)