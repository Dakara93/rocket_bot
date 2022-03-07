import asyncio
from telethon import TelegramClient, events
import sys
import tkinter as tk
import nest_asyncio
import json
from telethon.errors import SessionPasswordNeededError

import glob
import ui


api_hash = "1fea3df04d97e0c8691f37236ba3593e"
api_id = "12395584"

##### MUST BE CHANGED FOR PRODUCTION
running_dev = 0

code = 0
password = 0

if(running_dev):
    base_path = "./"
else:
    base_path = sys._MEIPASS


### --- --------------  Structural functions --------------


def quitt():
 
    ui.quit()
    glob.running = 0

def callbacks(funct):
    asyncio.create_task(funct())


async def init():
    
    glob.running = 1
    load_data()
    glob.current_name = glob.settings[0]['name']

    ui.create_window()

    glob.connected = await glob.client.is_user_authorized()
    if(glob.connected == False):
        # User is not logged in, configure the button to ask them to login
        ui.set_signed_state('Enter Phone/token:')
    else :
        ui.construct_advanced()
        ui.set_signed_state('signed_in')
        ui.menu_var.set(glob.current_name)
        show_data(glob.current_name)


#--------------- user login -------------------------

async def log_out():
    await glob.client.log_out()
    quitt()


async def sign_in():
    global code,password
    ui.set_signed_state('working')
    if await glob.client.is_user_authorized():
        ui.set_signed_state('signed_in')
        ui.construct_advanced()
        show_data(glob.current_name)
        glob.connected = True
        return

    value = ui.get_sign_value()
    if code:
        try:
            await glob.client.sign_in(code=value)
        except SessionPasswordNeededError:
            ui.set_signed_state('Password:')
            password = True
            code = None
            return
        except:
            ui.alert("Code refused.")
            ui.set_signed_state("Received code :")
        else :
            ui.set_signed_state('signed_in')
            ui.construct_advanced()
            glob.connected = True
            show_data(glob.current_name)
    
    elif ':' in value:
        try:
            await glob.client.sign_in(bot_token=value)
        except:
            ui.alert("Token refused.")
            ui.set_signed_state('Enter Phone/token:')
        else:
            ui.set_signed_state('signed_in')
            ui.construct_advanced()
            glob.connected = True
            show_data(glob.current_name) 
    
    elif password:
        try:
            await glob.client.sign_in(password=value)
        except:
            ui.alert("Password refused.")
            ui.set_signed_state('Password:')
        else:
            ui.set_signed_state('signed_in')
            ui.construct_advanced()
            glob.connected = True
            show_data(glob.current_name)
   
    else:
        try:
            code = await glob.client.send_code_request(value)
        except:
            ui.alert("Request refused.")
            ui.set_signed_state('Enter Phone/token:')
        else:
            ui.set_signed_state("Received code :")



# ----------------- Data handling -----------------------

def update_settings():

    index = next(i for i, x in enumerate(glob.settings) if x['name'] ==  glob.current_name)
    glob.settings[index].update(ui.get_settings()) 

    
    with open("./settings.json","w",encoding = 'utf-8') as settings_file:
        json.dump(glob.settings,settings_file,ensure_ascii=False)
    
    show_data( glob.current_name)


