import subprocess
import sys

from colorama import Fore, Style

G = Fore.GREEN
C = Fore.CYAN
Y = Fore.YELLOW
R = Fore.RED
X = Style.RESET_ALL

def menu():
    print(f"\n{C}{'='*40}")
    print(f"  user-scanner v1.4.1.1 — OSINT Tool")
    print(f"{'='*40}{X}")
    print(f"\n{G}What would you like to scan?{X}")
    print(f"  {Y}1{X}  Scan a username")
    print(f"  {Y}2{X}  Scan an email")
    print(f"  {Y}3{X}  List username modules")
    print(f"  {Y}4{X}  List email modules")
    print(f"  {Y}5{X}  Custom command")
    print(f"  {Y}q{X}  Quit")
    print()

def run(args):
    cmd = [sys.executable, "-m", "user_scanner"] + args
    subprocess.run(cmd)

def main():
    while True:
        menu()
        try:
            choice = input(f"{C}Choice:{X} ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{G}Goodbye!{X}")
            break

        if choice == "q":
            print(f"\n{G}Goodbye!{X}")
            break
        elif choice == "1":
            username = input(f"{C}Username to scan:{X} ").strip()
            if username:
                only_found = input(f"{Y}Only show found results? (y/n):{X} ").strip().lower() == "y"
                args = ["-u", username]
                if only_found:
                    args.append("--only-found")
                run(args)
        elif choice == "2":
            email = input(f"{C}Email to scan:{X} ").strip()
            if email:
                only_found = input(f"{Y}Only show found results? (y/n):{X} ").strip().lower() == "y"
                args = ["-e", email]
                if only_found:
                    args.append("--only-found")
                run(args)
        elif choice == "3":
            run(["--list-user"])
        elif choice == "4":
            run(["--list-email"])
        elif choice == "5":
            custom = input(f"{C}Enter flags (e.g. -u johndoe --only-found):{X} ").strip()
            if custom:
                run(custom.split())
        else:
            print(f"{R}Invalid choice. Please enter 1-5 or q.{X}")

if __name__ == "__main__":
    main()
