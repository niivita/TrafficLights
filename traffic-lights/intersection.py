import time
import tkinter as tk


# Single light
class TrafficLight:

    def __init__(self, color, offset):
        self.offset = offset  # position left to right for this instance to draw its light
        self.canvas = canvas
        canvas.create_rectangle(offset + 0, 30, offset + 100, 370, fill="black")
        canvas.create_oval(offset + 3, 40, offset + 100, 140, fill="grey")
        canvas.create_oval(offset + 3, 150, offset + 100, 250, fill="grey")
        canvas.create_oval(offset + 3, 260, offset + 100, 360, fill="grey")
        self.redLight = canvas.create_oval(self.offset + 3, 40, self.offset + 100, 140, fill="grey")
        self.yellowLight = canvas.create_oval(self.offset + 3, 150, self.offset + 100, 250, fill="grey")
        self.greenLight = canvas.create_oval(self.offset + 3, 260, self.offset + 100, 360, fill="grey")

        self.setColor(color)

    # sets the color
    def setColor(self, color):
        if color == "RED":
            canvas.itemconfig(self.redLight, fill="red")
            canvas.itemconfig(self.yellowLight, fill="grey")
            canvas.itemconfig(self.greenLight, fill="grey")
        elif color == "YELLOW":
            canvas.itemconfig(self.redLight, fill="grey")
            canvas.itemconfig(self.yellowLight, fill="yellow")
            canvas.itemconfig(self.greenLight, fill="grey")
        elif color == "GREEN":
            canvas.itemconfig(self.redLight, fill="grey")
            canvas.itemconfig(self.yellowLight, fill="grey")
            canvas.itemconfig(self.greenLight, fill="green")


# create GUI
root = tk.Tk()
root.title("Traffic Light Simulation")
canvas = tk.Canvas(root, width=450, height=400, bg="white")
canvas.pack()

# lights within logic
trafficLights = [TrafficLight("RED", 0), TrafficLight("GREEN", 110), TrafficLight("RED", 220),
                 TrafficLight("GREEN", 330)]


# update the light GUIs
def update_traffic_lights():
    root.update()


# Loop to change light colors based on time
# { Green(s) + Yellow(s) = Red(s) }
t = 0
while t <= 24:
    t = round(t, 1)

    # @ 9s, change E/W light to Yellow {9s Green}
    if t == 9:
        trafficLights[1].setColor("YELLOW")
        trafficLights[3].setColor("YELLOW")

    # @ 11s, change E/W light to Red {2s Yellow}
    if t == 11:
        trafficLights[1].setColor("RED")
        trafficLights[3].setColor("RED")

    # delay & @ 11s, change N/S light to Green {13s red}
    if t == 12:
        trafficLights[0].setColor("GREEN")
        trafficLights[2].setColor("GREEN")

    # @ 21s, change N/S light to Yellow {9s Green}
    if t == 21:
        trafficLights[0].setColor("YELLOW")
        trafficLights[2].setColor("YELLOW")

    # @ 23s, change N/S light to Red {2s Yellow}
    if t == 23:
        trafficLights[0].setColor("RED")
        trafficLights[2].setColor("RED")

    # @ 24s, change E/W light to Green {13s Red}
    if t == 24:
        trafficLights[1].setColor("GREEN")
        trafficLights[3].setColor("GREEN")
        t = 0

    # update GUI with new colors
    update_traffic_lights()
    t += .1
    time.sleep(.1)  # stops script for .1 seconds (for animation)

root.mainloop()
