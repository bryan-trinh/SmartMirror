# home_screen.py

# To run:
# > pip install requests

from tkinter import *
import time
import threading
import requests
import traceback
from user_data import user_info
from user_data.User import *
from user_data import fitbit

from face.facial_identification import *
from face.PIR import *

from display.keyboard import Keyboard

# TODO update when pull facial_recog
# import PIR

CURR_USER = get_user(1)

# OpenWeatherMap
OWM_API = "https://api.openweathermap.org/data/2.5/onecall"
OWM_PARAMS = {
    "lat": "33.6695",
    "lon": "-117.8231",
    "exclude": "minutely,hourly,alerts",
    "units": "imperial",
    "appid": user_info.OWM_KEY
    }

WEATHER_ICON = {
    "01d" : "sun.png", "01n" : "sun.png",
    "02d" : "sun_cloud.png", "02n" : "sun_cloud.png",
    "03d" : "clouds.png", "03n" : "clouds.png", "04d" : "clouds.png", "04n" : "clouds.png", 
    "09d" : "rain.png", "09n" : "rain.png",
    "10d" : "sunshower.png", "10n" : "sunshower.png",
    "11d" : "thunder.png", "11n" : "thunder.png",
    "13d" : "snowflake.png", "13n" : "snowflake.png",
    "50d" : "fog.png", "50n" : "fog.png"
    }

FONT = {
    "heading" : "Trebuchet",
    "body" : "Bahnschrift"
    #Raleway, Ubuntu Light
    }

class AppTimer(object):
    """Timer to call given function repeatedly after given interval."""

    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

