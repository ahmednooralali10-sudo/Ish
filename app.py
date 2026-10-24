import os
import subprocess
import sys

# الألوان وأنماط الخط (ANSI Escape Codes)
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
MAGENTA = "\033[1;35m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_banner():
    # تنظيف الشاشة
    os.system("clear")

    # شعار XORE بتصميم ASCII
    banner = f"""{MAGENTA}
__  _____  ____  _____ 
\\ \\/ / _ \\|  _ \\| ____|
 \\  / | | | |_) |  _|  
 /  \\| |_| |  _ <| |___ 
/_/\\_\\___/|_| \\_\\_____|
{RESET}"""
    print(banner)
    print(f"{CYAN}====================================================={RESET}")
    print(
        f"{YELLOW}   Welcome to XORE Terminal Environment (iSH) {RESET}"
    )
    print(f"{CYAN}====================================================={RESET}\n")


def main():
    print_banner()

    # حلقة استقبال وتشغيل الأوامر
    while True:
        try:
            # شكل مؤشر الأوامر (Prompt)
            prompt = f"{GREEN}XORE{RESET}@{CYAN}iSH{RESET}:{MAGENTA}~${RESET} "
            cmd = input(prompt)

            # التجاهل إذا كان المدخل فارغاً
            if not cmd.strip():
                continue

            # أمر الخروج
            if cmd.strip().lower() in ["exit", "quit"]:
                print(f"{YELLOW}Exiting XORE Terminal... Goodbye!{RESET}")
                break

            # أمر مسح الشاشة لعادة إظهار الشعار
            if cmd.strip().lower() == "clear":
                print_banner()
                continue

            # تنفيذ الأمر داخل بيئة النظام
            subprocess.run(cmd, shell=True)

        except KeyboardInterrupt:
            # التعامل مع الضغط على Ctrl+C بمرونة
            print("\nUse 'exit' to quit.")
        except EOFError:
            break


if __name__ == "__main__":
    main()
