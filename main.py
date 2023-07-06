import sys
import pygame as pg
from source.widgets import LoadingAnimation, Background, Button, LoginForm, MessageCore, InputBox, Switch
from source.manager import Settings, EthernetPort, DataBaseCore, AchievementCore
from source.style import COLORS
from platform import system
sys_d_i = system()
VER = "V0.1.3"

API_KEY = {YOUR_KEY}
settings, ethernet = Settings(), EthernetPort(API_KEY)
achievements = AchievementCore(settings, VER, True)
settings.read_init()
pg.init()
glo_cur = int(settings.get("last"))
log_f, last_s = True, False
HX, HY = settings.get("xy")
bor = 12 if sys_d_i != "Windows" else 4
if settings.get("mode") == 1:
    screen = pg.display.set_mode((HX + bor * 2, HY + bor * 2), pg.DOUBLEBUF | pg.NOFRAME)
else:
    screen = pg.display.set_mode((HX + bor * 2, HY + bor * 2), pg.DOUBLEBUF | pg.RESIZABLE)
pg.display.set_icon(pg.image.load("source/trash.png"))
if sys_d_i == "Windows":
    from win32api import RGB
    from win32con import GWL_EXSTYLE, WS_EX_LAYERED, LWA_COLORKEY
    from win32gui import SetWindowLong, SetLayeredWindowAttributes, GetWindowLong

    hwnd = pg.display.get_wm_info()["window"]
    SetWindowLong(hwnd, GWL_EXSTYLE, GetWindowLong(hwnd, GWL_EXSTYLE) | WS_EX_LAYERED)
    SetLayeredWindowAttributes(hwnd, RGB(*COLORS["pal"]), 0, LWA_COLORKEY)

screen_height = pg.display.get_desktop_sizes()[0][1]
main_font = pg.font.Font("source/chat-text-style.ttf", settings.get("ts"))
sys_font = pg.font.Font("source/sys-text-style.ttf", int(settings.get("ts") * 0.8))
ino_font = pg.font.Font("source/sys-text-style.ttf", int(settings.get("ts") * 0.6))
background = Background(screen, bor, bor, HX, HY, COLORS["bgr"], COLORS["pal"], COLORS["bor"])
exit_b = Button(screen, (int(0.75 * HX), int(0.02 * HY), int(0.2 * HX), int(0.07 * HY)), sys_font, COLORS["ex-b"],
                text="res", text_color=COLORS["text-i"])
chn = Switch(screen, (int(0.15 * HX), int(0.02 * HY), int(0.4 * HX), int(0.07 * HY)), COLORS["bor"], COLORS["bgr"],
             COLORS["go-b"])
background.render()
data = None
DATA_BASE = DataBaseCore(ethernet, settings)


