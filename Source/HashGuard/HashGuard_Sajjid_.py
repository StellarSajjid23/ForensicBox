#!/usr/bin/env python3

import os
import time
import sys
import json
import hashlib
from datetime import datetime

try:
    from colorama import init as colorama_init
    colorama_init()
except ImportError:
    pass


class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def print_message(message: str):
    print(message + Colors.RESET)


def ask_input(prompt: str) -> str:
    return input(Colors.YELLOW + prompt + Colors.RESET)


def print_banner():
    banner = r"""
      ╔══════════════════════════════════════════════════════════════════════════════════╗
      ║                                                                                  ║
      ║     ██╗  ██╗ █████╗ ███████╗██╗  ██╗ ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗    ║
      ║     ██║  ██║██╔══██╗██╔════╝██║  ██║██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗   ║
      ║     ███████║███████║███████╗███████║██║  ███╗██║   ██║███████║██████╔╝██║  ██║   ║
      ║     ██╔══██║██╔══██║╚════██║██╔══██║██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║   ║
      ║     ██║  ██║██║  ██║███████║██║  ██║╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝   ║
      ║     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝    ║
      ║                                                                                  ║
      ╚══════════════════════════════════════════════════════════════════════════════════╝
      ║                            File Integrity Monitor                                ║
      ╚══════════════════════════════════════════════════════════════════════════════════╝

"""
    print(Colors.RED + banner + Colors.RESET)
    print(Colors.CYAN + "[*] Internship Portfolio Edition" + Colors.RESET)
    print(Colors.GREEN + "[*] Author: StellarSajjid23" + Colors.RESET)
    print(Colors.YELLOW + "[*] Engine: SHA-256 File Integrity Monitoring" + Colors.RESET)
    print('                                                    ')


def get_file_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(4096)
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return "HASH_ERROR"


def collect_files(target_directory: str) -> dict:
    baseline = {}

    for root, _, files in os.walk(target_directory):
        for filename in files:
            full_path = os.path.join(root, filename)
            file_hash = get_file_hash(full_path)
            baseline[full_path] = file_hash

    return baseline


