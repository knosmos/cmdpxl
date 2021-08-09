
from threading import Thread
import numpy as np
import time
import cv2
import os

from .util.color import hsv_to_rgb, rgb_to_hsv
from .calls import show_cursor, hide_cursor
from .util.os import get_clear, get_getch
from .drawer import Drawer
from . import COLORS

class Application:

    IN_MENU = False
    RESPONSIVE_PADDING = True
    
    PADDING_X = 1
    PADDING_Y = 1

    POSITION = [0, 0]

    COLOR = [90,125,125]

    # CALLS
    CLEAR = None
    GETCH = None

    # History
    HISTORY = []

    FILENAME = None
    SIZES = None
    IMG = None

    ACTION = None # Action of trigger, create or open

    def __init__(self, filename = None, size = None, trigger: str = None):

        # Initialize objects
        self.drawer = Drawer()
        
        # OS dependant calls
        self.CLEAR = get_clear()
        self.GETCH = get_getch()

        if filename != None:
            self.FILENAME = filename

        if size != None:
            self.SIZES = size

        if trigger != None:
            self.ACTION = trigger.lower()

    def __resize__(self, filename, img):
        
        dimensions = [0,0]

        while True:
            if os.get_terminal_size() != dimensions and not self.IN_MENU:
                self.CLEAR()
                dimensions = os.get_terminal_size()
                if self.RESPONSIVE_PADDING:
                    self.PADDING_X = (dimensions[0] - img.shape[1]*2) // 2
                    self.drawer.update(self.PADDING_X,self.PADDING_Y)
                self.drawer.draw_image_box(img)
                self.__interface__(filename, img)
            time.sleep(0.2)

    def __interface__(self, filename, img):
        
        self.drawer.draw(
            [-1]
            ,1+self.PADDING_X
            ,1+self.PADDING_Y
            ,f"CMDPXL: {filename} ({img.shape[1]}x{img.shape[0]})"
            ,COLORS["highlight"]
        )

        self.drawer.color_select(
            self.COLOR
        )

        self.drawer.draw(
            [-1]
            ,1+self.PADDING_X
            ,8+self.PADDING_Y+img.shape[0]
            ,"[wasd] move │ [e] draw    │ [f] fill"
            ,COLORS["secondary"]
        )

        self.drawer.draw(
            [-1]
            ,1+self.PADDING_X
            ,9+self.PADDING_Y+img.shape[0]
            ,"[z] undo    │ [t] filters │ [esc] quit"
            ,COLORS["secondary"]
        )

        self.drawer.draw_image(
            img
            ,self.POSITION
        )

    def __loop__(self):
        
        while True:

            self.__interface__(self.FILENAME, self.IMG)
            m = self.GETCH()

            # NOTE: Movement
            if m == "w":
                self.POSITION[1] = (self.POSITION[1]-1)%self.IMG.shape[0]
            if m == "s":
                self.POSITION[1] = (self.POSITION[1]+1)%self.IMG.shape[0]
            if m == "a":
                self.POSITION[0] = (self.POSITION[0]-1)%self.IMG.shape[1]
            if m == "d":
                self.POSITION[0] = (self.POSITION[0]+1)%self.IMG.shape[1]

            # NOTE: Drawing
            if m == "e" or m == " ":
                self.HISTORY.append(np.copy(self.IMG))
                self.IMG[self.POSITION[1]][self.POSITION[0]] = hsv_to_rgb(self.COLOR)

            if m == "f":
                self.HISTORY.append(np.copy(self.IMG))
                self.IMG = self.drawer.flood_fill(self.POSITION, self.IMG, hsv_to_rgb(self.COLOR), np.copy(self.IMG[self.POSITION[1]][self.POSITION[0]]))

            if m == "z":
            # Load most recent from history
                if len(self.HISTORY) > 0:
                    self.IMG = self.HISTORY[-1]
                    self.HISTORY.pop(-1)
        
            # NOTE: Color change options
            if m == "u":
                self.COLOR = self.drawer.change_hue(self.COLOR,-18)
            if m == "i":
                self.COLOR = self.drawer.change_saturation(self.COLOR,-25)
            if m == "o":
                self.COLOR = self.drawer.change_value(self.COLOR,-25)

            if m == "j":
                self.COLOR = self.drawer.change_hue(self.COLOR,18)
            if m == "k":
                self.COLOR = self.drawer.change_saturation(self.COLOR,25)
            if m == "l":
                self.COLOR = self.drawer.change_value(self.COLOR,25)

            # NOTE: Filters
            if m == "t":
                self.IN_MENU = True

                show_cursor()
                self.CLEAR()

                self.drawer.draw(
                    [-1]
                    ,1
                    ,1
                    ,"APPLY FILTER"
                    ,COLORS["highlight"]
                )

                print("\n[esc]: Return\n")

                filters = [
                    ["G", "Grayscale", cv2.COLORMAP_BONE],
                    ["S", "Sepia", cv2.COLORMAP_PINK],
                    ["O", "Ocean", cv2.COLORMAP_OCEAN],
                    ["H", "Heatmap", cv2.COLORMAP_JET],
                    ["I", "Invert", None],
                    ["B", "Blur", None]
                ]

                for i in filters:
                    print(f"[{i[0]}]: {i[1]}")
                
                option = " "
                while not (option in [i[0] for i in filters] or option == "\x1b"):
                    option = self.GETCH().upper()
                
                self.CLEAR()

                if option != "\x1b":
                    self.HISTORY.append(np.copy(self.IMG))
                    if option == "I":
                        self.IMG = cv2.bitwise_not(self.IMG)
                    elif option == "B":
                        self.IMG = cv2.blur(self.IMG,(1,2))
                    else:
                        grayscale = cv2.cvtColor(self.IMG, cv2.cv2.COLOR_RGB2GRAY)
                        for i in filters:
                            if i[0] == option:
                                filtered = cv2.applyColorMap(grayscale, i[2])
                                filtered = cv2.cvtColor(filtered, cv2.COLOR_BGR2RGB)
                        self.IMG = filtered
                
                hide_cursor()

                self.drawer.draw_image_box(
                    self.IMG
                )

                self.IN_MENU = False

            # NOTE: Quit
            if m == "\x1b": # esc
                
                self.IN_MENU = True

                show_cursor()
                self.CLEAR()

                self.drawer.draw(
                    [-1]
                    ,1
                    ,1
                    ,"QUIT"
                    ,COLORS["highlight"]
                )

                print("\n[S]: Save and exit")
                print("[Q]: Quit without saving")
                print("\n[esc]: Cancel")

                option = " "
                while not option in "sq\x1b":
                    option = self.GETCH().lower()
                
                self.CLEAR()

                if option == "s":
                    # Convert back to BGR before writing
                    self.IMG = cv2.cvtColor(self.IMG, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(self.FILENAME, self.IMG)
                    exit()
                elif option == "q":
                    exit()

                hide_cursor()
                self.drawer.draw_image_box(self.IMG)

                self.IN_MENU = False

    def __start__(self):
        
        # Start responsiveness thread
        t = Thread(
            target=self.__resize__
            ,args=[self.FILENAME, self.IMG]
        )
        t.daemon = True
        t.start()

        self.__loop__()

    def __initialize__(self):
        
        self.CLEAR()

        if self.FILENAME != None and self.ACTION == "open":
            img = cv2.imread(self.FILENAME)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img = np.zeros((self.SIZES[0],self.SIZES[1],3), np.uint8)
            img[:,:,:] = 250

        self.CLEAR()
        hide_cursor()

        # Assign filename and img
        self.IMG = img

        self.__start__()

        # self.drawer.draw(
        #     [-1]
        #     ,1
        #     ,1
        #     ,"CMDPXL - A TOTALLY PRACTICAL IMAGE EDITOR"
        #     ,COLORS["highlight"]
        # )

        # Empty print
        # print("\n[O]: Open file")
        # print("[C]: Create new file")

        # option = " "

        # while not option in "ocOC":
        #     option = self.GETCH()
        
        # filename = input("File name: ")

        # Load existing image
        # if option.lower() == "o":
        #     img = cv2.imread(filename)
        #     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Create new image
        # else:
        #     height = int(input("New image height: "))
        #     width = int(input("New image width: "))
        #     img = np.zeros((height,width,3), np.uint8)
        #     img[:,:,:] = 250

    def start(self):
        self.__initialize__()