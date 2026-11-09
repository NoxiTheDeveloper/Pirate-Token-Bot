import ctypes, math, os, random, sys, threading, time
from ctypes import wintypes
import cv2, mss, numpy as np, pydirectinput

here = os.path.dirname(os.path.abspath(__file__))
pydirectinput.PAUSE = 0.01
pydirectinput.FAILSAFE = True

MATCH = 0.75
SCAN = (0.12, 0.25)
ARM_FOR = 45
COOLDOWN = 10
CLICK_GAP = 1.5
ESC_WAIT = 4
ESC_TRIES = 3

REACT = (0.25, 0.7)
AFTER_ESC = (0.4, 0.8)
BEFORE_CLICK = (0.08, 0.25)
CLICK_HOLD = (0.05, 0.12)
TAP_HOLD = (0.05, 0.11)

IDLE_AFTER = 1.0
HOLD = (0.8, 3.0)
COMBOS = [("w",), ("w",), ("w",), ("w", "a"), ("w", "d"), ("a",), ("d",), ("s",)]
JUMP = (6, 12)
LOOK = (2.5, 6)
USER_WAIT = 20

ANYTIME = {"ready"}

NAMES = {
    "placed": "the YOU PLACED text (just the words, not the number)",
    "menu": "the 3 lines button",
    "lobby": "the Return to Lobby button",
    "ready": "the yellow READY button",
}
SAY = {"menu": "3 lines", "lobby": "Return to Lobby", "ready": "READY"}

sct = (mss.MSS if hasattr(mss, "MSS") else mss.mss)()
MON = sct.monitors[1]
u32 = ctypes.windll.user32
k32 = ctypes.windll.kernel32


def r(a):
    return random.uniform(*a)


def wait(a):
    time.sleep(r(a))


def down(vk):
    return bool(u32.GetAsyncKeyState(vk) & 0x8000)


def mousepos():
    p = wintypes.POINT()
    u32.GetCursorPos(ctypes.byref(p))
    return p.x, p.y


def shot():
    return cv2.cvtColor(np.array(sct.grab(MON)), cv2.COLOR_BGRA2BGR)


last_real = 0.0
LRES = ctypes.c_ssize_t
HOOK = ctypes.WINFUNCTYPE(LRES, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
u32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
u32.CallNextHookEx.restype = LRES
u32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOK, ctypes.c_void_p, wintypes.DWORD]
u32.SetWindowsHookExW.restype = ctypes.c_void_p
k32.GetModuleHandleW.restype = ctypes.c_void_p


class MS(ctypes.Structure):
    _fields_ = [("pt", wintypes.POINT), ("data", wintypes.DWORD), ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("extra", ctypes.c_size_t)]


class KB(ctypes.Structure):
    _fields_ = [("vk", wintypes.DWORD), ("scan", wintypes.DWORD), ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("extra", ctypes.c_size_t)]


def mouse_cb(n, w, l):
    global last_real
    if n >= 0 and not (ctypes.cast(l, ctypes.POINTER(MS)).contents.flags & 0x01):
        last_real = time.time()
    return u32.CallNextHookEx(None, n, w, l)


def key_cb(n, w, l):
    global last_real
    if n >= 0:
        k = ctypes.cast(l, ctypes.POINTER(KB)).contents
        if not (k.flags & 0x10) and k.vk not in (0x77, 0x78):
            last_real = time.time()
    return u32.CallNextHookEx(None, n, w, l)


def hooks():
    m, k = HOOK(mouse_cb), HOOK(key_cb)
    h = k32.GetModuleHandleW(None)
    u32.SetWindowsHookExW(14, m, h, 0)
    u32.SetWindowsHookExW(13, k, h, 0)
    msg = wintypes.MSG()
    while u32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        u32.TranslateMessage(ctypes.byref(msg))
        u32.DispatchMessageW(ctypes.byref(msg))


def path(n):
    return os.path.join(here, n + ".png")


def findfile(n):
    key = n.lower().replace("_", "")
    got = None
    for f in os.listdir(here):
        low = f.lower()
        if not low.endswith((".png", ".jpg", ".jpeg")):
            continue
        stem = low.split(".")[0].replace("_", "").replace(" ", "").replace("-", "")
        if stem == key or (n == "lobby" and stem == "returntolobby"):
            if low == n + ".png":
                return os.path.join(here, f)
            got = got or os.path.join(here, f)
    return got


