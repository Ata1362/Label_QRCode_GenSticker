import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
import cv2 as cv




def motion(event):
    x, y = event.x, event.y
    print('{}, {}'.format(x, y))



def UploadAction(event=None):
    filename = filedialog.askopenfilename()
    print('Selected:', filename)
    if filename:
        img = ImageTk.PhotoImage(Image.open(filename))
        '''Very key code to activate the possibility of having more than one winodws function simultansly'''
        preview = tk.Toplevel(win)
        canvas = tk.Canvas(preview)
        canvas.pack(expand="no", fill="none")#expand=tk.YES, fill=tk.BOTH
        panel = tk.Label(preview, image=img)
        panel.pack(side="bottom", fill="both", expand="yes")
        #canvas.create_rectangle(10, 10, 200, 500, fill='yes', outline='blue', width=0)
        preview.bind('<Motion>', motion)
        preview.mainloop()

    else:
        print('No file loaded')




product_list = ['PISTACHIO INSHELL', 'PISTACHIOS KERNEL', 'DRIED FIGS', 'RAISINS', 'SUNFLOWER SEED']


win = tk.Tk()
win.geometry("800x600")
win.title("TAHER Label Generator")


label1 = tk.Label(win, text="Your Brand")
brand_name = tk.Entry(win)
brand_name.insert(0, "Company's Brand")

label2 = tk.Label(win, text="Contract Number")
contract_number = tk.Entry(win)
contract_number.insert(0, "C5360NJF")

label3 = tk.Label(win, text="Product")
product_type = tk.StringVar(win)
product_type.set("Choose") # default value
'''Adding the "*" was a key solution to make the list vertical for the OptionMenu'''
product_type_menu = tk.OptionMenu(win, product_type, *product_list)

label4 = tk.Label(win, text="Total Packs")
total_packs = tk.Entry(win)
total_packs.insert(0, "0")

label5 = tk.Label(win, text="Upload the template")
button = tk.Button(win, text='Open', command=UploadAction)

'''define the positions'''

label1.grid(row=1, column=0)
label2.grid(row=2, column=0)
label3.grid(row=3, column=0)
label4.grid(row=4, column=0)
label5.grid(row=5, column=0)


brand_name.grid(row=1, column=1)
contract_number.grid(row=2, column=1)
product_type_menu.grid(row=3, column=1)
total_packs.grid(row=4, column=1)
button.grid(row=5, column=1)







win.mainloop()
