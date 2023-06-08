from .widgets import Switch, Button, ProgressBar


COLORS = {"wh": (30, 30, 30), "gr": (150, 150, 150), "fn": (90, 100, 90), "li": (255, 230, 190),
          'grey': (150, 150, 150), 'lilac': (100, 130, 250), 'red': (250, 40, 80),
          'blue': (40, 120, 200), 'dark': (60, 60, 60), 'green': (40, 250, 80),
          'yellow': (240, 200, 10), 'meddle': (90, 90, 100), 'dark_blue': (30, 90, 150), 'white': (255, 255, 255),
          'black': (0, 0, 0), 'orange': (180, 120, 40), 'dark_green': (20, 120, 60)}


def lim_255(g):
    if g > 255:
        return 255
    elif g < 0:
        return 0
    return g


def switch_catcher(pos_x: int, pos_y: int, pressed: bool, switch: Switch):
    sel = switch.show(pos_x, pos_y)
    if pressed and sel:
        switch.switch()


def button_catcher(pos_x: int, pos_y: int, pressed: bool, button: Button, color=None, light=0.6):
    sel = button.show(pos_x, pos_y)
    if color is None:
        color = button.col[:]
    color = list(map(lambda g: lim_255(int(g * light)), color))
    if pressed and sel:
        button.task_animation(pos_x, pos_y, color, 50)
        return True
    return False
