# ========================= #
# PIXELY DRAWER             #
# ========================= #

import numpy as np
import sys

from .. import COLORS
from .util.color import hsv_to_rgb, rgb_to_hsv

class Drawer:

    # Replace with superclass var
    PADDING_X = 1
    PADDING_Y = 1

    def __init__(self):
        pass

    # Convert to superclass method?
    def update(self,padding_x, padding_y):
        self.PADDING_X = padding_x
        self.PADDING_Y = padding_y

    # ========================= #
    # DRAWERS                   #
    # ========================= #

    def draw(self,color: int, x: float, y: float, text: str, textcolor: list = None):
        
        color_start = ""
        color_end = ""

        position_start = f"\x1b7\x1b[{y};{x}f"
        position_end = "\x1b8"
        
        if sum(color) > 350 and textcolor == None:
            text = f"\x1b[38;2;0;0;0m{text}\x1b[0m"
        
        if textcolor != None:
            text = f"\x1b[38;2;{textcolor[0]};{textcolor[1]};{textcolor[2]}m{text}\x1b[0m"

        if color[0] != -1: # Transparent
            color_start = f"\x1b[48;2;{color[0]};{color[1]};{color[2]}m"
            color_end = "\x1b[0m"        

        sys.stdout.write(color_start+position_start+text+position_end+color_end)

    def draw_image(self,img, pos):
        
        offset_y = 6
        y, x, _ = img.shape
        text = "  "

        for j in range(y):
            for i in range(x):
                if i == pos[0] and j == pos[1]:
                    text = "[]"        
                self.draw(
                    img[j][i]
                    ,i*2+2+self.PADDING_X
                    ,j+1+offset_y+self.PADDING_Y
                    ,text
                )
        
        sys.stdout.flush()

    def draw_image_box(self,img):
        
        offset_y = 6
        y, x, _ = img.shape
        
        box_top = "╭"+"─"*(x*2)+"╮"
        box_mid = "│"+" "*(x*2)+"│"
        box_bot = "╰"+"─"*(x*2)+"╯"
        
        self.draw(
            [-1]
            ,1+self.PADDING_X
            ,offset_y+self.PADDING_Y
            ,box_top
            ,COLORS["edge"]
        )

        for i in range(y):
            self.draw(
                [-1]
                ,1+self.PADDING_X
                ,offset_y+self.PADDING_Y+1+i
                ,box_mid
                ,COLORS["edge"]
            )
        
        self.draw(
            [-1]
            ,1+self.PADDING_X
            ,offset_y+self.PADDING_Y+1+y
            ,box_bot
            ,COLORS["edge"]
        )

    # ========================= #
    # FILL SHAPE                #
    # ========================= #

    def flood_fill(self, pos, img, color, original_color):
        
        img[pos[1]][pos[0]] = color
       
        neighbors = [
            [pos[1]-1, pos[0]],
            [pos[1]+1, pos[0]],
            [pos[1], pos[0]-1],
            [pos[1], pos[0]+1]
        ]

        for i, j in neighbors:
            if i >= 0 and j >= 0 and i < img.shape[0] and j < img.shape[1]:
                if np.array_equal(img[i][j], original_color) and not np.array_equal(img[i][j], color):
                    img = self.flood_fill([j,i], np.copy(img), color, original_color)

        return img

    # ========================= #
    # COLOR SELECTOR            #
    # ========================= #

    def change_hue(self, color: list, amount: int):
        color[0] += amount
        color[0] = min(max(0,color[0]),180)//18*18
        return color

    def change_saturation(self, color: list, amount: int):
        color[1] += amount
        color[1] = min(max(0,color[1]),255)//25*25
        return color

    def change_value(self, color: list, amount: int):
        color[2] += amount
        color[2] = min(max(0,color[2]),255)//25*25
        return color

    def color_select(self,color: list, offset_y: int = 1):
        
        section_width = 11
        box_height = 3

        box_top = "╭"+"┬".join(["─"*section_width]*4)+"╮"
        box_mid = "│"+"│".join([" "*section_width]*4)+"│"
        box_bot = "╰"+"┴".join(["─"*section_width]*4)+"╯"

        self.draw(
            [-1]
            ,1+self.PADDING_X
            ,1+offset_y+self.PADDING_Y
            ,box_top
            ,COLORS["edge"]
        )

        for i in range(box_height):
            self.draw(
                [-1]
                ,1+self.PADDING_X
                ,1+offset_y+self.PADDING_Y+1+i
                ,box_mid
                ,COLORS["edge"]
            )

        self.draw(
            [-1]
            ,1+self.PADDING_X
            ,1+offset_y+self.PADDING_Y+box_height
            ,box_bot
            ,COLORS["edge"]
        )

        # Draw instruction text
        instructions = ["[u/j]: hue","[i/k]: sat", "[o/l]: val", "current"]
        for i in range(len(instructions)):
            self.draw(
                [-1]
                ,1+self.PADDING_X+1+i*12
                ,1+offset_y+self.PADDING_Y+1
                ,instructions[i]
                ,COLORS["secondary"]
            )

        ticks = 10

        # Draw hue display
        for h in range(0,181,180//ticks):
            ncolor = [h,255,255]
            text = " "
            ncolor_rgb = hsv_to_rgb(ncolor)
            if round(color[0]/18)*18 == h:
                text = "●"
            self.draw(
                ncolor_rgb
                ,h//(180//ticks)+1+self.PADDING_X+1
                ,2+offset_y+self.PADDING_Y+1
                ,text
            )

        # Draw saturation display
        for s in range(0,251,250//ticks):
            ncolor = color.copy()
            ncolor[1] = s
            text = " "
            ncolor_rgb = hsv_to_rgb(ncolor)
            # This is not the best way but at this point I'm too tired to care
            if color[1]//(250/ticks)*250//ticks == s:
                text = "●"
            self.draw(
                ncolor_rgb
                ,s//(250//ticks)+ticks+3+self.PADDING_X+1
                ,2+offset_y+self.PADDING_Y+1
                ,text
            )

        # Draw value display
        for v in range(0,251,250//ticks):
            ncolor = color.copy()
            ncolor[2] = v
            text = " "
            ncolor_rgb = hsv_to_rgb(ncolor)
            if color[2]//(250/ticks)*250/ticks == v:
                text = "●"
            self.draw(
                ncolor_rgb
                ,v//(250//ticks)+2*ticks+5+self.PADDING_X+1
                ,2+offset_y+self.PADDING_Y+1
                ,text
            )
        
        self.draw(
            hsv_to_rgb(color)
            ,37+self.PADDING_X+1
            ,2+offset_y+self.PADDING_Y+1
            ," "*11
        )