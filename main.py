from machine import Pin, I2C, Timer
import time
from ssd1306 import SSD1306_I2C
from helperfunc import centerMsg
from rotary import Rotary

# Set up OLED display
i2c = I2C(0, scl=Pin(1), sda=Pin(0))

oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)
oled.fill(0)

# Configure pins for rotary encoder
clk = Pin(20, Pin.IN, Pin.PULL_UP)
dt = Pin(19, Pin.IN, Pin.PULL_UP)
sw = Pin(18, Pin.IN, Pin.PULL_UP)

# Variables to track rotation(dt,clk,sw)
rotary = Rotary(dt,clk,sw)

# controller variable
val = 0
currentPage = 0
onPage = False
startTimer = False
TimerHolder = None
currentObjectSelected = 0
startedTimerSelected = 0

timeHour = 0
timeSecs = 0
timeMins = 0

# other stuff
welcomeText = "Pomodoro Timer"
version = "version 0.1"

pages = ["Set Hours","Set Minutes","Set Seconds","Start Timer"]

objectsInTimer = ["pause","cancel"]

def welcome():
    oled.text(welcomeText,centerMsg(welcomeText),4)
    oled.text(version,centerMsg(version),12)
    oled.show()
    time.sleep(2)
    oled.contrast(1)

def highlight(obj,yoffset):
    oled.rect(centerMsg(obj)-4,yoffset-2,len(obj)*8+8,12,1) #(x,y,sizex,sizey, color)


#standard yoffset is 4
def SetMessage(msg, yoffset):
    oled.fill(0)
    oled.text(msg,centerMsg(msg),yoffset)
    oled.show()
    
def storeTime(value):
    global currentPage, timeHour, timeMins, timeSecs
    if value < 0 : return
    if currentPage == 1:
        timeHour = value
    elif currentPage == 2 and value < 60:
        timeMins = value
    elif currentPage == 3 and value < 60:
        timeSecs = value
        
def retrieveTime():
    global currentPage, timeHour, timeMins, timeSecs
    if currentPage == 1:
        return timeHour
    elif currentPage == 2:
        return timeMins
    return timeSecs


def updateHighlight(direction): #direction is number 1 is CW/ -1 is CCW
    currentObjectSelected += direction

def startTimerClock(timer):
    global timeSecs, timeMins, timeHour, TimerHolder, startTimer
    print("calling timer clock")
    
    if timeSecs == 0 and timeMins == 0 and timeHour == 0:
        TimerHolder.deinit()

        oled.fill(0)
        oled.text("TIME'S UP!", centerMsg("TIME'S UP!"), 12)
        oled.show()
        time.sleep(0.5)
        SetMessage(pages[currentPage-1],4)
        startTimer = False
        return
    # Decrement seconds
    timeSecs -= 1
    
    # Handle rollover
    if timeSecs < 0:
        if timeMins > 0:
            timeMins -= 1
            timeSecs = 59
        elif timeHour > 0:
            timeHour -= 1
            timeMins = 59
            timeSecs = 59
    
    oled.fill(0)
    highLightOnTimerScreen()

    oled.text("timer",centerMsg("timer"),4)
    
    oled.text("pause",centerMsg("pause"),30)
    
    oled.text("cancel",centerMsg("cancel"),40)
    
    time_str = "{:02d}:{:02d}:{:02d}".format(timeHour, timeMins, timeSecs)

    oled.text(time_str,centerMsg(time_str),12)
    oled.show()
    
#set screen based on scroll value
def checkScreen():
    global currentPage, onPage
        
    
    if onPage:
        relativeValue = retrieveTime()
        SetMessage(str(relativeValue),4)
        #storeTime(val)
        return
    SetMessage(pages[currentPage-1],4)
    
    
def highLightOnTimerScreen():
    global startedTimerSelected
    if startedTimerSelected%2 == 0:
        highlight("pause",30)
    else:
        highlight("cancel",40)


def rotary_changed(change):
    global onPage, currentPage, startTimer, TimerHolder, startedTimerSelected
    if startTimer :
        print("currently in timer")
        #we want to highlight the options and allow user to select them
        if change == Rotary.ROT_CW:
            startedTimerSelected += 1
            return
                
        elif change == Rotary.ROT_CCW:
            startedTimerSelected -= 1
            return
        
        elif change == Rotary.SW_PRESS:
            if startedTimerSelected%2 == 0: #pause
                print("ON PAUSE")
                #TimerHolder.deinit()
                #startTimer = False
            else: #cancel
                TimerHolder.deinit()
                timeHour = 0
                timeMins = 0
                timeSecs = 0
                startTimer = False
            return
        


    
    if change == Rotary.ROT_CW:
        if onPage: # when user is adjusting values within a page
            current = retrieveTime()
            storeTime(current + 1)
        else:
            currentPage += 1
            #currentPage = currentPage%5
            currentPage = currentPage if currentPage > 0 and currentPage < 5 else 4
            
    elif change == Rotary.ROT_CCW:
        if onPage:
            current = retrieveTime()
            storeTime(current - 1)

        else:
            currentPage -= 1
            currentPage = currentPage if currentPage > 0 else 1
            
    elif change == Rotary.SW_PRESS:
        print("hi im being pressed")
        if pages[currentPage-1] == "Start Timer" :
            print("pressed")
            startTimer = True
            TimerHolder = Timer(period=1000, mode=Timer.PERIODIC, callback=startTimerClock)  # 1000ms = 1 second
            return
        onPage = not onPage
        

    
    checkScreen()

rotary.add_handler(rotary_changed)
welcome()
    
    
    
