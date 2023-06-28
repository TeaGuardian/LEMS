import pygame as pg
import hashlib
from .style import COLORS
lim255 = lambda g: 255 if g > 255 else g if g > 0 else 0
napcon = lambda g: -1 if g < 0 else 1 if g > 0 else 0
anpoi = [(112, 96, 0.02), (102, 90, 0.2), (90, 84, 0.38), (77, 78, 0.52), (62, 72, 0.66), (44, 70, 0.76), (34, 80, 0.8),
         (35, 96, 0.84), (43, 110, 0.87), (52, 120, 0.9), (62, 134, 0.96), (74, 146, 1), (86, 158, 1), (98, 169, 1),
         (101, 172, 1), (111, 181, 1), (127, 193, 1), (142, 205, 1), (156, 217, 1), (171, 229, 1), (187, 240, 1),
         (203, 252, 1), (219, 264, 1), (235, 276, 1), (251, 288, 1), (267, 299, 1), (283, 310, 1), (298, 320, 1),
         (319, 333, 1), (335, 344, 1), (351, 354, 1), (367, 363, 1), (383, 371, 1), (399, 380, 1), (415, 388, 1),
         (425, 392, 1), (439, 398, 1), (454, 402, 0.85), (467, 397, 0.74), (467, 382, 0.62), (461, 370, 0.48),
         (449, 350, 0.28), (443, 343, 0.02)]


class LoadingAnimation:
    def __init__(self, sc, x, y, hx, hy, image):
        self.orig_im = image
        self.col, self.xy, self.dh, self.ss, self.st = (163, 127, 84), (x, y), hy / 500, pg.Surface((hx, hy)), 0
        self.image, self.sc, self.step, self.ti = pg.transform.smoothscale(image, (hx, hy)), sc, 0, pg.time.get_ticks()
        self.run = True
        self.image.set_colorkey((255, 255, 255))

    def render(self):
        global anpoi
        if self.st >= self.xy[1] + self.dh * 500:
            return 1
        self.ss.fill([0, 0, 0])
        self.ss.blit(self.image, (0, 0))
        m, n, r = map(lambda g: g * self.dh, anpoi[self.step])
        pg.draw.circle(self.ss, self.col, (m, n), 18 * r)
        self.ss.set_colorkey([0, 0, 0])
        if self.st != 0:
            self.ss.set_alpha(255 - self.st / (self.xy[1] + self.dh * 500) * 250)
            self.st += (self.xy[1] + self.dh * 500) // 10

    def finish(self):
        self.st = (self.xy[1] + self.dh * 500) // 10

    def show(self, grad=255, pag=None):
        global anpoi
        if self.ti + 40 < pg.time.get_ticks() and self.run:
            self.ti = pg.time.get_ticks()
            if self.step != 0 or self.st == 0:
                self.step += 1
            if self.step >= len(anpoi):
                self.step = 0
            self.render()
        self.ss.set_alpha(grad)
        if pag is None:
            self.sc.blit(self.ss, (self.xy[0], self.xy[1] - self.st))
        else:
            pag.blit(self.ss, (self.xy[0], self.xy[1] - self.st))

    def resize(self, sc, x, y, hx, hy):
        self.sc, self.x, self.y, self.ss, self.image = sc, x, y, pg.Surface((hx, hy)), pg.transform.smoothscale(self.orig_im, (hx, hy))
        self.dh = hy / 500
        self.render()


