from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.filedialog import askopenfile
from tkinter import messagebox
import os
import ctypes
win  = Tk()


myappid = 'mycompany.myproduct.subproduct.version'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


win.iconbitmap(default="R2N.ico")
global file1
file1 = None

def fileOpen():
    
    file1 = filedialog.askdirectory()
    btnRename = tk.Button(text="Rename all",width=20,pady=10,command=lambda: rename_file(file1),state=NORMAL).pack()
    path = os.chdir(file1)
    if file1:
        current_dir.set(file1)
        list_files(file1)
    return file1
    
def rename_file(file1):
        if messagebox.askyesno("Question","Are you sure?") == True:
           
                i = 1
                for file in os.listdir(file1):
                    new_file_name = "{0:03d}.png".format(i)
                    os.rename(file,new_file_name)
                    i = i + 1  
                    print(file)
                messagebox.showinfo("","Success")
        else:
            print("Cancel") 

def list_files(file1):
    for item in tree_view.get_children():
        tree_view.delete(item)
    for filename in os.listdir(file1):
        if os.path.isfile(os.path.join(file1, filename)):
            tree_view.insert("", "end", values=(filename,))
    

   
current_dir = StringVar()
        


width = 700
height = 600
x = (win.winfo_screenwidth()//2) - (width//2)
y = (win.winfo_screenheight()//2) - (height//2)
win.geometry('{}x{}+{}+{}' .format(width,height,x,y))
win.title("ReReFilename")



btnOpenFile = Button(text="Open Folder",width=20,pady=10,command=fileOpen).pack()

folder_label = tk.Label(win, textvariable=current_dir)
folder_label.pack()

tree_view = ttk.Treeview(win, columns=("Files",), show="headings", selectmode="browse")
tree_view.heading("Files", text="Files in Directory")
tree_view.pack(padx=200, pady=40, fill="both", expand=True)

vsb = ttk.Scrollbar(win, orient="vertical", command=tree_view.yview)
vsb.place(x=480, y=130, height=360)

tree_view.configure(yscrollcommand=vsb.set)




win.mainloop()