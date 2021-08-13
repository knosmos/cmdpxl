from pathlib import Path

import click
import cv2  # Read/write images
import sys  # Write to terminal
import os
import numpy as np
import time

from threading import Thread  # Constantly check for terminal size update
from cmdpxl.terminal_io import getch, clear, show_cursor, hide_cursor
from cmdpxl.datatypes import Pos, Color

""" DISPLAY PARAMS """
highlight_color = Color(214, 39, 112)
secondary_color = Color(53, 204, 242)
edge_color = Color(200, 200, 200)

padding_y = 1
responsive_padding = True  # Change x padding on terminal resize

color = Color(90, 125, 125)  # Default starting color
pos = Pos(0, 0)  # Default cursor position

TRANSPARENT = Color(-1, 0, 0)

""" GLOBALS """
# These are necessary for the responsiveness thread to work
in_menu = False
padding_x = 1
img = None

""" IMAGE DRAWING """


def draw(color: Color, text_pos: Pos, text, textcolor: Color = None):
    """
    Prints text at x, y with background color
    :param text_pos:
    :param color:
    :param text:
    :param textcolor:
    :return:
    """
    # ANSI Escape sequences
    # Somehow this was easier than curses or rich

    # Make text color black if background is too light
    if sum(list(color)) > 350 and textcolor is None:
        text = f"\x1b[38;2;0;0;0m{text}\x1b[0m"
    if textcolor is not None:
        text = f"\x1b[38;2;{textcolor.r};{textcolor.g};{textcolor.b}m{text}\x1b[0m"

    if color is not TRANSPARENT:
        color_start = f"\x1b[48;2;{color.r};{color.g};{color.b}m"
        color_end = "\x1b[0m"
    else:
        color_start = ""
        color_end = ""
    position_start = f"\x1b7\x1b[{text_pos.y};{text_pos.x}f"
    position_end = "\x1b8"
    sys.stdout.write(color_start + position_start + text + position_end + color_end)


def draw_image_box(img):
    """
    Draws the image box
    :param img:
    :return:
    """
    global padding_x
    offset_y = 6
    y, x, _ = img.shape
    box_top = "╭" + "─" * (x * 2) + "╮"
    box_mid = "│" + " " * (x * 2) + "│"
    box_bot = "╰" + "─" * (x * 2) + "╯"
    draw(TRANSPARENT, Pos(x=1 + padding_x, y=offset_y + padding_y), box_top, edge_color)
    for i in range(y):
        draw(
            TRANSPARENT,
            Pos(x=1 + padding_x, y=offset_y + padding_y + 1 + i),
            box_mid,
            edge_color,
        )
    draw(
        TRANSPARENT,
        Pos(x=1 + padding_x, y=offset_y + padding_y + 1 + y),
        box_bot,
        edge_color,
    )


def draw_image(img, img_pos: Pos):
    offset_y = 6
    y, x, _ = img.shape

    for j in range(y):
        for i in range(x):
            if i == img_pos.x and j == img_pos.y:
                text = "[]"
            else:
                text = "  "
            draw(
                Color(img[j][i]),
                Pos(x=i * 2 + 2 + padding_x, y=j + 1 + offset_y + padding_y),
                text,
            )
    sys.stdout.flush()


""" FLOOD FILL """


def flood_fill(fill_pos: Pos, img, fill_color: Color, original_color):
    img[fill_pos.y][fill_pos.x] = np.array(list(fill_color))
    neighbors = [
        Pos(fill_pos.y - 1, fill_pos.x),
        Pos(fill_pos.y + 1, fill_pos.x),
        Pos(fill_pos.y, fill_pos.x - 1),
        Pos(fill_pos.y, fill_pos.x + 1),
    ]
    for i, j in neighbors:
        if i >= 0 and j >= 0 and i < img.shape[0] and j < img.shape[1]:
            if np.array_equal(img[i][j], list(original_color)) and not np.array_equal(
                img[i][j], list(fill_color)
            ):
                img = flood_fill(Pos(j, i), np.copy(img), fill_color, original_color)
    return img


""" COLOR SELECTION """


def rgb_to_hsv(color: Color) -> Color:
    arr = np.uint8([[list(color)]])
    r, g, b = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)[0][0]
    return Color(r, g, b)


def hsv_to_rgb(color: Color) -> Color:
    arr = np.uint8([[list(color)]])
    r, g, b = cv2.cvtColor(arr, cv2.COLOR_HSV2RGB)[0][0]
    return Color(r, g, b)