def files():
    print("folder:", here)
    for f in sorted(os.listdir(here)):
        print("   ", f)
    print()
    for n in NAMES:
        print(f"{n:8} -> {findfile(n) or 'NOT FOUND'}")


def pick(img, title):
    sc = min(1.0, 1600 / img.shape[1], 900 / img.shape[0])
    view = cv2.resize(img, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA) if sc < 1 else img.copy()
    dim = (view * 0.35).astype(np.uint8)
    st = {"a": None, "b": None, "drag": False}
    win = "select " + title

    def mouse(ev, x, y, fl, pr):
        if ev == cv2.EVENT_LBUTTONDOWN:
            st["a"], st["b"], st["drag"] = (x, y), (x, y), True
        elif ev == cv2.EVENT_MOUSEMOVE and st["drag"]:
            st["b"] = (x, y)
        elif ev == cv2.EVENT_LBUTTONUP and st["drag"]:
            st["b"], st["drag"] = (x, y), False

    def box():
        if not st["a"] or not st["b"]:
            return None
        x1, x2 = sorted((max(0, st["a"][0]), max(0, st["b"][0])))
        y1, y2 = sorted((max(0, st["a"][1]), max(0, st["b"][1])))
        x2, y2 = min(x2, view.shape[1]), min(y2, view.shape[0])
        return (x1, y1, x2, y2) if x2 - x1 > 3 and y2 - y1 > 3 else None

    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(win, mouse)
    try:
        cv2.setWindowProperty(win, cv2.WND_PROP_TOPMOST, 1)
    except cv2.error:
        pass

    out = None
    while True:
        f = dim.copy()
        b = box()
        if b:
            x1, y1, x2, y2 = b
            f[y1:y2, x1:x2] = view[y1:y2, x1:x2]
            cv2.rectangle(f, (x1, y1), (x2, y2), (0, 255, 0), 2)
            msg = f"{int((x2 - x1) / sc)}x{int((y2 - y1) / sc)}px - ENTER to save"
        else:
            msg = "drag over the button"
        cv2.rectangle(f, (0, 0), (f.shape[1], 30), (0, 0, 0), -1)
        cv2.putText(f, f"{title} | {msg} | R=redo ESC=skip", (8, 21),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow(win, f)
        k = cv2.waitKey(15) & 0xFF
        if k in (13, 32) and b:
            x1, y1, x2, y2 = b
            out = (int(x1 / sc), int(y1 / sc), int((x2 - x1) / sc), int((y2 - y1) / sc))
            break
        if k in (ord("r"), ord("R")):
            st.update(a=None, b=None, drag=False)
        if k == 27:
            break
        try:
            if cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) < 1:
                break
        except cv2.error:
            break
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    return out


def setup(n, src=None):
    print(f"\n== {n}: {NAMES[n]} ==")
    if src:
        img = cv2.imread(src)
        if img is None:
            print("cant read", src)
            return
    else:
        print("get it on screen then hit F8...")
        while down(0x77):
            time.sleep(0.05)
        while not down(0x77):
            time.sleep(0.03)
        img = shot()
    b = pick(img, n)
    if not b:
        print("skipped")
        return
    x, y, w, h = b
    cv2.imwrite(path(n), img[y:y + h, x:x + w])
    print(f"saved {path(n)} ({w}x{h})")


imgs = {}


def load():
    miss = [n for n in NAMES if not findfile(n)]
    if miss:
        print("missing:", ", ".join(miss), "- looked in", here)
        if input("grab them now? (y/n): ").strip().lower() != "y":
            print("try: python bot.py files   or   python bot.py setup")
            sys.exit(1)
        for n in miss:
            setup(n)
    for n in NAMES:
        p = findfile(n)
        im = cv2.imread(p, cv2.IMREAD_GRAYSCALE) if p else None
        if im is None:
            print(f"cant load {n} ({p}), run: python bot.py setup {n}")
            sys.exit(1)
        imgs[n] = im
        print(f"loaded {n}: {os.path.basename(p)} {im.shape[1]}x{im.shape[0]}")