class Button:
    def __init__(self, screen: pg.Surface, int_rect, font, color, grad=255, text="", text_color=(10, 10, 10),
                 an_col=None, an_li=0.6):
        x, y, sx, sy = int_rect
        an_col = an_col if an_col is not None else color
        self.plot, self.sc, self.llf, self.grad, self.an_flag = pg.Surface((sx, sy)), screen, False, grad, None
        self.x, self.y, self.sx, self.sy, self.col, self.an_plot = x, y, sx, sy, color[:], pg.Surface((sx, sy))
        self.font, self.text, self.text_c, self.an_li, self.an_col_m = font, text, text_color, an_li, an_col
        self.an_cord, self.an_color, self.an_grad, self.an_time = (0, 0), an_col, 0, pg.time.get_ticks()
        self.render(color)

    def render(self, color):
        """updating Button surface"""
        self.plot.fill([0, 0, 0])
        self.plot.set_alpha(self.grad)
        bor = int(min(self.sx, self.sy) * 0.2)
        pg.draw.rect(self.plot, color, (0, 0, self.sx, self.sy), border_radius=bor)
        pg.draw.rect(self.plot, list(map(lambda g: int(g * 0.6), color)), (0, 0, self.sx, self.sy), 2, border_radius=bor)
        text = self.font.render(self.text, True, self.text_c)
        self.plot.blit(text, text.get_rect(center=self.plot.get_rect().center))
        self.plot.set_colorkey([0, 0, 0])
        if self.an_flag is not None:
            self.an_plot.fill([0, 0, 0])
            self.an_plot.set_alpha(self.an_grad)
            pg.draw.circle(self.an_plot, self.an_color, self.an_cord, self.an_flag)
            self.plot.set_colorkey([0, 0, 0])
            if self.an_flag ** 2 > self.sx ** 2 + self.sy ** 2:
                lf = pg.Rect((self.x, self.y, self.sx, self.sy)).collidepoint(pg.mouse.get_pos())
                self.an_flag, self.llf = None, not lf
            elif self.an_time + 30 < pg.time.get_ticks():
                self.an_time = pg.time.get_ticks()
                self.an_flag += 10
            self.plot.blit(self.an_plot, (0, 0), special_flags=pg.BLEND_RGB_SUB)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if pg.Rect((self.x, self.y, self.sx, self.sy)).collidepoint(event.pos):
                self.task_animation(*event.pos, self.an_col_m, 50)
                return True
        if event.type == pg.MOUSEMOTION:
            lf = pg.Rect((self.x, self.y, self.sx, self.sy)).collidepoint(event.pos)
            if lf and not self.llf:
                self.llf = True
                self.render(list(map(lambda g: int(g * 0.7), self.col)))
            elif self.llf and not lf:
                self.llf = False
                self.render(self.col)
        return False

    def show(self):
        if self.an_flag is not None:
            self.render(self.col)
        self.sc.blit(self.plot, (self.x, self.y))

    def task_animation(self, x, y, color, grad=30):
        color = list(map(lambda g: lim255(int(g * self.an_li)), color))
        self.an_grad, self.an_cord, self.an_color, self.an_flag = grad, (x - self.x, y - self.y), color, 0

    def resize(self, sc, int_rect):
        x, y, sx, sy = int_rect
        self.plot, self.sc = pg.Surface((sx, sy)), sc
        self.x, self.y, self.sx, self.sy, self.an_plot = x, y, sx, sy, pg.Surface((sx, sy))
        self.render(self.col)