def color_select(color: Color, offset_y=1):
    """
    Draws the color selection display
    :param color:
    :param offset_y:
    :return:
    """
    # Draw the edge box
    section_width = 11
    box_height = 3
    box_top = "╭" + "┬".join(["─" * section_width] * 4) + "╮"
    box_mid = "│" + "│".join([" " * section_width] * 4) + "│"
    box_bot = "╰" + "┴".join(["─" * section_width] * 4) + "╯"

    draw(
        TRANSPARENT,
        Pos(x=1 + padding_x, y=1 + offset_y + padding_y),
        box_top,
        edge_color,
    )
    for i in range(box_height):
        draw(
            TRANSPARENT,
            Pos(x=1 + padding_x, y=1 + offset_y + padding_y + 1 + i),
            box_mid,
            edge_color,
        )
    draw(
        TRANSPARENT,
        Pos(x=1 + padding_x, y=1 + offset_y + padding_y + box_height),
        box_bot,
        edge_color,
    )

    # Draw instruction text
    instructions = ["[u/j]: hue", "[i/k]: sat", "[o/l]: val", "current"]
    for i in range(len(instructions)):
        draw(
            TRANSPARENT,
            Pos(x=1 + padding_x + 1 + i * 12, y=1 + offset_y + padding_y + 1),
            instructions[i],
            secondary_color,
        )

    ticks = 10
    # Draw hue display
    # hsv_color = rgb_to_hsv(color)
    hsv_color = color
    for h in range(0, 181, 180 // ticks):
        ncolor = Color(h, 255, 255)
        ncolor_rgb = hsv_to_rgb(ncolor)
        if round(hsv_color.r / 18) * 18 == h:
            text = "●"
        else:
            text = " "
        draw(
            ncolor_rgb,
            Pos(
                x=h // (180 // ticks) + 1 + padding_x + 1,
                y=2 + offset_y + padding_y + 1,
            ),
            text,
        )

    # Draw sat display
    for s in range(0, 251, 250 // ticks):
        ncolor = hsv_color.copy()
        ncolor.g = s
        ncolor_rgb = hsv_to_rgb(ncolor)
        # This is not the best way but at this point I'm too tired to care
        if hsv_color.g // (250 / ticks) * 250 // ticks == s:
            text = "●"
        else:
            text = " "
        draw(
            ncolor_rgb,
            Pos(
                x=s // (250 // ticks) + ticks + 3 + padding_x + 1,
                y=2 + offset_y + padding_y + 1,
            ),
            text,
        )

    # Draw val display
    for v in range(0, 251, 250 // ticks):
        ncolor = hsv_color.copy()
        ncolor.b = v
        ncolor_rgb = hsv_to_rgb(ncolor)
        if hsv_color.b // (250 / ticks) * 250 / ticks == v:
            text = "●"
        else:
            text = " "
            # print(hsv_color[2])
        draw(
            ncolor_rgb,
            Pos(
                x=v // (250 // ticks) + 2 * ticks + 5 + padding_x + 1,
                y=2 + offset_y + padding_y + 1,
            ),
            text,
        )

    # Draw current color
    draw(
        hsv_to_rgb(hsv_color),
        Pos(x=37 + padding_x + 1, y=2 + offset_y + padding_y + 1),
        " " * 11,
    )


def change_hue(hsv_color: Color, amount: int) -> Color:
    hsv_color.r += amount
    hsv_color.r = min(max(0, hsv_color.r), 180) // 18 * 18
    return hsv_color  # hsv_to_rgb(hsv_color)


def change_saturation(hsv_color: Color, amount: int) -> Color:
    hsv_color.g += amount
    hsv_color.g = min(max(0, hsv_color.g), 255) // 25 * 25
    return hsv_color  # hsv_to_rgb(hsv_color)


def change_value(hsv_color: Color, amount: int) -> Color:
    hsv_color.b += amount
    hsv_color.b = min(max(0, hsv_color.b), 255) // 25 * 25
    return hsv_color


""" RESPONSIVENESS """


def resize(filename: str) -> None:
    global padding_x, in_menu, img
    dimensions = [0, 0]
    while True:
        # Repaint on window size change
        if os.get_terminal_size() != dimensions and not in_menu:
            clear()
            dimensions = os.get_terminal_size()
            if responsive_padding:
                padding_x = (dimensions[0] - max(48, img.shape[1] * 2)) // 2
            draw_image_box(img)
            draw_interface(filename, img)
        time.sleep(0.2)


""" MAIN """


def draw_interface(filename: str, img) -> None:
    """
    Draws (most of) the paint ui. Menus are handled separately, and imgbox is drawn separately to reduce flickering
    :param filename:
    :param img:
    :return:
    """

    draw(
        TRANSPARENT,
        Pos(x=1 + padding_x, y=1 + padding_y),
        f"CMDPXL: {filename} ({img.shape[1]}x{img.shape[0]})",
        highlight_color,
    )
    color_select(color)
    draw(
        TRANSPARENT,
        Pos(x=1 + padding_x, y=8 + padding_y + img.shape[0]),
        "[wasd] move │ [e] draw    │ [f] fill",
        secondary_color,
    )
    draw(
        TRANSPARENT,
        Pos(x=1 + padding_x, y=9 + padding_y + img.shape[0]),
        "[z] undo    │ [t] filters │ [esc] quit",
        secondary_color,
    )
    draw_image(img, pos)


def draw_welcome_msg(func):
    def wrapper():
        clear()
        draw(
            TRANSPARENT,
            Pos(x=1, y=1),
            "CMDPXL - A TOTALLY PRACTICAL IMAGE EDITOR",
            highlight_color,
        )
        print("")
        func()
    return wrapper


@draw_welcome_msg
@click.command(name="cmdpxl")
@click.option(
    "--filepath",
    "-f",
    prompt="File path",
    help="Path for the file you want to open",
    type=click.Path(),
)
@click.option(
    "--resolution",
    "-res",
    help="Image height and width separated by a comma, e.g. 20,10 for a 20x10 image. Note that no spaces can be used.",
)
def main(filepath, resolution):
    global padding_x, padding_y, color, pos, in_menu, img

    # Load existing image
    image_path = Path(filepath)
    if image_path.exists() and image_path.is_file():
        img = cv2.imread(filepath)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Create new image
    else:
        if resolution:
            width, height = map(int, resolution.split(","))
        else:
            width = int(input("New image width: "))
            height = int(input("New image height: "))
        img = np.zeros((height, width, 3), np.uint8)
        img[:, :, :] = 250

    clear()
    hide_cursor()

    history = []

    # Start responsiveness thread
    t = Thread(target=resize, args=[filepath])
    t.daemon = True
    t.start()
    dimensions = os.get_terminal_size()
    padding_x = (dimensions[0] - max(48,img.shape[1] * 2)) // 2

    # Main loop
    while True:
        draw_interface(filepath, img)
        m = getch()

        """ MOVEMENT """
        if m == "w":
            pos.y = (pos.y - 1) % img.shape[0]
        if m == "s":
            pos.y = (pos.y + 1) % img.shape[0]
        if m == "a":
            pos.x = (pos.x - 1) % img.shape[1]
        if m == "d":
            pos.x = (pos.x + 1) % img.shape[1]

        """ DRAWING """
        if m == "e" or m == " ":
            history.append(np.copy(img))
            img[pos.y][pos.x] = list(hsv_to_rgb(color))

        if m == "f":
            history.append(np.copy(img))
            img = flood_fill(pos, img, hsv_to_rgb(color), np.copy(img[pos.y][pos.x]))

        if m == "z":
            # Load most recent from history
            if len(history) > 0:
                img = history[-1]
                history.pop(-1)

        """ COLOR CHANGE """
        if m == "u":
            color = change_hue(color, -18)
        if m == "i":
            color = change_saturation(color, -25)
        if m == "o":
            color = change_value(color, -25)

        if m == "j":
            color = change_hue(color, 18)
        if m == "k":
            color = change_saturation(color, 25)
        if m == "l":
            color = change_value(color, 25)

        """ FILTERS """
        if m == "t":
            in_menu = True

            show_cursor()
            clear()
            draw(TRANSPARENT, Pos(1, 1), "APPLY FILTER", highlight_color)
            print()
            print("[esc]: Return\n")
            filters = [
                ["G", "Grayscale", cv2.COLORMAP_BONE],
                ["S", "Sepia", cv2.COLORMAP_PINK],
                ["O", "Ocean", cv2.COLORMAP_OCEAN],
                ["H", "Heatmap", cv2.COLORMAP_JET],
                ["I", "Invert", None],
                ["B", "Blur", None],
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
                    img = cv2.blur(img, (1, 2))
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

        """ QUIT """
        if m == "\x1b":  # esc
            in_menu = True

            show_cursor()
            clear()
            draw(TRANSPARENT, Pos(x=1, y=1), "QUIT", highlight_color)
            print()
            print("[S]: Save and exit")
            print("[Q]: Quit without saving")
            print("\n[esc]: Cancel")
            option = " "
            while option not in "sq\x1b":
                option = getch().lower()
            clear()
            if option == "s":
                # Convert back to BGR before writing
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                cv2.imwrite(filepath, img)
                exit()
            elif option == "q":
                exit()
            hide_cursor()
            draw_image_box(img)

            in_menu = False


if __name__ == "__main__":
    main()