def starting():
    global log_f, screen, HX, HY, data, settings, ethernet, background, glo_cur

    def ch_s(fl):
        global log_f
        if fl[0]:
            log_f = False
        login.sta.render(fl[1])

    anim = LoadingAnimation(screen, HX // 4 + bor, (HY - HX // 2) // 2 + bor, HX // 2, HX // 2, pg.image.load("source/loading.png"))
    tt = pg.time.get_ticks()
    login = LoginForm(screen, bor, bor, HX, HY, COLORS["bgr"], COLORS["go-b"], COLORS["text-i"], sys_font, settings)
    log_f, ini = True, (False, "checking..")

    def ch_i(fl):
        ini = fl
        if ini[0]:
            settings.set("hash", data[3]), settings.set("name", data[0]), settings.set("key", data[2])
            settings.save()
            login.sta.render("статус: вход..")
            ethernet.async_login(ch_s, data[0], data[1])
        else:
            login.sta.render(f"статус: {ini[1]}")

    while True:
        screen.fill(COLORS["pal"])
        background.show()
        if log_f:
            login.show(anim.show)
        else:
            anim.show(grad=60)
        if tt + 800 < pg.time.get_ticks() and anim.st == 0 and not log_f:
            anim.finish()
            achievements.e_in() #ach
        elif log_f:
            tt = pg.time.get_ticks()
        if anim.st >= anim.xy[1]:
            DATA_BASE.switch_table(settings.get("key"))
            DATA_BASE.task_download_chat(settings.get("last"))
            glo_cur = int(settings.get("last"))
            return True
        for event in pg.event.get():
            if log_f:
                rez = login.handel_event(event)
                if rez is not None:
                    data = rez
                    ethernet.async_try_int(ch_i)
            if event.type == pg.QUIT:
                return False
            if event.type == pg.WINDOWCLOSE:
                achievements.e_rubi()
                return False
            if event.type == pg.VIDEORESIZE:
                new_width, new_height = event.size
                aspect_ratio = 9 / 16
                if new_height >= screen_height:
                    new_height = screen_height
                new_width = int(new_height * aspect_ratio)
                HX, HY = new_width, new_height
                screen = pg.display.set_mode((HX + bor * 2, HY + bor * 2), pg.DOUBLEBUF | pg.RESIZABLE)
                background.resize(screen, bor, bor, HX, HY), anim.resize(screen, HX // 4 + bor, (HY - HX // 2) // 2 + bor, HX // 2, HX // 2)
                login.resize(screen, bor, bor, HX, HY), settings.set("xy", (HX, HY))
                settings.save()
        pg.display.flip()


def main():
    global screen, HX, HY, settings, ethernet, background, bor, exit_b, last_s, chn, glo_cur
    up_ti, up_tk = pg.time.get_ticks(), pg.time.get_ticks()
    mestab = pg.Surface((HX - bor * 2 - 4, int(HY * 0.85)))
    send_t = InputBox(screen, (bor + 4, int(HY * 0.85), HX - bor * 2, int(HY * 0.1)), main_font, (30, 30, 30), COLORS["bor"], "сообщение")
    iip = settings.get("inverse")
    mesp = MessageCore(mestab, HX - bor * 2, HY - 50, main_font, sys_font, COLORS["mes-f"], settings, DATA_BASE)
    while True:
        screen.fill(COLORS["pal"])
        background.show()
        screen.blit(mestab, (bor + 4, int(HY * 0.09)))
        send_t.show(), chn.show(), exit_b.show()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                settings.save()
                return False
            if event.type == pg.WINDOWCLOSE:
                if not settings.get("acive-rubi"):
                    achievements.e_rubi()
                    settings.save()
                return False
            if event.type == pg.VIDEORESIZE:
                new_width, new_height = event.size
                aspect_ratio = 9 / 16
                if new_height >= screen_height:
                    new_height = screen_height
                new_width = int(new_height * aspect_ratio)
                HX, HY = new_width, new_height
                achievements.e_rz()
                screen = pg.display.set_mode((HX + bor * 2, HY + bor * 2), pg.DOUBLEBUF | pg.RESIZABLE)
                background.resize(screen, bor, bor, HX, HY)
                mestab = pg.Surface((HX - bor * 2 - 4, int(HY * 0.85)))
                mesp = MessageCore(mestab, HX - bor * 2, HY - 50, main_font, sys_font, COLORS["mes-f"], settings, DATA_BASE)
                exit_b.resize(screen, (int(0.75 * HX), int(0.02 * HY), int(0.2 * HX), int(0.07 * HY)))
                chn.resize(screen, (int(0.15 * HX), int(0.02 * HY), int(0.4 * HX), int(0.07 * HY)))
                send_t.resize(screen, (bor + 4, int(HY * 0.85), HX - bor * 2, int(HY * 0.1)))
                settings.save()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_DOWN:
                    glo_cur -= iip
                elif event.key == pg.K_UP:
                    achievements.e_re()
                    glo_cur += iip
                if glo_cur < 0:
                    achievements.e_down()
                    glo_cur = 0
            if exit_b.handle_event(event):
                settings.save()
                return True
            chn.handle_event(event)
            to_send = send_t.handle_event(event)
            if 0 < len(to_send) < 10000:
                ethernet.send_message(to_send, "mes", settings.get("name"), settings.get("key"))
                achievements.e_he()
        if chn.get_finally_state() != last_s:
            last_s = chn.get_finally_state()
            if last_s:
                achievements.e_ca()
                screen = pg.display.set_mode((HX + bor * 2, HY + bor * 2), pg.DOUBLEBUF | pg.NOFRAME)
            else:
                screen = pg.display.set_mode((HX + bor * 2, HY + bor * 2), pg.DOUBLEBUF | pg.RESIZABLE)
            background.resize(screen, bor, bor, HX, HY)
            mestab = pg.Surface((HX - bor * 2 - 4, int(HY * 0.85)))
            mesp = MessageCore(mestab, HX - bor * 2, HY - 50, main_font, sys_font, COLORS["mes-f"], settings, DATA_BASE)
            exit_b.resize(screen, (int(0.75 * HX), int(0.02 * HY), int(0.2 * HX), int(0.07 * HY)))
            chn.resize(screen, (int(0.15 * HX), int(0.02 * HY), int(0.4 * HX), int(0.07 * HY)))
            send_t.resize(screen, (bor + 4, int(HY * 0.85), HX - bor * 2, int(HY * 0.1)))
        if up_ti + 3000 < pg.time.get_ticks():
            up_ti = pg.time.get_ticks()
            mesp.update_data(glo_cur)
        elif up_tk + 100 < pg.time.get_ticks():
            up_tk = pg.time.get_ticks()
            mesp.render_mes(glo_cur)
        pg.display.flip()


if __name__ == '__main__':
    pg.display.set_caption(f"LEMS-{VER}")
    print("https://github.com/TeaGuardian/LEMS")
    """python -m PyInstaller --onefile --noconsole --uac-admin --icon=source/trash.ico --paths venv/Lib/site-packages --hidden-import plyer.platforms.win.notification main.py"""
    """screen = pg.display.set_mode((800, 800), pg.NOFRAME) ethernet.send_message(f"Hello {i}", "mes", settings.get("name"), settings.get("key"))"""
    """
    if not settings.get("acive-"):
        notification.notify(title="", message="", app_name=f"LEMS-{VER}", app_icon="source/trash.ico", timeout=40)
        settings.set("acive-", True)
    """
    run = True
    while run:
        run = starting()
        run = main() if run else False
    settings.save()
    pg.quit()
    sys.exit()
