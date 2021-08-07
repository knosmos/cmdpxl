import cv2 # Read/write images
import sys # Write to terminal
import os
import numpy as np

''' DISPLAY PARAMS '''
highlight_color = [214, 39, 112]
secondary_color = [53, 204, 242]
edge_color = [77, 77, 77]
padding_x = 1
padding_y = 1

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

''' MAIN '''
def main():
    
    clear()
    draw([-1], 1, 1, "CMDPXL - A TOTALLY PRACTICAL IMAGE EDITOR", highlight_color)
    print()
    print("[O]: Open file")
    print("[C]: Create new file")
    option = " "
    while not option in "ocOC":
        option = getch()
    filename = input("File name: ")
    # Load existing image
    if option.lower() == "o":
        img = cv2.imread(filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Create new image
    else:
        height = int(input("New image height: "))
        width = int(input("New image width: "))
        img = np.zeros((height,width,3), np.uint8)
        img[:,:,:] = 255
    
    # img = np.zeros((6,12,3), np.uint8)
    # img[:,:,:] = 255

    clear()
    hide_cursor()
    pos = [0,0]
    color = [90,125,125]
    draw_image_box(img)

    dimensions = os.get_terminal_size()
    history = []

    while True:
        # Repaint on window size change
        if os.get_terminal_size() != dimensions:
            clear()
            dimensions = os.get_terminal_size()
            draw_image_box(img)

        draw([-1], 1+padding_x, 1+padding_y, f"CMDPXL: {filename} ({img.shape[1]}x{img.shape[0]})", highlight_color)
        color_select(color)
        draw([-1], 1+padding_x, 9+padding_y+img.shape[0], "[wasd]: move | [e]: draw | [z]: undo | [esc]: quit", secondary_color)
        draw_image(img,pos)

        m = getch()

        if m == "w":
            pos[1] = (pos[1]-1)%img.shape[0]
        if m == "s":
            pos[1] = (pos[1]+1)%img.shape[0]
        if m == "a":
            pos[0] = (pos[0]-1)%img.shape[1]
        if m == "d":
            pos[0] = (pos[0]+1)%img.shape[1]
        
        if m == "e":
            history.append(np.copy(img))
            img[pos[1]][pos[0]] = hsv_to_rgb(color)

        if m == "z":
            # Load most recent from history
            if len(history) > 0:
                img = history[-1]
                history.pop(-1)

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

        if m == "\x1b": # esc
            show_cursor()
            clear()
            draw([-1], 1, 1, "QUIT", highlight_color)
            print()
            print("[S]: Save and exit")
            print("[Q]: Quit without saving")
            print("[C]: Cancel")
            option = " "
            while not option in "sqc":
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

if __name__ == "__main__": main()
