import PySimpleGUI as sg
from PIL import Image, ImageTk
import requests
import os
import time
import header
import http.client

# change global http variable to prevent HTTPException('got more than 100 headers')
http.client._MAXHEADERS = 1000

# create temp folder if it doesnt exist, and clear temp folder
dir = os.path.dirname(os.path.abspath(__file__))
try:
    os.mkdir(dir + '\\temp')
except:
    print("temp folder already exists")
    pass
# if temp folder is not empty, clear it out
if len(os.listdir(dir + '\\temp')) != 0:
    for f in os.listdir(dir + '\\temp'):
        os.remove(os.path.join(dir + '\\temp', f))

# setting visual style of GUI
sg.ChangeLookAndFeel("TealMono")

# list that stores the paths of locally saved images
# used to delete images when program is exited
image_paths = []
image_paths_master = []
imagewidth = 150

# gui layout code
layout = [
    [sg.Text("Enter your image search query", font = ('Helvetica', 16, 'bold'))],
    [sg.InputText(key="-QUERY-", size=(50), font=("Helvetica", 16)), sg.Button("Search")],
    [sg.Column([[sg.Image(key=f"-IMAGE0-")], [sg.Checkbox('Select', key='-CHECKBOX0-')]], element_justification='c'),
     sg.Column([[sg.Image(key=f"-IMAGE1-")], [sg.Checkbox('Select', key='-CHECKBOX1-')]], element_justification='c'),
     sg.Column([[sg.Image(key=f"-IMAGE2-")], [sg.Checkbox('Select', key='-CHECKBOX2-')]], element_justification='c'),
     sg.Column([[sg.Image(key=f"-IMAGE3-")], [sg.Checkbox('Select', key='-CHECKBOX3-')]], element_justification='c'),
     sg.Column([[sg.Image(key=f"-IMAGE4-")], [sg.Checkbox('Select', key='-CHECKBOX4-')]], element_justification='c')    
    ],
    [sg.Button("Generate ASCII Art")],
    [sg.Text("", font=("Helvetica", 11), text_color='red', key="-SUCCESS-")],
    [sg.Text("Enter desired width of ASCII art (default 150)", font=("Helvetica", 10)),
    sg.InputText(key='-WIDTH-', size=(10), font=('Helvetica', 12)), sg.Button("Enter")],
    [sg.Text("Accepted values are between 5 and 1000, edge inclusive", font=("Helvetica", 8))],
    [sg.Text("Current width: "), sg.Text("", key='-CURRENTWIDTH-', font=('Helvetica', 10, 'bold'))]
]

window = sg.Window("ASCII Art Generator", layout, finalize=True)

while True:
    # update ascii art width to most recently input value
    window['-CURRENTWIDTH-'].update(str(imagewidth))
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        for path in image_paths_master:
             os.remove(path)
             time.sleep(0.25)
        break
    # if user clicks search button
    if event == 'Search':
        # clear all images from gui
        for i in range(5):
            window["-IMAGE" + str(i) + "-"].update(data=None)
        image_paths.clear()
        if values['-QUERY-'] != '':
            # prompts user for search, stores results in search_json (json variable)
            search_json = header.user_query(values['-QUERY-'])
            # pulls valid links out of json and stores 5 of them in image_urls[]
            image_urls = header.json_urls(search_json)
            # requests image, downloads it and saves to drive, or prints error if fails to download
            count = 0
            for i in range(len(image_urls)):
                if count > 4: break
                r = requests.get(image_urls[i])
                if r.status_code == 200:
                        # load image data
                        image_data = r.content
                        # parse url into a usable filenamet
                        filename = image_urls[i].split('/')[-1]
                        # discover directory of src
                        script_directory = os.path.dirname(os.path.abspath(__file__))
                        script_directory += "\\temp"
                        # create path to save image to
                        image_paths.append(os.path.join(script_directory, filename))
                        image_paths_master.append(os.path.join(script_directory, filename))
                        # save image
                        with open(os.path.join(script_directory, filename), 'wb') as image_file:
                            image_file.write(image_data)
                        img = Image.open(os.path.join(script_directory, filename))
                        img.thumbnail((300,300),Image.Resampling.LANCZOS)
                        img = ImageTk.PhotoImage(image=img)
                        window["-IMAGE" + str(count) + "-"].update(data=img)
                        count+=1
                else:
                    print("Image " + str(i) + " failed to download.")
    # if user clicks generate button
    if event == 'Generate ASCII Art':
        # if no image paths loaded, skip generation and do nothing
        if not len(image_paths): pass
        else:
            what_to_gen, count = [], 0
            if values['-CHECKBOX0-']==True: what_to_gen.append(0)
            if values['-CHECKBOX1-']==True: what_to_gen.append(1)
            if values['-CHECKBOX2-']==True: what_to_gen.append(2)
            if values['-CHECKBOX3-']==True: what_to_gen.append(3)
            if values['-CHECKBOX4-']==True: what_to_gen.append(4)
            # for console debugging (dist .exe file does not open console, so user wouldnt see output)
            print("What to gen: ", what_to_gen)
            print("Image paths: ", image_paths)
            for x in what_to_gen:
                header.convert_to_ascii(image_paths[x], imagewidth)
                os.startfile('art.txt')
                time.sleep(0.5)
                count+=1
            window['-SUCCESS-'].update(str("Generated " + str(count) + " piece(s) of ASCII art"))
    # update width and displayed width when user changes value and presses enter
    if event == 'Enter':
        input = values['-WIDTH-']
        if input.isdigit():
            input = int(input)
            if input != 0 and input >= 5 and input <= 1000:
                imagewidth = input
        

        

         