def update_patterns(cmd):

    index = next(i for i, x in enumerate(glob.settings) if x['name'] ==  glob.current_name)

    n = ui.n_pattern()
        
    if(cmd == "add"):
        glob.patterns[index]['pattern'][n] = ui.get_current_pattern()
        glob.patterns[index]['pattern'] = glob.patterns[index]['pattern'][0:n+1]+[""]+glob.patterns[index]['pattern'][n+1:]
        ui.n_pattern(n+1)
    elif(cmd == "del"):
        glob.patterns[index]['pattern'].pop(n)
        ui.n_pattern(n-1)
    elif(cmd == "inc"):
        glob.patterns[index]['pattern'][n] = ui.get_current_pattern()
        ui.n_pattern(n+1)
    elif(cmd == "dec"):
        glob.patterns[index]['pattern'][n] = ui.get_current_pattern()
        ui.n_pattern(n-1)
    elif(cmd =="save"):
        glob.patterns[index]['pattern'][n] = ui.get_current_pattern()
        save_data()
    elif(cmd == "restore"):
        load_data()

        #On full sequence
    elif(cmd == "del_seq"):
        glob.patterns.pop(index)
        glob.settings.pop(index)
        glob.current_name =glob.settings[0]['name']
        save_data()
    elif(cmd == "add_seq"):
        name = ui.get_new_name()
        glob.settings.append({"name":name,"delay":1,"iter":1,"command":"cmd","add_new":0})
        glob.patterns.append({"name":name,"pattern":[""]})
        glob.current_name = name
        save_data()
    elif(cmd == "ren_seq"):
        name = ui.get_new_name()
        glob.patterns[index]['name'] = name
        glob.settings[index]['name'] = name
        glob.current_name = name
        save_data()
    
    show_data(glob.current_name)

def save_data():

    with open("./patterns.json","w",encoding = 'utf-8') as patterns_file:
        json.dump(glob.patterns,patterns_file,ensure_ascii=False)

    with open("./settings.json","w",encoding = 'utf-8') as settings_file:
        json.dump(glob.settings,settings_file,ensure_ascii=False)

def load_data():
    with open("./settings.json","r",encoding='utf-8') as settings_file:
        glob.settings = json.load(settings_file)

    with open("./patterns.json","r",encoding='utf-8') as patterns_file:
        glob.patterns = json.load(patterns_file)


def search_json(json_object, item,value):
    dict = 0
    for dict in json_object:
        if dict[item] == value:
            return dict


# ---------------------- Display datas --------------------------------


def show_data(selected = False):
    
    if(glob.current_name != selected and type(selected) == str):
        glob.current_name = selected
        n = 0
    else:
        n = ui.n_pattern()
    names = []
    for obj in glob.settings:
        names.append(obj['name'])
    
    setting = search_json(glob.settings,"name", glob.current_name)
    pattern = search_json(glob.patterns,"name", glob.current_name)['pattern']

    patt_len = len(pattern)
    n = n%patt_len
    
    ui.menu_var.set(glob.current_name)
    ui.n_pattern(n)
    ui.display_data(setting,pattern[n],patt_len,names)
    

    
#------------ TG actions --------------------

async def print_pattern(pattern,setting,message, n,m):

    await asyncio.sleep(setting['delay'])
    if setting['add_new']:
        await glob.client.send_message(message.peer_id,pattern[n])
    else:
        await glob.client.edit_message(message.peer_id,message.id,pattern[n])
    
    n = (m+1)
    if(m<(setting['iter']*(len(pattern)-1)+(setting['iter']-1))):
        await print_pattern(pattern,setting,message,n%len(pattern),n)



async def tg_monitor(loop):

    glob.client = TelegramClient('anon', api_id, api_hash,loop=loop)
    await glob.client.connect()
    await init()
    
    @glob.client.on(events.NewMessage())
    async def normal_handler(event):
        
        setting = search_json(glob.settings,"command",event.message.message)
        if (setting and event.message.from_id.user_id == 1796705633):
            await glob.client.delete_messages(event.message.peer_id,event.message.id)
            pattern = search_json(glob.patterns,"name",setting['name'])['pattern']
            message = await glob.client.send_message(event.message.peer_id,pattern[0])
            await print_pattern(pattern,setting,message,1,1)
    
    try:
        while glob.running:
            ui.update()
            
            await asyncio.sleep(0.05)
    except KeyboardInterrupt:
        pass
    except tk.TclError as e:
        if 'application has been destroyed' not in e.args[0]:
            raise
    finally:
        await glob.client.disconnect()
    

async def main():
    global loop

    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tg_monitor(loop))


if __name__ == '__main__':
    asyncio.run(main())

    
    





 