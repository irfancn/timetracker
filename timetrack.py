import tkinter as tk
import tkinter.font as tkFont
import os
from datetime import date
import time
import json
import matplotlib.pyplot as plt

root = tk.Tk()
root.title('Timetrack')
img = tk.PhotoImage(file='icon.png')
root.tk.call('wm', 'iconphoto', root._w, img)

def_font = tk.font.nametofont("TkDefaultFont")
def_font.config(size=18)

backcolor = '#03396c'
forecolor = '#b3cde0'
activecolor = '#2E8B57'

canvas = tk.Canvas(root, height=300, width=500, bg=forecolor)
canvas.pack()

# active buttons
activeold = -1
activenew = 0
runparam = 0

# Applications and initial lists
Applications = ['Break', 'Task 1', 'Task 2', 'Task 3', 'Task 4']

appButt = []
appTime = []
appdTime = []
tnew = round(time.time())		# start time of new task
told = round(time.time())		# start time of the last task
act_file = open('activity.json', 'r')
act_data = json.load(act_file)
today = str(date.today())

if str(date.today()) == act_data['dates'][-1]:
	activity = act_data['entries'][-1]
else:
	activity = {'applications':Applications, 'time':[0,0,0,0,0]}

# Functions
def activatebar(param):				# activating bars
	appTime[param].config(bg=activecolor)
	appdTime[param].config(bg=activecolor)
	appButt[param].config(bg=activecolor)

def deactivatebar(param):			# deactivating bars
	appTime[param].config(bg=backcolor)
	appdTime[param].config(text='0:0:0', bg=backcolor)
	appButt[param].config(bg=backcolor)

def timeupdate():					# updating the timer
	global runparam, label, tnew
	if runparam:
		dtime = round(time.time()) - tnew
		dtimestr = [dtime//3600, (dtime%3600)//60, dtime%60]
		label.config(text= str(dtimestr[0]) + ':' + 
			str(dtimestr[1]) + ':' + str(dtimestr[2]))
		label.after(1000, timeupdate)
	else:
		label.config(text='0:0:0')

def buttonpress(activenew):			# while pressing the app button
	global activeold, runparam, label, told, tnew

	if activenew != activeold:		# not the same button
		label = appdTime[activenew]
		activatebar(activenew)


		if activeold == -1:
			told = round(time.time())
		else:
			told = tnew
		tnew = round(time.time())
		runparam = 1
		timeupdate()
		
		if activeold > -1:			# avoiding the first case
			deactivatebar(activeold)
			actupdate()

		activeold = activenew

def stopfun():						# to stop timer and rest
	global activeold, runparam, label, told, tnew
	if activeold > -1:
		told = tnew
		runparam = 0
		label = appdTime[activeold]
		deactivatebar(activeold)
		timeupdate()
		actupdate()
	activeold = -1

def actupdate():				# to update activies
	global activeold, activity, told
	tstep = round(time.time()) - told
	activity['time'][activeold] = activity['time'][activeold] + tstep
	timestr = [activity['time'][activeold]//3600, 
		(activity['time'][activeold]%3600)//60,
		(activity['time'][activeold])%60]
	appTime[activeold].config(text= str(timestr[0]) + ':' + 
			str(timestr[1]) + ':' + str(timestr[2]))
	actsave(activity)

def actsave(activity):			# to save activies
	if str(date.today()) == act_data['dates'][-1]:
		act_data['dates'][-1] = str(date.today())
		act_data['entries'][-1] = activity
	else:
		act_data['dates'].append(str(date.today()))
		act_data['entries'].append(activity)

	with open('activity.json', 'w') as json_file:
		json.dump(act_data, json_file, indent=4)

def actplot():
	days = int(dayEntry.get())
	dayacts = act_data['entries'][-days:]
	actdist = [0, 0, 0, 0, 0]
	for i in range(0, days):
		actdist = [actdist[j] + dayacts[i]['time'][j]/3600
			for j in range(0, len(Applications))]

	colors = ['#4a4e4d','#0e9aa7','#3da4ab','#f6cd61','#fe8a71']
	plt.pie(actdist, labels=Applications, colors=colors,
	autopct='%1.1f%%', startangle=140)

	plt.axis('equal')
	plt.title('Total ' + str(round(sum(actdist), 1)) + ' hours')
	plt.show()

def actclose():				# to close the window
	stopfun()
	root.destroy()


# break tab and buttons
frame = tk.Frame(root, bg=forecolor)
frame.place(height=300, width=480, x=10, y=10)

for i in range(0, len(Applications)):
	tinit = [activity['time'][i]//3600, (activity['time'][i]%3600)//60,
		(activity['time'][i])%60]
	appButt.append(tk.Button(frame, text=Applications[i], bg=backcolor,
		fg='white', width=15, borderwidth=1, relief="raised"))
	appButt[i].grid(row=i, column=0)
	appTime.append(tk.Label(frame, text=str(tinit[0])+':'+
		str(tinit[1])+':'+str(tinit[2]), 
		bg=backcolor, fg='white', width=8, borderwidth=2, relief="groove"))
	appTime[i].grid(row=i, column=1)
	appdTime.append(tk.Label(frame, text='0:0:0', bg=backcolor,
		fg='white', width=8, borderwidth=2, relief="groove"))
	appdTime[i].grid(row=i, column=2)

appButt[0].config(command= lambda: buttonpress(0))
appButt[1].config(command= lambda: buttonpress(1))
appButt[2].config(command= lambda: buttonpress(2))
appButt[3].config(command= lambda: buttonpress(3))
appButt[4].config(command= lambda: buttonpress(4))

# stop button
stopButt = tk.Button(frame, text='Stop', bg=backcolor,
	fg='white', width=6, borderwidth=1, relief="raised",
	command=stopfun)
stopButt.grid(row=5, column=1)

# plotting the history
dayEntry = tk.Entry(frame, width=20, borderwidth=1, justify='center')
dayEntry.insert(0, 'Number of previous days')
dayEntry.grid(row=6, column=0)

plotButt = tk.Button(frame, text='Plot', bg=backcolor,
	fg='white', width=6, borderwidth=1, relief='raised',
	command=actplot)
plotButt.grid(row=6, column=1)

closeButt = tk.Button(frame, text='Close', bg='#fe8a71',
	fg='white', width=6, borderwidth=1, relief='raised',
	command=actclose)
closeButt.grid(row=6, column=2)

root.mainloop()