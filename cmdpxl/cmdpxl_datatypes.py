class Color:
    def __init__(self, *rgb_colors):
        # Check if passing a tuple with three elements, like on draw_image
        self.r, self.g, self.b = rgb_colors[0] if len(rgb_colors) == 1 else rgb_colors

    def __iter__(self):
        return iter((self.r, self.g, self.b))

    def copy(self):
        return Color(self.r, self.g, self.b)


class Pos:
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y

    def __iter__(self):
        return iter((self.x, self.y))
