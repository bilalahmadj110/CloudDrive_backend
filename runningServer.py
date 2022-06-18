from tkinter import *
import subprocess

window = Tk()

font_name = "Helvetica"
font_size = 12

ip_lbl = Label(window, text="IP: ", font=(font_name, font_size))
txtfld = Entry(window, text="", bd=5, font=(font_name, font_size))
ip_lbl.grid(row=0, column=0)
txtfld.grid(row=0, column=1)

var1 = IntVar()
checkbox = Checkbutton(window, text="Save IP", variable=var1, font=(font_name, font_size)).grid(row=1, column=1)

output_txt = Text(window, height=10, width=50, font=(font_name, font_size))
output_txt.grid(row=2, column=0, columnspan=2)


btn = Button(window, text="Run Server", fg='blue')
btn.grid(row=3, column=1)

def redirect(module, method):
    '''Redirects stdout from the method or function in module as a string.'''
    proc = subprocess.Popen(["py", "-m"], stdout=subprocess.PIPE)
    out = proc.communicate()[0]
    return out.decode('unicode_escape')

def put_in_txt():
    '''Puts the redirected string in a text.'''
    print (redirect("runningServer", "main"))
    output_txt.insert('1.0', redirect("src", ""))
    
# add listener to button
btn.bind(put_in_txt)

window.title('Hello Python')
window.geometry("500x300+10+10")
window.mainloop()