class Switch:
    """colors should be RGB, grad should be in range(0, 255)"""
    def __init__(self, sc: pg.Surface, int_rect, col_bor, col_off, col_on, border=4, grad=255, state=False, tick_time=20):
        x, y, sx, sy = int_rect
        self.x, self.y, self.sx, self.sy, self.col_bor, self.moo = x, y, sx, sy, col_bor, False
        self.plot, self.col_off, self.col_on, self.state = pg.Surface((sx, sy)), col_off, col_on, state
        self.bor, self.sc, self.grad, self.tk_k = border, sc, grad, tick_time
        self.rad, self.last_tick = (sy - 4 * self.bor) // 2, pg.time.get_ticks()
        self.ma, self.mi = sx - 2 * self.bor - self.rad, 2 * self.bor + self.rad
        self.step, self.las = (sx - 4 * self.bor) // 10, self.ma if state else self.mi
        self.render()

    def render(self):
        """updating Switch surface"""
        po = self.sy // 2
        self.plot.fill([0, 0, 0])
        self.plot.set_alpha(self.grad)
        if self.moo and pg.time.get_ticks() - self.tk_k > self.last_tick:
            self.last_tick = pg.time.get_ticks()
            self.las += self.step // 2 if self.state else -self.step // 2
            if not self.state and self.las in range(self.mi - self.step, self.mi):
                self.moo, self.las = False, self.mi
            if self.state and self.las in range(self.ma, self.ma + self.step):
                self.moo, self.las = False, self.ma
        pg.draw.rect(self.plot, self.col_off, (0, 0, self.sx, self.sy), border_radius=po)
        pg.draw.rect(self.plot, self.col_on, (0, 0, self.las, self.sy), border_top_left_radius=po, border_bottom_left_radius=po)
        pg.draw.rect(self.plot, self.col_bor, (0, 0, self.sx, self.sy), self.bor, border_radius=po)
        pg.draw.circle(self.plot, self.col_bor, (self.las, self.sy // 2), self.rad)
        self.plot.set_colorkey([0, 0, 0])

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if pg.Rect((self.x, self.y, self.sx, self.sy)).collidepoint(event.pos):
                self.switch()

    def switch(self):
        """switching switch state"""
        self.moo, self.state = True, False if self.state else True

    def set_state(self, state):
        """set switch state"""
        self.moo, self.state = self.state != state, state

    def show(self):
        if self.moo:
            self.render()
        self.sc.blit(self.plot, (self.x, self.y))

    def get_real_state(self):
        """returns real switch state"""
        return self.state if not self.moo else not self.state

    def get_finally_state(self):
        """returns finally switch state"""
        return self.state

    def resize(self, sc, int_rect):
        x, y, sx, sy = int_rect
        self.x, self.y, self.sx, self.sy = x, y, sx, sy
        self.plot, self.sc = pg.Surface((sx, sy)), sc
        self.rad, self.last_tick = (sy - 4 * self.bor) // 2, pg.time.get_ticks()
        self.ma, self.mi = sx - 2 * self.bor - self.rad, 2 * self.bor + self.rad
        self.step, self.las = (sx - 4 * self.bor) // 10, self.ma if self.state else self.mi
        self.render()


class ProgressBar:
    def __init__(self, sc, int_rect, col_bor, col_off, col_on, border=4, grad=255, phis_t=0, phis_st=10, show_real=False):
        x, y, sx, sy = int_rect
        self.x, self.y, self.sx, self.sy, self.col_bor, self.phis_t = x, y, sx, sy, col_bor, phis_t
        self.plot, self.col_off, self.col_on, self.phis_lt = pg.Surface((sx, sy)), col_off, col_on, pg.time.get_ticks()
        self.bor, self.sc, self.grad, self.iner, self.phis_st = border, sc, grad, 0, phis_st
        self.ma, self.mi, self.show_real = sx - self.bor, 4 * self.bor, show_real
        self.step, self.las = (self.ma - self.mi) / 100, 0
        self.render()

    def render(self):
        po, now = self.sy // 10, int(self.mi + self.step * self.las)
        now2 = now
        self.plot.fill([0, 0, 0])
        self.plot.set_alpha(self.grad)
        pg.draw.rect(self.plot, self.col_off, (0, 0, self.sx, self.sy), border_radius=po)
        if self.show_real and napcon(now - self.iner) > 0:
            pg.draw.rect(self.plot, list(map(lambda g, g2: (g + g2) // 2, self.col_on, self.col_off)), (0, 0, now, self.sy), border_radius=po)
        if self.phis_t > 0 and self.phis_t + self.phis_lt < pg.time.get_ticks():
            self.phis_lt = pg.time.get_ticks()
            self.iner += napcon(now - self.iner) * self.phis_st * (0 if abs(now - self.iner) <= self.phis_st else 1)
        if self.phis_t > 0:
            now = int(self.iner)
        pg.draw.rect(self.plot, self.col_on, (0, 0, now, self.sy), border_radius=po)
        if self.show_real and napcon(now2 - self.iner) < 0:
            pg.draw.rect(self.plot, list(map(lambda g, g2: (g + g2) // 2, self.col_on, self.col_off)), (0, 0, now2, self.sy), border_radius=po)
        pg.draw.rect(self.plot, self.col_bor, (0, 0, self.sx, self.sy), self.bor, border_radius=po)
        self.plot.set_colorkey([0, 0, 0])

    def show(self):
        if self.phis_t > 0 and self.phis_t + self.phis_lt < pg.time.get_ticks():
            self.render()
        self.sc.blit(self.plot, (self.x, self.y))

    def set_prog(self, per):
        if per > 0 and per <= 100:
            self.las = per
            self.render()

    def add_prog(self, per):
        if per > 0 and self.las + per <= 100:
            self.las += per
            self.render()

    def resize(self, sc, int_rect):
        x, y, sx, sy = int_rect
        self.x, self.y, self.sx, self.sy = x, y, sx, sy
        self.plot, self.sc = pg.Surface((sx, sy)), sc
        self.ma, self.mi = sx - self.bor, 4 * self.bor
        self.step, self.las = (self.ma - self.mi) / 100, 0
        self.render()


class InputBox:
    def __init__(self, sc, int_rect, font, inac_col=(0, 0, 0), ac_col=(0, 0, 0), text='', sub_moo=1):
        x, y, w, h = int_rect
        self.h, self.w, self.x, self.y, self.cur_t, self.cur_s = h, w, x, y, pg.time.get_ticks(), False
        self.color, self.lines, self.plot, self.font = inac_col, [""], pg.Surface((w, h)), font
        self.text, self.hs, self.ls, self.smb = text, font.size("A")[1], font.size("Щ")[0], sub_moo
        self.active, self.cur, self.sc, self.cin, self.cac = False, 0, sc, inac_col, ac_col
        self.lines = self.split_text(text, font)

    def split_text(self, text, font):
        lsmax = self.w - font.size("Щ")[0]
        trf, lp, ste = lsmax / 1.2, 0, 0
        if lsmax < 8:
            print("too small")
        rez, line = [], ""
        for si in text:
            if si == " " and ste == 0:
                continue
            if si == " ":
                lp = ste
            if font.size(line)[0] >= lsmax:
                if ste - lp > trf or ste - lp == 0:
                    rez.append(line)
                    line, ste, lp = "", -1, 0
                else:
                    if lp == 0:
                        lp = len(line)
                    rez.append(line[:lp])
                    line += si
                    line, ste, lp = line[lp:], len(line[lp + 1:]) - 1, 0
            else:
                line += si
            ste += 1
        if line:
            rez.append(line)
        return rez if len(rez) else [""]

    def handle_event(self, event):
        rez = ""
        if event.type == pg.MOUSEBUTTONDOWN:
            if pg.Rect((self.x, self.y, self.w, self.h)).collidepoint(event.pos):
                self.active = not self.active
                self.cur = len(self.text)
            else:
                self.active = False
            self.color = self.cac if self.active else self.cin
        if event.type == pg.KEYDOWN:
            if self.active:
                n = self.cur
                if event.key == pg.K_RETURN and len(self.text):
                    rez = self.text
                    self.text, self.lines, self.cur = '', [""], 0
                elif event.key == pg.K_BACKSPACE and len(self.text):
                    self.text = self.text[:n - 1] + self.text[n:]
                    self.cur -= 1
                    self.lines = self.split_text(self.text, self.font)
                elif event.key == pg.K_LEFT and self.cur > 0:
                    self.cur -= 1
                elif event.key == pg.K_RIGHT and self.cur < len(self.text):
                    self.cur += 1
                elif event.key != pg.K_BACKSPACE:
                    self.text = self.text[:n] + event.unicode + self.text[n:]
                    if len(event.unicode):
                        self.cur += 1
                    self.lines = self.split_text(self.text, self.font)
                le_li = len(self.lines)
                if self.smb == -1:
                    if (self.hs + 2) * le_li > self.h and self.y - (self.hs + 2) * le_li > 0:
                        while (self.hs + 2) * le_li > self.h and self.y - (self.hs + 2) * le_li > 0:
                            self.y -= (self.hs + 2)
                            self.h += (self.hs + 2)
                        self.plot = pg.Surface((self.w, self.h))
                    elif (self.hs + 2) * (le_li + 1) < self.h and le_li:
                        while (self.hs + 2) * (le_li + 1) < self.h and le_li:
                            self.y += (self.hs + 2)
                            self.h -= (self.hs + 2)
                        self.plot = pg.Surface((self.w, self.h))
                elif self.smb == 1:
                    if (self.hs + 2) * le_li > self.h:
                        while (self.hs + 2) * le_li > self.h:
                            self.h += (self.hs + 2)
                        self.plot = pg.Surface((self.w, self.h))
                    elif (self.hs + 2) * (le_li + 1) < self.h and le_li:
                        while (self.hs + 2) * (le_li + 1) < self.h and le_li:
                            self.h -= (self.hs + 2)
                        self.plot = pg.Surface((self.w, self.h))
        if self.y - (self.hs + 2) * len(self.lines) <= 0:
            yc, yd = int((self.find_cur()[1] - 2) / (self.hs + 2)), int(self.h / (self.hs + 2))
            sp, ep = yc - yd + yd // 2, yc + yd // 2
            lines = self.lines[sp if sp > 0 else 0:ep if ep < len(self.lines) else None]
        else:
            lines = self.lines
        self.plot.fill((0, 0, 0))
        self.plot.set_colorkey((0, 0, 0))
        for i, s in enumerate(lines):
            self.plot.blit(self.font.render(s, True, self.color), (2 + self.ls // 4, self.hs // 8 + (self.hs + 2) * i))
        pg.draw.rect(self.plot, self.color, (0, 0, self.w, self.h - 4), 2)
        return rez

    def find_cur(self):
        y, pp = 0, 0
        for i in self.lines:
            if self.cur > pp + len(i) + 1:
                y += 1
                pp += len(i)
        return self.font.size(self.lines[y][:self.cur - pp])[0], 2 + (self.hs + 2) * y

    def show(self):
        self.sc.blit(self.plot, (self.x, self.y))
        if self.active:
            if self.cur_t + 600 < pg.time.get_ticks():
                self.cur_t, self.cur_s = pg.time.get_ticks(), not self.cur_s
            if self.cur_s:
                dx, dy = self.find_cur()
                x, y = 2 + self.ls // 4 + self.x + dx, 2 + self.y + dy
                if self.y - (self.hs + 2) * len(self.lines) <= 0:
                    p = int(self.h / (self.hs + 2)) - int(self.h / (self.hs + 2)) // 2
                    y = 4 + self.y + p * (self.hs + 2)
                pg.draw.rect(self.sc, self.color, (x, y + self.hs // 8 - 2, 2, self.hs - 6))

    def resize(self, sc, int_rect):
        self.x, self.y, self.w, self.h = int_rect
        self.plot, self.sc = pg.Surface((self.w, self.h)), sc


class TextBox:
    def __init__(self, sc, int_rect, font, col=(0, 0, 0), text='', sub_moo=1):
        self.x, self.y, self.w, self.h = int_rect
        self.color, self.plot, self.font, self.smb = col, pg.Surface((self.w, self.h)), font, sub_moo
        self.text, self.hs, self.ls = text, font.size("A")[1], font.size("Щ")[0]
        self.sc = sc
        self.render(text)

    def split_text(self, text, font):
        lsmax = self.w - font.size("Щ")[0]
        trf, lp, ste = lsmax / 1.2, 0, 0
        if lsmax < 8:
            print("too small")
        rez, line = [], ""
        for si in text:
            if si == " " and ste == 0:
                continue
            if si == " ":
                lp = ste
            if font.size(line)[0] >= lsmax:
                if ste - lp > trf or ste - lp == 0:
                    rez.append(line)
                    line, ste, lp = "", -1, 0
                else:
                    if lp == 0:
                        lp = len(line)
                    rez.append(line[:lp])
                    line += si
                    line, ste, lp = line[lp:], len(line[lp + 1:]) - 1, 0
            else:
                line += si
            ste += 1
        if line:
            rez.append(line)
        return rez if len(rez) else [""]

    def render(self, text):
        self.text = text
        lines = self.split_text(self.text, self.font)
        le_li = len(lines)
        if self.smb == -1:
            if (self.hs + 2) * le_li > self.h and self.y - (self.hs + 2) * le_li > 0:
                while (self.hs + 2) * le_li > self.h and self.y - (self.hs + 2) * le_li > 0:
                    self.y -= (self.hs + 2)
                    self.h += (self.hs + 2)
                self.plot = pg.Surface((self.w, self.h))
            elif (self.hs + 2) * (le_li + 1) < self.h and le_li:
                while (self.hs + 2) * (le_li + 1) < self.h and le_li:
                    self.y += (self.hs + 2)
                    self.h -= (self.hs + 2)
                self.plot = pg.Surface((self.w, self.h))
        elif self.smb == 1:
            if (self.hs + 2) * le_li > self.h:
                while (self.hs + 2) * le_li > self.h:
                    self.h += (self.hs + 2)
                self.plot = pg.Surface((self.w, self.h))
            elif (self.hs + 2) * (le_li + 1) < self.h and le_li:
                while (self.hs + 2) * (le_li + 1) < self.h and le_li:
                    self.h -= (self.hs + 2)
                self.plot = pg.Surface((self.w, self.h))
        self.plot.fill((0, 0, 0))
        self.plot.set_colorkey((0, 0, 0))
        for i, s in enumerate(lines):
            self.plot.blit(self.font.render(s.lstrip(" "), True, self.color), (2 + self.ls // 4, self.hs // 8 + (self.hs + 2) * i))
        #pg.draw.rect(self.plot, self.color, (0, 0, self.w, self.h - 4), 2)

    def show(self):
        self.sc.blit(self.plot, (self.x, self.y))

    def resize(self, sc, int_rect):
        self.x, self.y, self.w, self.h = int_rect
        self.plot, self.sc = pg.Surface((self.w, self.h)), sc
        self.render(self.text)


class Background:
    def __init__(self, sc, x, y, hx, hy, bg, tdl, br, grad=255):
        self.sc, self.hx, self.hy, self.bg, self.br, self.plot, self.tdl = sc, hx, hy, bg, br, pg.Surface((hx, hy)), tdl
        self.grad, self.x, self.y = grad, x, y

    def render(self):
        r = int(min(self.hx, self.hy) * 0.1)
        self.plot.fill(self.tdl)
        pg.draw.rect(self.plot, self.bg, (0, 0, self.hx, self.hy), border_radius=r)
        pg.draw.rect(self.plot, self.br, (0, 0, self.hx, self.hy), 2, border_radius=r)
        self.plot.set_alpha(self.grad)

    def show(self):
        self.sc.blit(self.plot, (self.x, self.y))

    def resize(self, sc, x, y, hx, hy):
        self.sc, self.hx, self.hy, self.plot = sc, hx, hy, pg.Surface((hx, hy))
        self.x, self.y = x, y
        self.render()


class LoginForm:
    def __init__(self, sc, x, y, hx, hy, fon_c, but_c, txt_c, font, settings):
        self.sc, self.hx, self.hy, self.fon_c, self.but_c, self.txt_c = sc, hx, hy, fon_c, but_c, txt_c
        self.plot, self.sets, self.font, self.x, self.y = pg.Surface((hx, hy)), settings, font, x, y
        self.name, self.pasw, self.key = "имя енота", "пароль енота", "ключ енота"
        if not settings.is_normal():
            n, p, k = "имя енота", "пароль енота", "ключ енота"
        else:
            n, p, k = settings.get("name"), settings.get("hash"), settings.get("key")
        lif = (163, 127, 84)
        self.fon = Background(self.plot, 0, 0, hx, hy, fon_c, (0, 0, 0), COLORS["bor"])
        self.fon.render()
        ina = (10, 10, 10)
        self.te1 = TextBox(self.plot, (int(0.05 * hx) + x, int(0.1 * hx) + y, int(0.85 * hx), int(0.12 * hx)), font, COLORS["bor"])
        self.sta = TextBox(self.plot, (int(0.05 * hx) + x, int(0.6 * hy) + y, int(0.85 * hx), int(0.12 * hx)), font, COLORS["bor"])
        self.te_n = InputBox(self.plot, (int(0.05 * hx) + x, int(0.2 * hy) + y, int(0.85 * hx), int(0.12 * hx)), font, ina, lif, n, sub_moo=1)
        self.te_p = InputBox(self.plot, (int(0.05 * hx) + x, int(0.3 * hy) + y, int(0.85 * hx), int(0.12 * hx)), font, ina, lif, p, sub_moo=1)
        self.te_k = InputBox(self.plot, (int(0.05 * hx) + x, int(0.4 * hy) + y, int(0.85 * hx), int(0.12 * hx)), font, ina, lif, k, sub_moo=1)
        self.te1.render("регистрация и вход енота"), self.sta.render("статус: waiting..")
        self.ok = Button(self.plot, (int(0.5 * hx) + x, int(0.5 * hy) + y, int(0.4 * hx), int(0.1 * hx)), font, lif, 255, "енот!", ina)

    def handel_event(self, event):
        n, p, k = self.te_n.handle_event(event), self.te_p.handle_event(event), self.te_k.handle_event(event)
        rez = self.ok.handle_event(event)
        if event.type == pg.MOUSEBUTTONDOWN:
            m = hashlib.sha256()
            m.update(self.te_p.text.encode())
            self.name, self.pasw, self.key = self.te_n.text, m.hexdigest(), self.te_k.text
        if n != "":
            self.te_n.text, self.te_n.active, self.te_p.active, self.te_p.cur = n, False, True, len(self.te_p.text)
            self.te_n.lines, self.te_n.color, self.te_p.color = self.te_n.split_text(n, self.te_n.font), self.te_n.cin, self.te_p.cac
            self.te_n.handle_event(event)
        if p != "":
            self.te_p.text, self.te_p.active, self.te_k.active, self.te_k.cur = p, False, True, len(self.te_k.text)
            self.te_p.lines, self.te_p.color, self.te_k.color = self.te_p.split_text(p, self.te_p.font), self.te_p.cin, self.te_k.cac
            self.te_p.handle_event(event)
        if k != "":
            self.te_k.text, self.te_k.active = k, False
            self.te_k.lines, self.te_k.color = self.te_k.split_text(k, self.te_k.font), self.te_k.cin
            self.te_k.handle_event(event)
        if rez and self.name and self.pasw and self.key:
            self.sta.render("статус: checking..")
            return self.name, self.pasw, self.key, self.te_p.text
        return None

    def show(self, anim=None):
        self.fon.show()
        if anim is not None:
            anim(30, self.plot)
        self.te1.show(), self.te_k.show(), self.te_n.show(), self.te_p.show()
        self.ok.show(), self.sta.show()
        self.sc.blit(self.plot, (self.x, self.y))

    def resize(self, sc, x, y, hx, hy):
        self.sc, self.hx, self.hy = sc, hx, hy
        self.plot, self.x, self.y = pg.Surface((hx, hy)), x, y
        self.fon.resize(self.plot, 0, 0, hx, hy), self.ok.resize(self.plot, (int(0.5 * hx) + x, int(0.5 * hy) + y, int(0.4 * hx), int(0.1 * hx)))
        self.te1.resize(self.plot, (int(0.05 * hx) + x, int(0.1 * hx) + y, int(0.85 * hx), int(0.12 * hx)))
        self.sta.resize(self.plot, (int(0.05 * hx) + x, int(0.6 * hy) + y, int(0.85 * hx), int(0.12 * hx)))
        self.te_n.resize(self.plot, (int(0.05 * hx) + x, int(0.2 * hy) + y, int(0.85 * hx), int(0.12 * hx)))
        self.te_p.resize(self.plot, (int(0.05 * hx) + x, int(0.3 * hy) + y, int(0.85 * hx), int(0.12 * hx)))
        self.te_k.resize(self.plot, (int(0.05 * hx) + x, int(0.4 * hy) + y, int(0.85 * hx), int(0.12 * hx)))


class TextMessage:
    def __init__(self, x, y, sx, sy, font, font2, bgc, mes, owner, date):
        self.plot, self.font, self.bgc, self.sx, self.sy = pg.Surface((sx, sy)), font, bgc, sx, sy
        self.x, self.y, self.mes, self.ow, self.date = x, y, mes, owner, date
        self.info = TextBox(self.plot, (2, 2, sx - 4, 10), font2, COLORS["text-i"], "")
        self.cont = TextBox(self.plot, (2, 25, sx - 4, 10), self.font, COLORS["text-a"], "")
        self.render()

    def render(self, sf=False):
        r = int(min(self.sx, self.sy) * 0.1)
        self.plot.fill(COLORS["pal"])
        self.info.render(f"{self.ow}({self.date}):"), self.cont.render(self.mes)
        if self.cont.h + self.info.h != self.sy - 4:
            self.sy = self.cont.h + self.info.h + 6
            self.plot = pg.Surface((self.sx, self.sy))
            vrt = self.info.h
            self.info.resize(self.plot, (2, 2, self.sx - 4, vrt))
            self.cont.resize(self.plot, (2, vrt + 2, self.sx - 4, self.sy - vrt - 4))
        bgc = list(map(lambda g: (g + 100) // 2, self.bgc)) if sf else self.bgc
        pg.draw.rect(self.plot, bgc, (0, 0, self.sx, self.sy), border_radius=r)
        self.info.show(), self.cont.show()
        self.plot.set_colorkey(COLORS["pal"])
        return self.plot


class MessageCore:
    def __init__(self, sc, sx, sy, font, font2, bgc, settings, db):
        self.sc, self.sx, self.sy, self.font, self.font2 = sc, sx, sy, font, font2
        self.bgc, self.settings, self.db, self.data = bgc, settings, db, []
        self.myname = settings.get("name")
        self.surmes = []

    def text_mes_wrap(self, sx, mes, owner, date, sf=False):
        color = self.bgc if self.myname != owner else COLORS["mes-f-a"]
        mes_o = TextMessage(0, 0, sx - 4, 10, self.font, self.font2, color, mes, owner, date)
        return mes_o.render(sf)

    def render_mes(self, foc):
        self.sc.fill(COLORS["bgr"])
        if len(self.data) == 0:
            return False
        self.surmes = []
        y = 0
        for i in self.data:
            rez = self.text_mes_wrap(self.sx, i[1], i[3], i[4], int(i[0]) == foc)
            self.surmes.append(rez)
            if int(i[0]) < foc:
                y -= rez.get_height()
        mh = self.sc.get_height()
        for i in self.surmes:
            h = i.get_height()
            if y + h < 0 or y + h > mh:
                y += h
                continue
            else:
                self.sc.blit(i, (0, y))
                y += h + 4
        self.sc.set_colorkey(COLORS["bgr"])

    def update_data(self, idd):
        self.render_mes(idd)
        self.db.task_download_chat(idd)
        self.data = self.db.get_buffer()[:]

    def resize(self, sc, sx, sy):
        self.sc, self.sx, self.sy = sc, sx, sy