def save_baseline(baseline: dict, baseline_file: str):
    data = {
        "created_at": str(datetime.now()),
        "files": baseline
    }
    with open(baseline_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_baseline(baseline_file: str) -> dict:
    try:
        with open(baseline_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("files", {})
    except Exception:
        return {}


def compare_baseline(old_files: dict, new_files: dict):
    added = []
    deleted = []
    modified = []

    old_paths = set(old_files.keys())
    new_paths = set(new_files.keys())

    for path in new_paths - old_paths:
        added.append(path)

    for path in old_paths - new_paths:
        deleted.append(path)

    for path in old_paths.intersection(new_paths):
        if old_files[path] != new_files[path]:
            modified.append(path)

    return added, deleted, modified


def render_summary(added: list, deleted: list, modified: list):
    print()
    print(Colors.CYAN + Colors.BOLD + "Integrity Monitoring Summary:" + Colors.RESET)
    print(Colors.CYAN + "+-------------------------------------------------+" + Colors.RESET)
    print(f"{Colors.WHITE}| {'Category':<20} | {'Count':<25}|{Colors.RESET}")
    print(Colors.CYAN + "+-------------------------------------------------+" + Colors.RESET)
    print(f"{Colors.WHITE}| {'New Files':<20} | {Colors.GREEN}{len(added):<25}{Colors.WHITE}|{Colors.RESET}")
    print(f"{Colors.WHITE}| {'Deleted Files':<20} | {Colors.RED}{len(deleted):<25}{Colors.WHITE}|{Colors.RESET}")
    print(f"{Colors.WHITE}| {'Modified Files':<20} | {Colors.YELLOW}{len(modified):<25}{Colors.WHITE}|{Colors.RESET}")
    print(Colors.CYAN + "+-------------------------------------------------+" + Colors.RESET)


def render_file_table(title: str, items: list, color: str):
    print()
    print(color + Colors.BOLD + title + Colors.RESET)
    print(Colors.CYAN + "+-------------------------------------------------------+" + Colors.RESET)
    print(f"{Colors.WHITE}| {'#':<4} | {'File Path':<47}|{Colors.RESET}")
    print(Colors.CYAN + "+-------------------------------------------------------+" + Colors.RESET)

    if not items:
        print(f"{Colors.WHITE}| {'-':<4} | {'None':<47}|{Colors.RESET}")
    else:
        for index, item in enumerate(items, start=1):
            display_path = item[:47]
            print(f"{Colors.WHITE}| {index:<4} | {color}{display_path:<47}{Colors.WHITE}|{Colors.RESET}")

    print(Colors.CYAN + "+-------------------------------------------------------+" + Colors.RESET)


def create_baseline_workflow():
    target_directory = ask_input("Enter Directory Path to Baseline: ").strip()
    baseline_file = ask_input("Enter Baseline Filename [Default: baseline.json]: ").strip()

    if not baseline_file:
        baseline_file = "baseline.json"

    if not os.path.isdir(target_directory):
        print_message(Colors.RED + "[!] Invalid Directory Path.")
        return

    print()
    print_message(Colors.YELLOW + "[-] Creating Baseline...\n")

    baseline = collect_files(target_directory)
    save_baseline(baseline, baseline_file)

    print_message(Colors.GREEN + f"[+] Baseline Created Successfully: {baseline_file}")
    print_message(Colors.GREEN + f"[+] Total Files Hashed: {len(baseline)}")


def monitor_workflow():
    target_directory = ask_input("Enter Directory Path to Monitor: ").strip()
    baseline_file = ask_input("Enter Baseline Filename [Default: baseline.json]: ").strip()

    if not baseline_file:
        baseline_file = "baseline.json"

    if not os.path.isdir(target_directory):
        print_message(Colors.RED + "[!] Invalid Directory Path.")
        return

    if not os.path.exists(baseline_file):
        print_message(Colors.RED + f"[!] Baseline File Not Found: {baseline_file}")
        return

    print()
    print_message(Colors.YELLOW + "[-] Loading Baseline...")
    print_message(Colors.YELLOW + "[-] Scanning Current Files...\n")

    old_files = load_baseline(baseline_file)
    new_files = collect_files(target_directory)

    added, deleted, modified = compare_baseline(old_files, new_files)

    render_summary(added, deleted, modified)
    render_file_table("New Files Detected:", added, Colors.GREEN)
    render_file_table("Deleted Files Detected:", deleted, Colors.RED)
    render_file_table("Modified Files Detected:", modified, Colors.YELLOW)


def main():
    print_banner()

    print_message(Colors.BLUE + "[i] Mode        : File Integrity Monitoring")
    print_message(Colors.BLUE + "[i] Hashing     : SHA-256")
    print_message(Colors.BLUE + "[i] Storage     : JSON Baseline\n")

    try:
        print(Colors.CYAN + "Choose an Option:" + Colors.RESET)
        print(Colors.WHITE + "1. Create Baseline" + Colors.RESET)
        print(Colors.WHITE + "2. Monitor Directory Against Baseline" + Colors.RESET)
        print(Colors.WHITE + "3. Exit\n" + Colors.RESET)

        choice = ask_input("Enter Choice [ 1 / 2 / 3 ] : ").strip()

        if choice == "1":
            create_baseline_workflow()
        elif choice == "2":
            monitor_workflow()
        elif choice == "3":
            print_message(Colors.YELLOW + "[-] Exiting.")
            sys.exit(0)
        else:
            print_message(Colors.RED + "[!] Invalid Choice.")

    except KeyboardInterrupt:
        print_message("\n" + Colors.RED + "[!] Operation Interrupted by User.")
        sys.exit(0)
    except Exception as exc:
        print_message(Colors.RED + f"[!] Unexpected Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    time.sleep(60)
