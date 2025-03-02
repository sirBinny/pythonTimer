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
clk = Pin(10, Pin.IN, Pin.PULL_UP)
dt = Pin(11, Pin.IN, Pin.PULL_UP)
sw = Pin(12, Pin.IN, Pin.PULL_UP)

# Variables to track rotation(dt,clk,sw)
rotary = Rotary(dt,clk,sw)
val = 0
currentPage = 0
onPage = False
settingTime = False
startTimer = False

TimerHolder = None

timeHour = 0
timeSecs = 0
timeMins = 0

# other stuff
welcomeText = "Pomodoro Timer"
version = "version 0.1"

pages = ["Set Hours","Set Minutes","Set Seconds","Start Timer"]

def welcome():
    oled.text(welcomeText,centerMsg(welcomeText),4)
    oled.text(version,centerMsg(version),12)
    oled.show()
    time.sleep(2)
    oled.contrast(1)

def highlight(obj):
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
    elif currentPage == 2 and value <= 60:
        timeMins = value
    elif currentPage == 3 and value <= 60:
        timeSecs = value
        
def retrieveTime():
    global currentPage, timeHour, timeMins, timeSecs
    if currentPage == 1:
        return timeHour
    elif currentPage == 2:
        return timeMins
    return timeSecs

def startTimerClock(timer):
    global timeSecs, timeMins, timeHour, TimerHolder
    
    
    if timeSecs == 0 and timeMins == 0 and timeHour == 0:
        oled.fill(0)
        oled.text("TIME'S UP!", centerMsg("TIME'S UP!"), 12)
        oled.show()
        TimerHolder.deinit()

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
    oled.text("timer",centerMsg("timer"),4)
    time_str = "{:02d}:{:02d}:{:02d}".format(timeHour, timeMins, timeSecs)

    oled.text(time_str,centerMsg(time_str),12)
    oled.show()
    
#set screen based on scroll value
def checkScreen():
    global currentPage, onPage,val, startTimer
    if startTimer:
        print("starting timer")
        startTimerClock()
        return
        
    
    if onPage:
        relativeValue = retrieveTime()
        SetMessage(str(relativeValue),4)
        #storeTime(val)
        return
    SetMessage(pages[currentPage-1],4)
    
    

def rotary_changed(change):
    global val, onPage, currentPage,settingTime, startTimer, TimerHolder
    if startTimer : return
    if change == Rotary.ROT_CW:
        if onPage: # when user is adjusting values within a page
            cacheValue = retrieveTime()
            val = 0
            val = val + 1
            #val = val if val >= 0 else 0
            storeTime(cacheValue + val)
        else:
            currentPage += 1
            #currentPage = currentPage%5
            currentPage = currentPage if currentPage > 0 and currentPage < 5 else 4
        
    elif change == Rotary.ROT_CCW:
        if onPage:
            cacheValue = retrieveTime()
            val = 0
            val = val - 1
            storeTime(cacheValue + val)

        else:
            currentPage -= 1
            currentPage = currentPage if currentPage > 0 else 1
            
    elif change == Rotary.SW_PRESS:
        if pages[currentPage-1] == "Start Timer" :
            print("pressed")
            startTimer = True
            TimerHolder = Timer(period=1000, mode=Timer.PERIODIC, callback=startTimerClock)  # 1000ms = 1 second
            return
        onPage = not onPage
        

    
    checkScreen()
    
    
            
rotary.add_handler(rotary_changed)
welcome()
    
    
    