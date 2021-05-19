import tkinter
from tkinter import *
from tkinter.ttk import *
from PIL  import Image, ImageTk
from threading import Thread
from pytube import YouTube, Playlist
import tkinter.filedialog
import subprocess
import os
from urllib import request, error
import io
from tkinter import messagebox

#  variable to set the program's thumbnail
def image(smp):
    image_miniature = tkinter.PhotoImage(file="red.png")
    image_miniature = image_miniature.subsample(smp, smp)
    return image_miniature

# verification anti-spam and principal function calling
def download():
    global actived
    lblState.configure(text="", foreground = "black")
    if actived == False:
        actived = True
        start_dowloading()
    else:
        pass

#Trys to get the playlist
def start_dowloading():
    global actived
    try:
        if Playlist(url=link_input.get()).video_urls != []:
            Thread(target=playlist_download, args=(Playlist(url=link_input.get()),)).start()
        else:
            actived = False
            lblState.configure(text="Please enter a correct link", foreground = "red")
    except KeyError:
        actived = False
        lblState.configure(text='Please enter a correct link', foreground = "red")

#After the verification of the existence of the playlist, download starting
def playlist_download(p):
    global actived
    lblState.configure(text="")
    #asking the path wanted by the user for downloading the playlist
    path = tkinter.filedialog.askdirectory()
    #customization of the path with the playlist title
    path+="/"+p.title+"/"
    #window adjustement for download videos
    dl_btn.configure(state="disabled")
    mp3_checkbox.configure(state="disabled")
    link_input.configure(state="disabled")
    root.minsize(height=240, width=480)
    root.maxsize(height=240, width=480)
    k=1
    #verification if the file path already exist, and adjusting it if necessary
    if os.path.isdir(path):
        continue_searching = True
        while continue_searching == True:
            if os.path.isdir(path):
                path2 = path.rsplit(p.title,1)[0]+p.title+" ("+str(k)+")"
                path = path2
                k+=1
            else:
                continue_searching = False
    i=0
    #calling the function that will download the videos of the playlist one by one
    for url in p.video_urls:
        i+=1
        yt = YouTube(url)
        #registering of functions which will serve to display the progression of the downloading
        yt.register_on_progress_callback(progress)
        yt.register_on_complete_callback(complete)
        try:
            video_download(yt, path, i)
        except Exception as e:
            lblState.configure(text=e)
            video_download(yt, path, i)
    #adjustement of the window once the playlist is downloaded
    label_percent.configure(text="Downloaded")
    messagebox.showinfo("info", "playlist downloaded")
    dl_btn.configure(state="normal")
    mp3_checkbox.configure(state="normal")
    link_input.configure(state="normal")
    root.minsize(height=62, width=480)
    root.maxsize(height=62, width=480)
    lblState.configure(text="")
    link_input.delete(0, END)
    actived = False

#function that download the videos
def video_download(yt, path, i):
    try:
        #setting design of the video downoading
        lblState.configure(text="Downloading "+yt.title)
        image_label.configure(image = set_thumbnail(yt.thumbnail_url))
        bar.configure(value=0)
        bar.place(x=70, y=200)
        label_percent.configure(text="Getting Video...")
        title = set_title(yt.title)
        #verifying if the user checked the "Audio only" checkbox and downloading the video in function 
        if is_mp3.get():
            path = yt.streams.filter(only_audio=True, file_extension="mp4").first().download(output_path=path, filename=title, filename_prefix=str(i)+"_")
        else:
            yt.streams.filter(file_extension="mp4").get_highest_resolution().download(output_path=path, filename=title)
    except (error.HTTPError, KeyError):
        lblState.configure(text="Failed to get video. Retrying...")
        video_download(yt,path,i)

# function that will display to the user the downloading progression
def progress(stream, chunk, bytes_remaining):
    current = ((stream.filesize - bytes_remaining) / stream.filesize)
    progress = int(50 * current)
    pourcent = str(progress * 2)
    bar["value"] = pourcent
    texte = str(pourcent) + " %"
    label_percent.configure(text=texte)

#function which displays that the video is downloaded and convert it if necessary
def complete(stream, file_path):
    label_percent.configure(text="Downloading...")
    if is_mp3.get():
        Thread(target=convert, args=(file_path,)).start()

#function to make the video title readable by the explorer.
def set_title(s):
    s=s.replace(" ","_")
    s=s.replace(":","")
    s=s.replace("/","")
    s=s.replace("\\","")
    s=s.replace("|","")
    s=s.replace("?","")
    s=s.replace("*","")
    s=s.replace("<","")
    s=s.replace(">","")
    s=s.replace('"', "")
    return s

#conversion of the file which need to be
def convert(path):
    if os.path.isfile(path):
        out_path = path.rsplit(".", 1)
        out_path = out_path[0]+".wav"
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(["ffmpeg", "-y","-i", path, out_path], stderr=subprocess.STDOUT, startupinfo=si)
        os.remove(path)

#function called to display the video thumbnail to the user
def set_thumbnail(url):
    raw_data = ""
    try:
        raw_data = request.urlopen(url).read()
    except:
        try:
            raw_data = request.urlopen(url).read()
        except error.HTTPError:
            set_thumbnail(url)
    im = Image.open(io.BytesIO(raw_data))
    im = im.resize((231, 130), Image.ANTIALIAS)
    imagesagrandmere = ImageTk.PhotoImage(im)
    image_label.configure(image=imagesagrandmere)
    image_label.image = imagesagrandmere

#settings of the window
global actived
actived = False
root = tkinter.Tk()
root.minsize(height=62, width=480)
root.maxsize(height=62, width=480)
link_input = tkinter.Entry(root, disabledbackground="#E3E3E3", disabledforeground="grey", insertwidth=1, width=40)
link_input.place(x=70, y=25)
label_higher = tkinter.Label(root, text="Paste down there the link of the playlist ↓")
label_higher.place(x=80)
is_mp3 = tkinter.BooleanVar(root)
mp3_checkbox = tkinter.Checkbutton(root, text="Audio Only", variable=is_mp3)
mp3_checkbox.place(x=390, y=23)
dl_btn = tkinter.Button(root, text="Download", bd=0, relief="groove", compound=tkinter.CENTER, fg="black",
                        activeforeground="pink")
img = image(6)
dl_btn.config(image=img, command=download)
dl_btn.place(x=325, y=22)
alert_label = Label(root, foreground="red", background="#f0f0f0", text="test")
alert_label.place_forget()
s = Style()
s.theme_use('default')
s.configure("TProgressbar", foreground='red', background='red', thickness=5)
bar = Progressbar(root, orient=HORIZONTAL, length=230, style="TProgressbar", mode="determinate")
bar.place_forget()
label_percent = Label(background="#f0f0f0", text="")
label_percent.place(x=300, y=195)
lblState = tkinter.Label(text="")
lblState.place(x=67, y=45)
root.wm_iconbitmap('images.ico')
root.wm_title("Cold Downloader")
image_label = Label(background="#f0f0f0")
image_label.place(x=67, y=65)
root.mainloop()
