from PIL import ImageGrab
import requests
from io import BytesIO
from tkinter import Tk, Button, Label, Entry, Frame
import threading
from datetime import datetime
import time
import webbrowser 

running = False

def start_stop():
    global running
    if running:
        running = False
        button.config(text="START")
    else:
        running = True
        button.config(text="STOP")
        thread = threading.Thread(target=run_scheduler)
        thread.start()

def run_scheduler():
    while running:
        capture_and_upload()
        time.sleep(250)

def capture_and_upload():
    nick = nick_entry.get()
    password = password_entry.get()
    screenshot = ImageGrab.grab(all_screens=True)
    buffer = BytesIO()
    screenshot.save(buffer, format="WEBP", quality=80)
    buffer.seek(0)
    files = {'image': ('screenshot.webp', buffer, 'image/webp')}
    data = {'nick': nick}
    response = requests.post('https://clan.varmi.cz/imgs/upload', files=files, data=data)

    if response.status_code == 200:
        response_data = response.json()
        image_url = response_data.get('url')
        update_gui(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), image_url)

        status_data = {'url': image_url, 'nick': nick, 'password': password}
        status_response = requests.post('https://clan.varmi.cz/api/statusImg', json=status_data)
        print(f'Status of status update: {status_response.status_code}, Response: {status_response.text}')
        if status_response.status_code == 200:
            status_text.config(text="Status:\n✅ V pořádku!")
        elif status_response.status_code == 401: 
            status_text.config(text="Status:\n❌ Špatné heslo nebo nick!")
        else:
            print(f'Status: {response.status_code}, Response: {response.text}')
    else:
        print(f'Status: {response.status_code}, Response: {response.text}')

def open_link(url):
    webbrowser.open(url)

def update_gui(time_str, url):
    time_label.config(text=f"Čas pořízení:\n{time_str}")
    link_label.config(text="Screen:\n[Klik pro zobrazení]")
    link_label.bind("<Button-1>", lambda e: open_link(url)) 
    root.update_idletasks()

root = Tk()
root.title("Status Checker")
root.geometry('280x300')

root.configure(bg='#333333')

nick_label = Label(root, text="Nick:", bg='#333333', fg='white')
nick_label.pack()
nick_entry = Entry(root, bd=2, relief='sunken')
nick_entry.pack(pady=5)

password_label = Label(root, text="Heslo:", bg='#333333', fg='white')
password_label.pack()
password_entry = Entry(root, show='*', bd=2, relief='sunken')
password_entry.pack(pady=5)

status_text = Label(root, text="Status:\nČekání", font=("Helvetica", 11, "bold"), bg='#333333', fg='white')
status_text.pack(pady=(5, 0))
link_label = Label(root, text="Screen:\nNone", font=("Helvetica", 11, "bold"), bg='#333333', fg='white')
link_label.pack(pady=(5, 0))
time_label = Label(root, text="Čas pořízení: -", font=("Helvetica", 11, "bold"), bg='#333333', fg='white')
time_label.pack(pady=(5, 0))

button = Button(root, text="START", command=start_stop, 
                bg='#556677', fg='white', 
                font=('Helvetica', 10, 'bold'), 
                padx=5, pady=5, 
                borderwidth=2, relief="ridge")
button.pack(pady=10, anchor='center')  

root.mainloop()