def scan():
    scr = cv2.cvtColor(shot(), cv2.COLOR_BGR2GRAY)
    out = {}
    for n, t in imgs.items():
        if t.shape[0] > scr.shape[0] or t.shape[1] > scr.shape[1]:
            out[n] = (0, 0, 0.0)
            continue
        res = cv2.matchTemplate(scr, t, cv2.TM_CCOEFF_NORMED)
        _, best, _, loc = cv2.minMaxLoc(res)
        h, w = t.shape
        out[n] = (MON["left"] + loc[0] + w // 2, MON["top"] + loc[1] + h // 2, best)
    return out


def bez(a, b, c, d, t):
    u = 1 - t
    return (u**3 * a[0] + 3 * u * u * t * b[0] + 3 * u * t * t * c[0] + t**3 * d[0],
            u**3 * a[1] + 3 * u * u * t * b[1] + 3 * u * t * t * c[1] + t**3 * d[1])


def curve(a, b, jit=1.0):
    sx, sy = a
    ex, ey = b
    d = math.hypot(ex - sx, ey - sy)
    if d < 2:
        pydirectinput.moveTo(int(ex), int(ey), _pause=False)
        return
    nx, ny = -(ey - sy) / d, (ex - sx) / d
    bend = d * random.uniform(0.05, 0.2) * random.choice((-1, 1))
    p1 = (sx + (ex - sx) * 0.3 + nx * bend, sy + (ey - sy) * 0.3 + ny * bend)
    p2 = (sx + (ex - sx) * 0.7 + nx * bend * 0.6, sy + (ey - sy) * 0.7 + ny * bend * 0.6)
    n = int(max(14, min(70, d / 12)))
    dur = 0.18 + d / 2600 + random.uniform(0.05, 0.2)
    for i in range(1, n + 1):
        t = i / n
        t = t * t * (3 - 2 * t)
        x, y = bez(a, p1, p2, b, t)
        if i < n:
            x += random.uniform(-jit, jit)
            y += random.uniform(-jit, jit)
        pydirectinput.moveTo(int(x), int(y), _pause=False)
        time.sleep(dur / n * random.uniform(0.7, 1.3))


def goto(x, y):
    s = mousepos()
    if random.random() < 0.25 and math.hypot(x - s[0], y - s[1]) > 150:
        ang = math.atan2(y - s[1], x - s[0])
        o = random.uniform(5, 14)
        ox, oy = x + math.cos(ang) * o, y + math.sin(ang) * o
        curve(s, (ox, oy))
        time.sleep(random.uniform(0.04, 0.12))
        curve((ox, oy), (x, y), 0.4)
    else:
        curve(s, (x, y))


def click(n, x, y):
    h, w = imgs[n].shape
    x += random.randint(-int(w * 0.25), int(w * 0.25))
    y += random.randint(-int(h * 0.25), int(h * 0.25))
    goto(x, y)
    wait(BEFORE_CLICK)
    pydirectinput.mouseDown(_pause=False)
    wait(CLICK_HOLD)
    pydirectinput.mouseUp(_pause=False)


def tap(k):
    pydirectinput.keyDown(k, _pause=False)
    wait(TAP_HOLD)
    pydirectinput.keyUp(k, _pause=False)


cam_y = 0


def look():
    global cam_y
    dx = random.randint(80, 420) * random.choice((-1, 1))
    dy = int(-cam_y * 0.5 + random.randint(-35, 35))
    cam_y += dy
    n = random.randint(12, 28)
    px = py = 0
    for i in range(1, n + 1):
        t = i / n
        t = t * t * (3 - 2 * t)
        tx, ty = int(dx * t), int(dy * t)
        pydirectinput.moveRel(tx - px, ty - py, relative=True, _pause=False)
        px, py = tx, ty
        time.sleep(random.uniform(0.012, 0.03))


class Idle:
    def __init__(self):
        self.held = set()
        self.sw = 0.0
        self.nj = 0.0
        self.nl = 0.0
        self.on = True

    def release(self):
        for k in list(self.held):
            pydirectinput.keyUp(k, _pause=False)
        self.held.clear()

    def reset(self):
        self.nj = 0.0
        self.nl = 0.0

    def keys(self, now):
        if now < self.sw and self.held:
            return
        self.release()
        if random.random() < 0.12:
            self.sw = now + random.uniform(0.3, 0.9)
            return
        for k in random.choice(COMBOS):
            pydirectinput.keyDown(k, _pause=False)
            self.held.add(k)
        self.sw = now + r(HOLD)

    def jump(self, now):
        if self.nj == 0.0:
            self.nj = now + r(JUMP)
        elif now >= self.nj:
            tap("space")
            self.nj = time.time() + r(JUMP)

    def glance(self, now):
        if self.nl == 0.0:
            self.nl = now + r(LOOK)
        elif now >= self.nl:
            look()
            self.nl = time.time() + r(LOOK)


def run():
    load()
    threading.Thread(target=hooks, daemon=True).start()
    print("\nscanning... (F9 = idle on/off, ctrl+c = stop)")
    print("clicked whenever seen:", ", ".join(ANYTIME) or "nothing")

    idle = Idle()
    arm_end = rest = esc_at = 0.0
    lastclick = {}
    tries = 0
    seen_at = time.time()
    f9p = False
    wasuser = False
    ready_done = False
    ready_at = 0.0

    try:
        while True:
            now = time.time()

            f9 = down(0x78)
            if f9 and not f9p:
                idle.on = not idle.on
                if not idle.on:
                    idle.release()
                print("idle", "on" if idle.on else "off")
            f9p = f9

            hits = scan()
            seen = {n: (x, y) for n, (x, y, s) in hits.items() if s >= MATCH}
            armed = now < arm_end
            if seen:
                seen_at = now

            if ready_done and now - ready_at > 300:
                ready_done = False

            user = now - last_real < USER_WAIT
            if user != wasuser:
                print("you're on, bot idle paused" if user else "no input for a bit, idle back on")
                wasuser = user

            if user or seen or armed:
                idle.release()
                idle.reset()

            if "placed" in seen and not armed and now >= rest:
                print("YOU PLACED -> leaving")
                ready_done = False
                arm_end = now + ARM_FOR
                tries = 1
                wait(REACT)
                tap("esc")
                esc_at = time.time()
                wait(AFTER_ESC)
                continue

            did = False
            for n in ("ready", "lobby", "menu"):
                if n not in seen:
                    continue
                if n == "ready" and ready_done:
                    continue
                if not (armed or (n in ANYTIME and not user)):
                    continue
                if now - lastclick.get(n, 0) < CLICK_GAP:
                    continue
                print("  see", SAY[n], "-> click")
                idle.release()
                wait(REACT)
                click(n, *seen[n])
                lastclick[n] = time.time()
                if n == "ready":
                    ready_done = True
                    ready_at = time.time()
                did = True
                if n == "ready" and armed:
                    print("  done\n")
                    arm_end = 0.0
                    rest = time.time() + COOLDOWN
                    tries = 0
                break

            if armed and not did and not ({"menu", "lobby", "ready"} & set(seen)):
                if tries < ESC_TRIES and now - esc_at > ESC_WAIT:
                    print("  no menu, esc again")
                    wait(REACT)
                    tap("esc")
                    tries += 1
                    esc_at = time.time()

            if arm_end and now >= arm_end:
                print("  timed out\n")
                arm_end = 0.0
                rest = now + COOLDOWN
                tries = 0

            t = time.time()
            if idle.on and not user and t >= arm_end and not seen and t - seen_at > IDLE_AFTER:
                idle.keys(t)
                idle.jump(t)
                idle.glance(t)

            time.sleep(r(SCAN))
    finally:
        idle.release()
        for k in ("w", "a", "s", "d", "space", "esc"):
            try:
                pydirectinput.keyUp(k, _pause=False)
            except Exception:
                pass
        print("keys released")


def test():
    load()
    print(f"scores (need {MATCH}, * = seen) ctrl+c to stop")
    while True:
        h = scan()
        print("   ".join(f"{n}: {s:.2f}{'*' if s >= MATCH else ' '}" for n, (_, _, s) in h.items()),
              end="\r", flush=True)
        time.sleep(0.3)


if __name__ == "__main__":
    a = sys.argv[1:]
    try:
        if a and a[0] == "setup":
            if len(a) > 1:
                if a[1] not in NAMES:
                    print("one of:", ", ".join(NAMES))
                    sys.exit(1)
                setup(a[1], a[2] if len(a) > 2 else None)
            else:
                for n in NAMES:
                    setup(n)
        elif a and a[0] == "test":
            test()
        elif a and a[0] == "files":
            files()
        else:
            run()
    except KeyboardInterrupt:
        print("\nstopped")
