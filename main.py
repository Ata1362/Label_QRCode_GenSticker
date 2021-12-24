import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import cv2 as cv
from PIL import Image
import numpy as np
import pandas as pd
import os
from os import listdir
from os.path import isfile, join
import qrcode

'''Here we chose the ROI and create a preview of the final Label'''
def draw_roi(path):
    label_draft = cv.imread(path)
    scale_percent = 35  # percent of original size which can get it from the GUI
    width = int(label_draft.shape[1] * scale_percent / 100)
    height = int(label_draft.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    resized = cv.resize(label_draft, dim, interpolation=cv.INTER_AREA)

    QRCode = qrcode.make('This is a sample QR-Code for the template')
    QRCode.save("sample.png")
    qr_code_master = Image.open("sample.png")

    roi_position = cv.selectROIs("Select ROIs", resized)
    cv.destroyWindow("Select ROIs")
    dim = []
    roi_position = roi_position * 100 / scale_percent
    for i in range(0, len(roi_position)):
        dim.append(round(max([roi_position[i][2], roi_position[i][3]])))

    label_draft = Image.open(path)
    for i in range(0, len(dim)):
        qr_code = qr_code_master.resize((dim[i], dim[i]))
        label_draft.paste(qr_code, (round(roi_position[i][0]), round(roi_position[i][1])))

    label_draft.show()
    print("ROI Position is: {}".format(roi_position))
    print("Dim Resizes are: {}".format(dim))

    return roi_position, dim

def UploadAction(event=None):
    global filename, fileisloaded
    filename = filedialog.askopenfilename()
    if filename:
        print('Selected:', filename)
        tk.messagebox.showinfo(title="Status", message="Press 'OK' and DRAG the pointer where to stick the QR-Code and press Enter")
        global roi_position, dim
        roi_position = []
        dim = []
        roi_position, dim = draw_roi(filename)
        fileisloaded = True
        return filename
    else:
        print('No file is loaded')
        fileisloaded = False
    return None

def CreateRandomTrackingNumber(start, stop, totalsample, startstring):
    '''String is the code for the contract and manufacturer company's name.
    strat and stop is the range of numbers we want to have codes.
    TotalSample is the number of QR code we want to create.'''
    start = 1000
    stop = 9999
    data = []
    rnd = np.random.choice(range(start, stop), totalsample, replace=False)
    for i in rnd:
        data.append(startstring+str(i))
    return data

def SaveTrackingAsExcel(data, address, contract, product):
    '''#Data is the array of all tracking codes.
    Address is the location we want to save the Excel file, must ends with / or \.
    Contract number as a string to add it in the file name.'''

    path = address + contract + "/" + product
    path = path.replace(' ', '_')
    if not os.path.exists(path):
        os.makedirs(path)
    writer = pd.ExcelWriter(path + '/' + product + '.xlsx', engine='xlsxwriter')

    # Change the Numpy format to Pandas format to save in Excel file
    panda_dic = pd.DataFrame(data)
    # Data is the Excel's Sheet name to save the data in.
    panda_dic.to_excel(writer, 'Tracking')
    writer.save()
    return

def read_entries():
    brand_name_input = brand_name.get()
    brand_name_input = brand_name_input.strip().upper()

    contract_number_input = contract_number.get()
    contract_number_input = contract_number_input.strip().upper()

    product_type_input = product_type.get()
    product_type_input = product_type_input.strip().upper()

    total_packs_input = total_packs.get()
    initial_message_input = initial_message.get()

    '''Date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')'''

    data_entry = pd.DataFrame(
        {'Company': brand_name_input, 'Product': product_type_input,
         'Contractnumber': contract_number_input,
         'Totalpacks': float(total_packs_input), 'Message': initial_message_input}, index=[0])

    return data_entry

def SimpleCreateQRCodes(data, message, destination_address):
    path = destination_address + "/QRCODES"
    if not os.path.exists(path):
        os.makedirs(path)
    for i in data:
        message2 = ""
        message2 = message + i
        QRCode = qrcode.make(message2)
        QRCode.save(path + "/" + i + ".png")

    return path, destination_address

def generate_final_labels(path_QrCodes, destination_address):
    path_final = destination_address + "/Final_Labels"
    if not os.path.exists(path_final):
        os.makedirs(path_final)

    onlyfiles = [f for f in listdir(path_QrCodes) if isfile(join(path_QrCodes, f))]
    print(onlyfiles)
    label_template = Image.open(filename)
    counter = 0
    lp = len(dim) + 1 # To make sure the the internal counter covers all the dimensions ROIs.
    label_template_copy = label_template.copy()

    print("Dim's Length is {}".format(lp))
    file_counter = 0

    for file in onlyfiles:
        counter += 1
        file_counter += 1
        print('counter = ', counter)
        if counter % lp != 0:
            qr_code = Image.open(path_QrCodes + "/" + file)
            qr_code = qr_code.resize((dim[counter - 1], dim[counter - 1]))
            label_template_copy.paste(qr_code, (round(roi_position[counter-1][0]), round(roi_position[counter-1][1])))
        else:
            label_template_copy.save(path_final + "/" + file.split('.')[0] + "_" + str(file_counter) + ".jpg")
            label_template_copy = label_template.copy()
            counter = 0
            print('File_Counter is: ', file_counter)

    label_template_copy.save(path_final + "/" + file.split('.')[0] + ".jpg") # To save the lastest qrcodes that are not saved yet.

def produce_labels():
    if fileisloaded:
        data = read_entries()
        print(data)
        packs = int(data.Totalpacks) + 10
        print(packs)
        start_string = data.Company[0] + "-" + data.Contractnumber[0] + "-" + data.Product[0] + "-"
        start_string = start_string.replace(' ', '_')
        print(start_string)
        start = 1000
        stop = 5 * packs
        tracking_numbers = CreateRandomTrackingNumber(start, stop, packs, start_string)
        SaveTrackingAsExcel(tracking_numbers, "generated/", data.Contractnumber[0], data.Product[0])
        message = data.Message[0]
        address = "generated/" + data.Contractnumber[0] + "/" + data.Product[0]
        address = address.replace(' ', '_')
        path, destination_address = SimpleCreateQRCodes(tracking_numbers, message, address)
        generate_final_labels(path, destination_address)
        tk.messagebox.showinfo(title="Status", message="Total Labels are Generated")
    else:
        tk.messagebox.showinfo(title="Status", message="Please upload a template")


''' Generate extra 10 pcs of labels to cover damaged ones'''


def load_main_window():
    global win, brand_name, contract_number, product_type, total_packs, initial_message

    win = tk.Tk()
    win.geometry("300x200")
    win.title("The Label Generator")


    label1 = tk.Label(win, text="Your Brand", anchor='w')
    brand_name = tk.Entry(win)
    brand_name.insert(0, "BrandName")

    label2 = tk.Label(win, text="Contract Number", anchor='w')
    contract_number = tk.Entry(win)
    contract_number.insert(0, "C5360NJF")

    label3 = tk.Label(win, text="Product", anchor='w')
    product_type = tk.StringVar(win)
    product_type.set("Choose") # default value
    '''Adding the "*" was a key solution to make the list vertical for the OptionMenu'''
    product_type_menu = tk.OptionMenu(win, product_type, *product_list)

    label4 = tk.Label(win, text="Total Packs", anchor='w')
    total_packs = tk.Entry(win)
    total_packs.insert(0, "500")

    label5 = tk.Label(win, text="Upload the template", anchor='w')

    label6 = tk.Label(win, text="Initial message")
    initial_message = tk.Entry(win)
    initial_message.insert(0, "www.taher-co.com\checker?item=")

    button = tk.Button(win, text='Open', command=UploadAction)

    button_generate = tk.Button(win, text="Generate", bg="green", fg="white", command=produce_labels)

    '''define the positions'''

    label1.grid(row=1, column=0)
    label2.grid(row=2, column=0)
    label3.grid(row=3, column=0)
    label4.grid(row=4, column=0)
    label5.grid(row=5, column=0)
    label6.grid(row=6, column=0)


    brand_name.grid(row=1, column=1)
    contract_number.grid(row=2, column=1)
    product_type_menu.grid(row=3, column=1)
    total_packs.grid(row=4, column=1)
    button.grid(row=5, column=1)
    initial_message.grid(row=6, column=1)
    button_generate.grid(row=7, column=1)


    win.mainloop()
    return

product_list = ['PISTACHIO INSHELL', 'PISTACHIOS KERNEL', 'DRIED FIGS', 'RAISINS', 'SUNFLOWER SEED']
global fileisloaded
fileisloaded = False

load_main_window()