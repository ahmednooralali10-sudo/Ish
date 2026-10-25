import os
import sys
import time
import random
import shutil
import threading
import requests
from user_agent import generate_user_agent


try:
    from rich.console import Console
    from rich.panel import Panel
    from rich import box
    from rich.prompt import Prompt
except ImportError:
    os.system('pip install rich')
    from rich.console import Console
    from rich.panel import Panel
    from rich import box
    from rich.prompt import Prompt


rich_console = Console()


RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[1;92m"
DARK = "\033[1;32m"
RED = "\033[1;91m"
PURPLE = "\033[1;95m"
CYAN = "\033[1;96m"
YELLOW = "\033[1;93m"

SYMBOLS = "!@#$%^&*<>[]{}\\/|0123456789▓▒░█▄▀"

# ---------------------------
# Utilities
# ---------------------------
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def terminal_size():
    cols, rows = shutil.get_terminal_size(fallback=(80, 24))
    return cols, rows

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def safe_exit():
    show_cursor()
    sys.stdout.write(RESET)
    sys.stdout.flush()


THE_LOGO = BOLD + GREEN + r"""
████████╗██╗  ██╗███████╗
╚══██╔══╝██║  ██║██╔════╝
   ██║   ███████║█████╗  
   ██║   ██╔══██║██╔══╝  
   ██║   ██║  ██║███████╗
   ╚═╝   ╚═╝  ╚═╝╚══════╝
""" + RESET

def print_logo():
    clear()
    print(THE_LOGO)



def ultra_glitch(text, duration=2.4, intensity=0.35, flicker=0.05):
    """يقطع النص ويرمزه بألوان ورموز، ثم يكشف النص النهائي"""
    end = time.time() + duration
    base = text
    palette = [PURPLE, RED, CYAN, GREEN, YELLOW]
    try:
        while time.time() < end:
            out = []
            for ch in base:
                if ch == " ":
                    out.append(" ")
                elif random.random() < intensity:
                    out.append(random.choice(SYMBOLS))
                else:
                    out.append(ch)
            color = random.choice(palette)
            sys.stdout.write("\r" + color + "".join(out) + RESET)
            sys.stdout.flush()
            time.sleep(flicker + random.random() * 0.03)
        # reveal
        sys.stdout.write("\r" + BOLD + GREEN + base + RESET + "\n")
    except KeyboardInterrupt:
        sys.stdout.write("\n")
        return

def pro_typewriter(text, wobble=0.06):
    PALETTE = [GREEN, PURPLE, RED, CYAN, YELLOW]
    for ch in text:
        if ch == " ":
            sys.stdout.write(" ")
            sys.stdout.flush()
            time.sleep(0.03)
            continue
        # flash random glyphs then real char
        for _ in range(random.randint(1,3)):
            sys.stdout.write(random.choice(PALETTE) + random.choice("!@#$%&*?") + RESET)
            sys.stdout.flush()
            time.sleep(wobble/8)
            sys.stdout.write("\b")
        sys.stdout.write(random.choice(PALETTE) + ch + RESET)
        sys.stdout.flush()
        time.sleep(wobble + random.uniform(0,0.03))
    print()

def matrix_rain(width=None, height=20, delay=0.05, duration=None):
    cols, rows = terminal_size()
    if width is None:
        width = min(80, cols)
    columns = [0] * width
    start = time.time()
    try:
        while True:
            if duration and (time.time() - start) > duration:
                break
            line = []
            for i in range(width):
                if columns[i] == 0:
                    line.append(" ")
                    if random.random() < 0.02:
                        columns[i] = random.randint(4, height)
                else:
                    line.append(chr(random.randint(33, 126)))
                    columns[i] -= 1
            sys.stdout.write(GREEN + "".join(line) + RESET + "\n")
            sys.stdout.flush()
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\n" + RED + "[Matrix stopped]" + RESET)
        return

_matrix_threads = []
_matrix_stop_event = threading.Event()

def _matrix_col_worker(x, width, height, stop_event):
    cols, rows = terminal_size()
    t_delay = lambda: random.uniform(0.02, 0.09)
    while not stop_event.is_set():
        stream = random.randint(3, max(3, height//2))
        for _ in range(stream):
            if stop_event.is_set():
                break
            row = random.randint(1, height)
            ch = chr(random.randint(33,126))
            sys.stdout.write(f"\033[{row};{x}H{GREEN}{ch}{RESET}")
            sys.stdout.flush()
            time.sleep(t_delay())
        time.sleep(random.uniform(0.02, 0.1))

def matrix_storm(duration=6):
    cols, rows = terminal_size()
    _matrix_stop_event.clear()
    sys.stdout.write("\033[2J\033[H")
    hide_cursor()
    threads = []
    step = max(1, cols // 60)
    try:
        for x in range(1, cols, step):
            t = threading.Thread(target=_matrix_col_worker, args=(x, cols, rows, _matrix_stop_event), daemon=True)
            threads.append(t)
            t.start()
        time.sleep(duration)
    except KeyboardInterrupt:
        pass
    finally:
        _matrix_stop_event.set()
        time.sleep(0.15)
        show_cursor()
        sys.stdout.write("\n")

def animated_gradient(rows=10, speed=0.05, cycles=9999):
    cols, _ = terminal_size()
    def bg(r,g,b): return f"\033[48;2;{r};{g};{b}m"
    try:
        for t in range(cycles):
            lines = []
            for y in range(rows):
                line = []
                for x in range(cols):
                    r = int((1 + __import__('math').sin((x/12.0)+(t/6.0)+(y/3.0))) * 127)
                    g = int((1 + __import__('math').sin((x/15.0)+(t/8.0)-(y/5.0))) * 127)
                    b = int((1 + __import__('math').sin((x/20.0)-(t/10.0)+(y/4.0))) * 127)
                    line.append(f"{bg(r,g,b)} ")
                lines.append("".join(line) + RESET)
            sys.stdout.write("\n".join(lines))
            sys.stdout.flush()
            time.sleep(speed)
            sys.stdout.write(f"\033[{rows}A")
    except KeyboardInterrupt:
        sys.stdout.write(RESET + "\n")
        return

def heartbeat_progress(total=30, speed=0.12, beep=False):
    try:
        for i in range(total+1):
            pct = int(i/total*100)
            blocks = i
            bar = "█"*blocks + "-"*(total-blocks)
            pulse = "*" if (i % 2 == 0) else " "
            sys.stdout.write(f"\r{PURPLE}[{bar}]{RESET} {CYAN}{pct:3d}%{RESET}  {RED}{pulse}{RESET}")
            sys.stdout.flush()
            if beep and i % 8 == 0:
                try:
                    sys.stdout.write("\a")
                except:
                    pass
            time.sleep(speed)
        print()
    except KeyboardInterrupt:
        print("\n" + RED + "[Progress stopped]" + RESET)

def spinner(duration=3, text="WORKING"):
    chars = "|/-\\"
    end = time.time() + duration
    while time.time() < end:
        for c in chars:
            sys.stdout.write(f"\r{CYAN}{c} {text}{RESET}")
            sys.stdout.flush()
            time.sleep(0.08)
    print("\r", end="\n")

def neon_box(text, color=PURPLE):
    line = f"  {text}  "
    l = len(line)
    print(color + "╔" + "═"*l + "╗" + RESET)
    print(CYAN + "║" + line + "║" + RESET)
    print(color + "╚" + "═"*l + "╝" + RESET)

def boss_mode():
    """تشغيل تسلسل مرئي قوي: شعار -> typewriter -> glitch -> gradient -> matrix storm -> progress"""
    try:
        clear()
        print_logo()
        time.sleep(0.6)
        pro_typewriter("INITIALIZING SECURE DISPLAY...", wobble=0.04)
        time.sleep(0.2)
        ultra_glitch("=== ACCESS GATEWAY ONLINE ===", duration=2.2, intensity=0.30)
        time.sleep(0.12)
        try:
            animated_gradient(rows=6, speed=0.04, cycles=20)
        except KeyboardInterrupt:
            pass
        try:
            matrix_storm(duration=5)
        except KeyboardInterrupt:
            pass
        heartbeat_progress(total=28, speed=0.10, beep=False)
        neon_box("THE BOSS MODE")
        print(BOLD + GREEN + "=== DONE ===" + RESET)
        time.sleep(0.8)
    except KeyboardInterrupt:
        print("\n" + RED + "[Boss mode interrupted]" + RESET)
    finally:
        safe_exit()



def youtube_likes():
    video = rich_console.input("[bold cyan]▶ رابط فيديو يوتيوب: [/bold cyan]")
    url = "https://leofame.com/free-youtube-likes?api=1"
    headers = {
        "Host": "leofame.com",
        "sec-ch-ua-platform": '"Android"',
        "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://leofame.com",
        "referer": "https://leofame.com/free-youtube-likes",
        "cookie": "cf_clearance=FAKECOOKIE; token=FAKETOKEN"
    }
    data = {"token": "FAKETOKEN", "timezone_offset": "Asia/Baghdad", "free_link": video}
    try:
        r = requests.post(url, headers=headers, data=data, timeout=15)
        if "Please wait" in r.text or '"error":' in r.text:
            rich_console.print(Panel("[bold red] يجب الانتظار 24 ساعة أو تغيير الرابط[/bold red]", title="فشل", style="red"))
        else:
            rich_console.print(Panel("[bold green] تم الرشق بنجاح![/bold green]", title="نجاح", style="green"))
    except Exception as e:
        rich_console.print(Panel(f"[bold red]خطأ في الاتصال: {e}[/bold red]", title="خطأ", style="red"))
    time.sleep(1)

def tiktok_likes():
    video = rich_console.input("[bold magenta]🎵 رابط فيديو تيك توك: [/bold magenta]")
    url = "https://leofame.com/free-tiktok-likes?api=1"
    headers = {
        "Host": "leofame.com",
        "sec-ch-ua-platform": '"Android"',
        "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        "sec-ch-ua-mobile": "?1",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://leofame.com",
        "referer": "https://leofame.com/free-tiktok-likes",
        "cookie": "cf_clearance=FAKECOOKIE; token=FAKETOKEN"
    }
    data = {"token": "FAKETOKEN", "timezone_offset": "Asia/Baghdad", "free_link": video}
    try:
        r = requests.post(url, headers=headers, data=data, timeout=15)
        if "Please wait" in r.text or '"error":' in r.text:
            rich_console.print(Panel("[bold red] يجب الانتظار 24 ساعة أو تغيير الرابط[/bold red]", title="فشل", style="red"))
        else:
            rich_console.print(Panel("[bold green] تم الرشق بنجاح![/bold green]", title="نجاح", style="green"))
    except Exception as e:
        rich_console.print(Panel(f"[bold red]خطأ في الاتصال: {e}[/bold red]", title="خطأ", style="red"))
    time.sleep(1)

def instagram_saves():
    link = rich_console.input("[bold yellow]📸 رابط فيديو إنستغرام: [/bold yellow]")
    url = "https://leofame.com/free-instagram-saves?api=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://leofame.com",
        "Referer": "https://leofame.com/free-instagram-saves",
        "Cookie": "token=FAKETOKEN; cf_clearance=FAKECOOKIE"
    }
    data = {"token": "FAKETOKEN", "timezone_offset": "Asia/Baghdad", "free_link": link, "quantity": "30", "speed": "-1"}
    try:
        r = requests.post(url, headers=headers, data=data, timeout=15)
        if "Please wait" in r.text or '"error":' in r.text:
            rich_console.print(Panel("[bold red] يجب الانتظار 24 ساعة أو تغيير الرابط[/bold red]", title="فشل", style="red"))
        else:
            rich_console.print(Panel("[bold green] تم الرشق بنجاح![/bold green]", title="نجاح", style="green"))
    except Exception as e:
        rich_console.print(Panel(f"[bold red]خطأ في الاتصال: {e}[/bold red]", title="خطأ", style="red"))
    time.sleep(1)

def tiktok_views():
    video = rich_console.input("[bold blue]👁️ رابط فيديو تيك توك: [/bold blue]")
    token_ex = "FAKETOKEN"
    url = "https://leofame.com/ar/free-tiktok-views?api=1"
    headers = {
        'User-Agent': generate_user_agent(),
        'sec-ch-ua-platform': '"Android"',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?1',
        'origin': 'https://leofame.com',
        'referer': 'https://leofame.com/ar/free-tiktok-views',
        'Cookie': f'token={token_ex}'
    }
    data = {'token': token_ex, 'timezone_offset': 'Asia/Baghdad', 'free_link': video, 'quantity': '200'}
    try:
        r = requests.post(url, headers=headers, data=data, timeout=15)
        if "Please wait" in r.text or '"error":' in r.text:
            rich_console.print(Panel("[bold red] يجب الانتظار 24 ساعة أو تغيير الرابط[/bold red]", title="فشل", style="red"))
        else:
            rich_console.print(Panel("[bold green] تم الرشق بنجاح![/bold green]", title="نجاح", style="green"))
    except Exception as e:
        rich_console.print(Panel(f"[bold red]خطأ في الاتصال: {e}[/bold red]", title="خطأ", style="red"))
    time.sleep(1)



def menu_loop():
    while True:
        clear()
        print_logo()
        print(BOLD + CYAN + "Select effect to run (press q to quit):" + RESET)
        print(f"{GREEN}[1]{RESET} Matrix rain (continuous)")
        print(f"{GREEN}[2]{RESET} Matrix storm (threaded, short)")
        print(f"{GREEN}[3]{RESET} Ultra Glitch")
        print(f"{GREEN}[4]{RESET} Animated Gradient")
        print(f"{GREEN}[5]{RESET} Pro Typewriter")
        print(f"{GREEN}[6]{RESET} Heartbeat Progress")
        print(f"{GREEN}[7]{RESET} Boss Mode (full sequence)")
        print(f"{GREEN}[8]{RESET} Neon box sample")
        print(f"{GREEN}[9]{RESET} متابعين يوتيوب")
        print(f"{GREEN}[10]{RESET} إعجابات تيك توك")
        print(f"{GREEN}[11]{RESET} حفظ منشور إنستغرام")
        print(f"{GREEN}[12]{RESET} مشاهدات تيك توك")
        print(f"{GREEN}[q]{RESET} Quit")
        choice = input(BOLD + YELLOW + "Choice: " + RESET).strip().lower()

        
        if choice == "1":
            clear()
            print(BOLD + GREEN + "[Matrix rain]  (Ctrl+C to stop)\n" + RESET)
            try:
                matrix_rain(width=None, height=terminal_size()[1]-5, delay=0.04, duration=None)
            except KeyboardInterrupt:
                input("\nPress Enter to return to menu...")
        elif choice == "2":
            clear()
            print(BOLD + GREEN + "[Matrix storm] (short)\n" + RESET)
            try:
                matrix_storm(duration=7)
            except KeyboardInterrupt:
                pass
            input("Press Enter to return to menu...")
        elif choice == "3":
            clear()
            txt = input("Glitch text (default: '!!! BOSS ACCESS GRANTED !!!'):\n> ").strip() or "!!! BOSS ACCESS GRANTED !!!"
            ultra_glitch(txt, duration=2.8, intensity=0.36)
            input("Press Enter to return to menu...")
        elif choice == "4":
            clear()
            print(BOLD + GREEN + "[Animated gradient] (Ctrl+C to stop)\n" + RESET)
            try:
                animated_gradient(rows=8, speed=0.04, cycles=9999)
            except KeyboardInterrupt:
                pass
            input("Press Enter to return to menu...")
        elif choice == "5":
            clear()
            txt = input("Typewriter text (default: 'INITIALIZING...'):\n> ").strip() or "INITIALIZING SECURE CHANNEL..."
            pro_typewriter(txt, wobble=0.05)
            input("Press Enter to return to menu...")
        elif choice == "6":
            clear()
            heartbeat_progress(total=30, speed=0.09, beep=False)
            input("Press Enter to return to menu...")
        elif choice == "7":
            clear()
            boss_mode()
            input("Press Enter to return to menu...")
        elif choice == "8":
            clear()
            neon_box("THE")
            input("Press Enter to return to menu...")

        
        elif choice == "9":
            clear()
            
            matrix_storm(duration=3)
            youtube_likes()
            input("\n[bold cyan]اضغط Enter للعودة للقائمة...[/bold cyan]")
        elif choice == "10":
            clear()
            matrix_storm(duration=3)
            tiktok_likes()
            input("\n[bold cyan]اضغط Enter للعودة للقائمة...[/bold cyan]")
        elif choice == "11":
            clear()
            matrix_storm(duration=3)
            instagram_saves()
            input("\n[bold cyan]اضغط Enter للعودة للقائمة...[/bold cyan]")
        elif choice == "12":
            clear()
            matrix_storm(duration=3)
            tiktok_views()
            input("\n[bold cyan]اضغط Enter للعودة للقائمة...[/bold cyan]")

        elif choice == "q":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")
            time.sleep(0.6)


if __name__ == "__main__":
    try:
        menu_loop()
    except Exception as e:
        safe_exit()
        print(RED + "[Error]" + RESET, e)
    finally:
        safe_exit()