class Application(Frame):
    """Opens the home screen of the smart mirror.
    
    Includes widgets for date, time, weather, and health (respiration, sleep, and body temperature).
    (Click the settings/gear icon to exit the Application)
    """

    def __init__(self, master=None):
        """Initializes outer frame and widgets for the Application."""
        # PIR.setup()

        # place frame (self) in window (take up full size)
        super().__init__(master, background="black", bd=20)
        self.master = master
        self.grid(row=0, column=0, sticky=NSEW)
        
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()

        # set up grid (3x3) in frame (take up full size)
        for x in range(3):
            Grid.rowconfigure(self, x, weight=1, uniform="row_third")
            Grid.columnconfigure(self, x, weight=1, uniform="col_third")

        # add a frame to each grid cell
        self.frame = [[Frame(self, bg="black") for m in range(3)] for n in range(3)]
        for i in range(3):
            for j in range(3):
                self.frame[i][j].grid(row=i, column=j, sticky=NSEW)

        # create timers for repeatedly updating widgets
        # datetime every 1 second
        # weather every 1 hour
        
        self.timer_dt = AppTimer(60, self.update_datetime)
        self.timer_w = AppTimer(3600, self.update_weather)
        self.timer_health = AppTimer(3600, self.update_health_stats)
            
        self.create_widgets()
        
        self.motion = PIR_Sensor()
        #self.timer_motion = AppTimer(5, self.lock)
        
        self.FR= FR()
    
    def create_widgets(self):
        self.add_datetime()
        self.add_weather()
        self.add_health_stats()

        # TODO hardcoded rn; finish functionality/return later
        self.keyboard_w = Toplevel(self.master)
        self.keyboard_w.title("Keyboard")
        w, h = 1000, 500
        x, y = (self.width/2 - w/2), (self.height - h - 30)
        self.keyboard_w.geometry("%dx%d+%d+%d" % (w, h, x, y))
        self.keyboard = Keyboard(self.keyboard_w)
        self.keyboard_w.withdraw()

        self.add_user = Button(self.frame[1][2], bg="black", fg="white", text="Add User",
                                command=self.input_user, relief=FLAT)
        self.add_user.config(font=(FONT["body"], 30))

        self.change_user = Button(self.frame[2][2], bg="black", fg="white", text="Change User",
                                command=self.switch_user, relief=FLAT)
        self.change_user.config(font=(FONT["body"], 30))

        self.quit = Button(self.frame[2][2], bg="black", fg="white", text="QUIT",
                            command=self.close, relief=FLAT)
        self.quit.config(font=(FONT["body"], 30))
        
        self.gear = PhotoImage(file = r"./display/icons/gear.png").subsample(10,10)
        self.settings = Button(self.frame[2][2], image=self.gear, bg="black",
                              command=self.show_options, relief=FLAT)
        self.settings.pack(side=BOTTOM, anchor=E)

        self.user_name = Label(self.frame[1][1], bg = "black", fg="white", text=CURR_USER.name)
        self.user_name.config(font=(FONT["body"], 30))
        self.user_name.pack(anchor=CENTER)
        
        self.lock_screen = Button(self.frame[2][1], bg="black", fg="white", text="LOCK",
                            command=self.lock, relief=FLAT)
        self.lock_screen.config(font=(FONT["body"], 30))
        self.lock_screen.pack(anchor=CENTER)
        
    def lock(self):
        print(self.motion.is_valid(), self.motion.motion_detected())
        if self.motion.motion_detected():
            try:
                bool, id = self.FR.recognize_face()
                self.user_name["text"] = "Hi " + str(id)
            except Exception as e:
                traceback.print_exc()
    
    def show_options(self):
        self.settings.config(command=self.hide_options)

        self.quit.pack(side=BOTTOM, anchor=E)
        self.change_user.pack(side=BOTTOM, anchor=E)
        self.add_user.pack(side=BOTTOM, anchor=E)

    def hide_options(self):
        self.settings.config(command=self.show_options)

        self.add_user.pack_forget()
        self.change_user.pack_forget()
        self.quit.pack_forget()

    def input_user(self):
        self.hide_options()

        # User_id should be passed in as a parameter (should be given by facial recognition)
        user_id = 3

        self.keyboard.prompt = "Please enter your name:\n"
        self.keyboard.refresh()
        self.wait_variable(self.keyboard.is_open)
        name = self.keyboard.result

        self.keyboard.prompt = "Please enter your location (ex: Irvine,CA,US):\n"
        self.keyboard.refresh()
        self.wait_variable(self.keyboard.is_open)
        location = self.keyboard.result

        # add new user to json file
        add_new_user(user_id, name, location, FITBIT, fitbit.USER_ID, fitbit.ACCESS_TOKEN)

        # get user from json file
        CURR_USER = get_user(user_id)

        OWM_PARAMS["lat"] = CURR_USER.lat
        OWM_PARAMS["lon"] = CURR_USER.lon
        self.location["text"] = CURR_USER.location

        #update name in middle; remove later
        self.user_name["text"] = CURR_USER.name

        self.timer_w.stop()
        self.update_weather()
        self.timer_w.start()

        self.timer_health.stop()
        if CURR_USER.fbit is None and CURR_USER.oura is None:
            self.heart_rate["text"] = ""
            self.steps["text"] = ""
            # unpack if have pictures...but need to repack
        else:
            self.update_health_stats()
            self.timer_health.start()

    def switch_user(self):
        """
        Assumes user_id is passed from facial recognition
        Switch between users that are already in database
        """
        # TODO: hardcode rn; get id for facial recognition
        user_id = 2

        self.hide_options()

        CURR_USER = get_user(user_id)

        OWM_PARAMS["lat"] = CURR_USER.lat
        OWM_PARAMS["lon"] = CURR_USER.lon
        self.location["text"] = CURR_USER.location

        #update name in middle; remove later
        self.user_name["text"] = CURR_USER.name

        self.timer_w.stop()
        self.update_weather()
        self.timer_w.start()

        self.timer_health.stop()
        if CURR_USER.fbit is None and CURR_USER.oura is None:
            self.heart_rate["text"] = ""
            self.steps["text"] = ""
            # unpack if have pictures...but need to repack
        else:
            self.update_health_stats()
            self.timer_health.start()

    def close(self):
        self.timer_dt.stop()
        self.timer_w.stop()
        self.timer_health.stop()
        #self.timer_motion.stop()
        
        self.master.destroy()

    def add_datetime(self):        
        self.clock = Label(self.frame[0][0], bg="black", fg="white")
        self.clock.config(font=(FONT["body"], 60))
        self.clock.pack(side=TOP, anchor=NW)
        
        self.date = Label(self.frame[0][0], bg="black", fg="white")
        self.date.config(font=(FONT["body"], 30, "bold"))
        self.date.pack(side=TOP, anchor=NW)

        self.update_datetime()
        self.timer_dt.start()

    def update_datetime(self):
        self.clock["text"] = time.strftime("%I:%M %p", time.localtime())
        self.date["text"] = time.strftime("%a, %B %d", time.localtime())

    def add_weather(self):
        self.location = Label(self.frame[0][2], bg="black", fg="white")
        self.location.config(font=(FONT["body"], 30))
        self.location["text"] = CURR_USER.location
        self.location.pack(side=TOP, anchor=NE)

        self.outdoor_main = Frame(self.frame[0][2], bg="black")
        self.outdoor_main.pack(side=TOP, anchor=NE)

        self.outdoor_temp = Label(self.outdoor_main, bg="black", fg="white")
        self.outdoor_temp.config(font=(FONT["body"], 60))
        self.outdoor_temp.pack(side=RIGHT, anchor=SE)

        self.outdoor_icon = Label(self.outdoor_main, bg="black", fg="white")
        self.outdoor_icon.pack(side=RIGHT, anchor=NE)

        self.outdoor_desc = Label(self.frame[0][2], bg="black", fg="white")
        self.outdoor_desc.config(font=(FONT["body"], 25))
        self.outdoor_desc.pack(side=TOP, anchor=NE)

        self.update_weather()
        self.timer_w.start()

    def update_weather(self):
        j = requests.get(url=OWM_API, params=OWM_PARAMS).json()
        icon_id = j["current"]["weather"][0]["icon"]
        self.icon = PhotoImage(file = r"./display/icons/" + WEATHER_ICON[icon_id]).subsample(10,10)

        self.outdoor_temp["text"] = str(int(j["current"]["temp"])) + u"\N{DEGREE SIGN}" + "F"
        self.outdoor_desc["text"] = j["current"]["weather"][0]["description"]
        self.outdoor_icon["image"] = self.icon

    def add_health_stats(self):
        # TODO: update internal temp
        # self.internal_temp = Label(self.frame[2][0], bg="black", fg="white")
        # self.internal_temp.config(font=(FONT["body"], 30))
        # self.internal_temp["text"] = "98" + u"\N{DEGREE SIGN}" + "F"
        # self.internal_temp.pack(side=BOTTOM, anchor=W)

        # TODO: sleep cycles
        # self.sleep_info = Label(self.frame[2][0], bg="black", fg="white")
        # self.sleep_info.config(font=(FONT["body"], 30))
        # self.sleep_info["text"] = "Sleep Info"
        # self.sleep_info.pack(side=BOTTOM, anchor=W)

        # TODO: respiration
        # self.respiration = Label(self.frame[2][0], bg="black", fg="white")
        # self.respiration.config(font=(FONT["body"], 30))
        # self.respiration["text"] = "Respiration"
        # self.respiration.pack(side=BOTTOM, anchor=W)

        self.heart_rate = Label(self.frame[2][0], bg="black", fg="white")
        self.heart_rate.config(font=(FONT["body"], 30))
        self.heart_rate.pack(side=BOTTOM, anchor=W)

        self.steps = Label(self.frame[2][0], bg="black", fg="white")
        self.steps.config(font=(FONT["body"], 30))
        self.steps.pack(side=BOTTOM, anchor=W)

        self.update_health_stats()
        self.timer_health.start()

    def update_health_stats(self):
        if CURR_USER.fbit is not None:
            self.heart_rate["text"] = str(CURR_USER.get_heart_rate()) + " BPM"
            self.steps["text"] = str(CURR_USER.get_steps()) + " steps"


if __name__=="__main__":
    # set up window in fullscreen
    root = Tk()
    #root.wm_attributes("-fullscreen","true")
    
    Grid.rowconfigure(root, 0, weight=1)
    Grid.columnconfigure(root, 0, weight=1)

    app = Application(master=root)
    app.mainloop()
