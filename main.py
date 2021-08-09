import cv2 # Read/write images
import sys # Write to terminal
import os
import numpy as np
from threading import Thread # Constantly check for terminal size update
import time
import argparse # parse commandline arguments

''' DISPLAY PARAMS '''
highlight_color = [214, 39, 112]
secondary_color = [53, 204, 242]
edge_color = [200, 200, 200]

padding_y = 1
responsive_padding = True # Change x padding on terminal resize

color = [90,125,125] # Default starting color
pos = [0, 0] # Default cursor position

''' GLOBALS '''
# These are necessary for the responsiveness thread to work
in_menu = False
padding_x = 1

''' INPUT '''
# Define the getch function used to get keyboard input
# https://stackoverflow.com/a/47548992
if os.name == 'nt':
    import msvcrt
    def getch():
        while True:
            try:
                return msvcrt.getch().decode()
            except UnicodeDecodeError: # A keypress couldn't be decoded, ignore it
                continue
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

''' MISC '''
# Clear the terminal
if os.name == 'nt':
    def clear():
        os.system("cls")
else:
    def clear():
        os.system("clear")

# Hide/show the cursor
def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\x1b[?25h")
    sys.stdout.flush()

''' IMAGE DRAWING '''

# Prints text at x, y with background color
def draw(color, x, y, text, textcolor = None):
    # ANSI Escape sequences
    # Somehow this was easier than curses or rich
    
    # Make text color black if background is too light
    if sum(color) > 350 and textcolor == None:
        text = f"\x1b[38;2;0;0;0m{text}\x1b[0m"
    if textcolor != None:
        text = f"\x1b[38;2;{textcolor[0]};{textcolor[1]};{textcolor[2]}m{text}\x1b[0m"

    if color[0] != -1: # transparent
        color_start = f"\x1b[48;2;{color[0]};{color[1]};{color[2]}m"
        color_end = "\x1b[0m"
    else:
        color_start = ""
        color_end = ""
    position_start = f"\x1b7\x1b[{y};{x}f"
    position_end = "\x1b8"
    sys.stdout.write(color_start+position_start+text+position_end+color_end)

# Draws the image box
def draw_image_box(img):
    global padding_x
    offset_y = 6
    y, x, _ = img.shape
    box_top = "╭"+"─"*(x*2)+"╮"
    box_mid = "│"+" "*(x*2)+"│"
    box_bot = "╰"+"─"*(x*2)+"╯"
    draw([-1],1+padding_x,offset_y+padding_y,box_top,edge_color)
    for i in range(y):
        draw([-1],1+padding_x,offset_y+padding_y+1+i,box_mid,edge_color)
    draw([-1],1+padding_x,offset_y+padding_y+1+y,box_bot,edge_color)

# Prints an image
def draw_image(img, pos):
    offset_y = 6
    y, x, _ = img.shape

    for j in range(y):
        for i in range(x):
            if i == pos[0] and j == pos[1]:
                text = "[]"
            else:
                text = "  "
            draw(img[j][i], i*2+2+padding_x, j+1+offset_y+padding_y, text)
    sys.stdout.flush()

''' FLOOD FILL '''
def flood_fill(pos, img, color, original_color):
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
                img = flood_fill([j,i], np.copy(img), color, original_color)
    return img
    

''' COLOR SELECTION '''
def rgb_to_hsv(color):
    arr = np.uint8([[color]])
    return cv2.cvtColor(arr,cv2.COLOR_RGB2HSV)[0][0]

def hsv_to_rgb(color):
    arr = np.uint8([[color]])
    return cv2.cvtColor(arr,cv2.COLOR_HSV2RGB)[0][0]

#print(hsv_to_rgb([0,0,0]))

# Draws the color selection display
def color_select(color,offset_y=1):
    # Draw the edge box
    section_width = 11
    box_height = 3
    box_top = "╭"+"┬".join(["─"*section_width]*4)+"╮"
    box_mid = "│"+"│".join([" "*section_width]*4)+"│"
    box_bot = "╰"+"┴".join(["─"*section_width]*4)+"╯"

    draw([-1],1+padding_x,1+offset_y+padding_y,box_top,edge_color)
    for i in range(box_height):
        draw([-1],1+padding_x,1+offset_y+padding_y+1+i,box_mid,edge_color)
    draw([-1],1+padding_x,1+offset_y+padding_y+box_height,box_bot,edge_color)

    # Draw instruction text
    instructions = ["[u/j]: hue","[i/k]: sat", "[o/l]: val", "current"]
    for i in range(len(instructions)):
        draw([-1],1+padding_x+1+i*12,1+offset_y+padding_y+1,instructions[i],secondary_color)

    ticks = 10
    # Draw hue display
    #hsv_color = rgb_to_hsv(color)
    hsv_color = color
    for h in range(0,181,180//ticks):
        ncolor = [h,255,255]
        ncolor_rgb = hsv_to_rgb(ncolor)
        if round(hsv_color[0]/18)*18 == h:
            text = "●"
        else:
            text = " "
        draw(ncolor_rgb, h//(180//ticks)+1+padding_x+1, 2+offset_y+padding_y+1, text)

    # Draw sat display
    for s in range(0,251,250//ticks):
        ncolor = hsv_color.copy()
        ncolor[1] = s
        ncolor_rgb = hsv_to_rgb(ncolor)
        # This is not the best way but at this point I'm too tired to care
        if hsv_color[1]//(250/ticks)*250//ticks == s:
            text = "●"
        else:
            text = " "
        draw(ncolor_rgb, s//(250//ticks)+ticks+3+padding_x+1, 2+offset_y+padding_y+1, text)

    # Draw val display
    for v in range(0,251,250//ticks):
        ncolor = hsv_color.copy()
        ncolor[2] = v
        ncolor_rgb = hsv_to_rgb(ncolor)
        if hsv_color[2]//(250/ticks)*250/ticks == v:
            text = "●"
        else:
            text = " "
            #print(hsv_color[2])
        draw(ncolor_rgb,v//(250//ticks)+2*ticks+5+padding_x+1,2+offset_y+padding_y+1,text)
    
    # Draw current color
    draw(hsv_to_rgb(hsv_color),37+padding_x+1,2+offset_y+padding_y+1," "*11)

#color_select([255,200,200])

# Changes hue by amount (returns RGB color)
def change_hue(color, amount):
    hsv_color = color # rgb_to_hsv(color)
    hsv_color[0] += amount
    hsv_color[0] = min(max(0,hsv_color[0]),180)//18*18
    return hsv_color # hsv_to_rgb(hsv_color)

# Changes hue by amount (returns RGB color)
def change_saturation(color, amount):
    hsv_color = color # rgb_to_hsv(color)
    hsv_color[1] += amount
    hsv_color[1] = min(max(0,hsv_color[1]),255)//25*25
    return hsv_color # hsv_to_rgb(hsv_color)

# Changes hue by amount (returns RGB color)
def change_value(color, amount):
    hsv_color = color # rgb_to_hsv(color)
    hsv_color[2] += amount
    hsv_color[2] = min(max(0,hsv_color[2]),255)//25*25
    return hsv_color # hsv_to_rgb(hsv_color)

''' RESPONSIVENESS '''
def resize(filename, img):
    global padding_x, in_menu
    dimensions = [0,0]
    while True:
        # Repaint on window size change
        if os.get_terminal_size() != dimensions and not in_menu:
            clear()
            dimensions = os.get_terminal_size()
            if responsive_padding:
                padding_x = (dimensions[0] - img.shape[1]*2)//2
            draw_image_box(img)
            draw_interface(filename, img)
        time.sleep(0.2)

''' MAIN '''
def draw_interface(filename, img):
    # draws (most of) the paint ui
    # menus are handled separately, and imgbox is drawn separately
    # to reduce flickering
    draw([-1], 1+padding_x, 1+padding_y, f"CMDPXL: {filename} ({img.shape[1]}x{img.shape[0]})", highlight_color)
    color_select(color)
    draw([-1], 1+padding_x, 8+padding_y+img.shape[0], "[wasd] move │ [e] draw    │ [f] fill", secondary_color)
    draw([-1], 1+padding_x, 9+padding_y+img.shape[0], "[z] undo    │ [t] filters │ [esc] quit", secondary_color)
    draw_image(img,pos)

def main():
    global padding_x, padding_y, color, pos, in_menu

    # If no arguments passed, display the welcome menu
    if len(sys.argv) == 1:
        clear()
        draw([-1], 1, 1, "CMDPXL - A TOTALLY PRACTICAL IMAGE EDITOR", highlight_color)
        print()
        print("[O]: Open file")
        print("[C]: Create new file")
        option = " "
        while not option in "oc":
            option = getch().lower()
        filename = input("File name: ")
        if option == "c":
            height = int(input("New image height: "))
            width = int(input("New image width: "))
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("mode", help="'open' or 'create'")
        parser.add_argument("filename", help="name of file to create/open")
        parser.add_argument("-s","--size", help="dimensions of image (if creating); width height", nargs=2, type=int)
        args = parser.parse_args()
        
        option = args.mode
        if not option in ["open","create"]:
            parser.print_help()
            sys.exit()
        
        filename = args.filename
        if args.size:
            width, height = args.size
    
    # Load existing image
    if option.lower() == "o" or option.lower() == "open":
        img = cv2.imread(filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Create new image
    else:
        img = np.zeros((height,width,3), np.uint8)
        img[:,:,:] = 250

    clear()
    hide_cursor()

    history = []

    # Start responsiveness thread
    t = Thread(target = resize, args = [filename, img])
    t.daemon = True
    t.start()

    # Main loop
    while True:
        draw_interface(filename, img)
        m = getch()

        ''' MOVEMENT '''
        if m == "w":
            pos[1] = (pos[1]-1)%img.shape[0]
        if m == "s":
            pos[1] = (pos[1]+1)%img.shape[0]
        if m == "a":
            pos[0] = (pos[0]-1)%img.shape[1]
        if m == "d":
            pos[0] = (pos[0]+1)%img.shape[1]
        
        ''' DRAWING '''
        if m == "e" or m == " ":
            history.append(np.copy(img))
            img[pos[1]][pos[0]] = hsv_to_rgb(color)

        if m == "f":
            history.append(np.copy(img))
            img = flood_fill(pos, img, hsv_to_rgb(color), np.copy(img[pos[1]][pos[0]]))

        if m == "z":
            # Load most recent from history
            if len(history) > 0:
                img = history[-1]
                history.pop(-1)

        ''' COLOR CHANGE '''
        if m == "u":
            color = change_hue(color,-18)
        if m == "i":
            color = change_saturation(color,-25)
        if m == "o":
            color = change_value(color,-25)

        if m == "j":
            color = change_hue(color,18)
        if m == "k":
            color = change_saturation(color,25)
        if m == "l":
            color = change_value(color,25)

        ''' FILTERS '''
        if m == "t":
            in_menu = True

            show_cursor()
            clear()
            draw([-1], 1, 1, "APPLY FILTER", highlight_color)
            print()
            print("[esc]: Return\n")
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
                option = getch().upper()
            clear()
            if option != "\x1b":
                history.append(np.copy(img))
                if option == "I":
                    img = cv2.bitwise_not(img)
                elif option == "B":
                    img = cv2.blur(img,(1,2))
                else:
                    grayscale = cv2.cvtColor(img, cv2.cv2.COLOR_RGB2GRAY)
                    for i in filters:
                        if i[0] == option:
                            filtered = cv2.applyColorMap(grayscale, i[2])
                            filtered = cv2.cvtColor(filtered, cv2.COLOR_BGR2RGB)
                    img = filtered
            hide_cursor()
            draw_image_box(img)

            in_menu = False

        ''' QUIT '''
        if m == "\x1b": # esc
            in_menu = True

            show_cursor()
            clear()
            draw([-1], 1, 1, "QUIT", highlight_color)
            print()
            print("[S]: Save and exit")
            print("[Q]: Quit without saving")
            print("\n[esc]: Cancel")
            option = " "
            while not option in "sq\x1b":
                option = getch().lower()
            clear()
            if option == "s":
                # Convert back to BGR before writing
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                cv2.imwrite(filename, img)
                exit()
            elif option == "q":
                exit()
            hide_cursor()
            draw_image_box(img)

            in_menu = False

if __name__ == "__main__": main()
