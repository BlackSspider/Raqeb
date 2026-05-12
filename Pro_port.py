from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import socket

pro=Tk()
pro.geometry('500x500')
pro.title('Mowfag Adnan AbuRas ')

'''
This's frist window build by En/Mowfag Adnan Abu Ras ...
Trust allh And your self After That You Can face all word....
2025-12-12 & level 4 '☻◢

'''

name_port=Entry(pro)
name_port.place(x=350,y=230)

#This function for import Scan port window
def Scanport():
	from Scan_port import app
	app.mainloop()
	

	
	
def Calalte():
	from Cal import root
	
	root.mainloop()



#msg Option one
def msg_byport():
	messagebox.showinfo('info', '☻This option help u know portName ')
	po=Label(pro, text ='Enter Your port number :', fg ='black')
	po.place(x=10, y=230)

#msg Option two
def msg_byname():
	messagebox.showinfo('info', '☻This Option help u know port number')
	pn=Label(pro , text='Enter Your port name : ', fg='black')
	pn.place(x=10,y=230)
	
	

#this fun process by port 
def scan_byport():
		
		s=int(name_port.get())
		#s=21
		Scan=socket.getservbyport(s)
		messagebox.showinfo('Your number of port is◣☻◢  ', Scan)
		return
#this fun process by name
def scan_byname():
	sn=name_port.get()
	Scan=socket.getservbyname(str(sn))
	messagebox.showinfo('Result',Scan )
	return
	
	
	
	

#This Label for  MainTitle
lbl1=Label(pro, text ='Mowfag Adnan AbuRas For ➪ know pro_port ',fg='white', bg='black' , width= 50 )
lbl1.pack(side='top')

#This Label for all Option
lb2=Label(pro , text = 'Click One options to use :', fg= 'Black')
lb2.place(x=1 ,y=100)

#this button for by port
bt1=Button(pro, text='byport ' , fg='white', bg ='gray' , cursor='spider' ,command=msg_byport)
bt1.place(x=10,y=150)

#this button for by name
bt2=Button(pro , text ='byname' , fg='white', bg='gray', cursor='spider' , command=msg_byname)
bt2.place(x=180, y=150)


#this button for Scan byport
bt_ok=Button(pro, text='◄Scan_byport►☻',width=15,height=2, fg='black',bg='silver' , cursor='heart' , command=scan_byport)
bt_ok.pack(side='right')
#this button for Scan byname
bt_sn=Button(pro , text= '◄Scan_byname►☻', width=15,height=2,fg='black', bg='silver', command=scan_byname)
bt_sn.pack(side='left')

#this button for Exit window
bt_exit=Button(pro,text='◄Exit► ☹', width=20, height=2, fg ='black', bg='silver', command=pro.quit)
bt_exit.pack(side='bottom')

#This button for Open Scanport window
bt_scan=Button(pro , text ='◄Scaning Open port►', width=15, height=2 , fg='black' ,activebackground='green', activeforeground='white'  ,  cursor='spider' , command=Scanport)

bt_scan.place(x=200, y =400)

####Button  for Open Cal ######
bt_cal=Button(pro , text ='◄Calcaltor►', width =8 , height=2 , fg ='black' , activebackground='red' , cursor ='hand2' , command=Calalte)

bt_cal.place(x=200, y = 500)



#this run window
pro=mainloop()