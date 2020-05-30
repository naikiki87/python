import tkinter
import tkinter.ttk
import time

window=tkinter.Tk()
window.title("YUN DAE HEE")
window.geometry("640x400+100+100")
window.resizable(False, False)

def cc(self):
    treeview.tag_configure("tag2", background="red")

treeview=tkinter.ttk.Treeview(window, columns=["one", "two"], displaycolumns=["two", "one"])
treeview.pack()

treeview.column("#0", width=100)
treeview.heading("#0", text="num")

treeview.column("one", width=100, anchor="center")
treeview.heading("one", text="문자", anchor="center")

treeview.column("#2", width=100, anchor="w")
treeview.heading("two", text="ASCII", anchor="center")

treelist=[("A", 65), ("B", 66), ("C", 67), ("D", 68), ("E", 69)]

for i in range(len(treelist)):
    # print(i)
    print(treelist[i])
    treeview.insert('', 'end', text=i, values=treelist[i], iid=str(i)+"번")

count=0

def countUP():
    global count
    count +=1
    label.config(text=str(count))

label = tkinter.Label(window, text="0")
label.pack()

button = tkinter.Button(window, overrelief="solid", width=15, command=countUP, repeatdelay=1000, repeatinterval=100)
button.pack()




window.mainloop()




# treelist.append(item)
# treelist.append(item)
# treeview.insert('', 'end', text=item, values=treelist[i], iid=str(i)+"번")

