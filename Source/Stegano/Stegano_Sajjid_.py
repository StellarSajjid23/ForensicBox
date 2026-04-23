#!/usr/bin/env python3

import sys
import time
from pathlib import Path

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

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


SUPPORTED_EXTENSIONS = {".png", ".bmp"}
END_MARKER = "~~~END~~~"


def print_message(message: str):
    print(message + Colors.RESET)


def ask_input(prompt: str) -> str:
    return input(Colors.YELLOW + prompt + Colors.RESET)


def print_banner():
    banner = r"""
            ▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
            ▐                                                                           ▌
            ▐     /$$$$$$   /$$                                                         ▌
            ▐    /$$__  $$ | $$                                                         ▌
            ▐   | $$  \__//$$$$$$    /$$$$$$   /$$$$$$   /$$$$$$  /$$$$$$$   /$$$$$$    ▌
            ▐   |  $$$$$$|_  $$_/   /$$__  $$ /$$__  $$ |____  $$| $$__  $$ /$$__  $$   ▌
            ▐    \____  $$ | $$    | $$$$$$$$| $$  \ $$  /$$$$$$$| $$  \ $$| $$  \ $$   ▌
            ▐    /$$  \ $$ | $$ /$$| $$_____/| $$  | $$ /$$__  $$| $$  | $$| $$  | $$   ▌
            ▐   |  $$$$$$/ |  $$$$/|  $$$$$$$|  $$$$$$$|  $$$$$$$| $$  | $$|  $$$$$$/   ▌
            ▐    \______/   \___/   \_______/ \____  $$ \_______/|__/  |__/ \______/    ▌
            ▐                                 /$$  \ $$                                 ▌
            ▐                                |  $$$$$$/                                 ▌
            ▐                                 \______/                                  ▌
            ▐                                                                           ▌
            ▐                  Steganography Extractor & Generator                      ▌
            ▐                                                                           ▌
            ▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
"""
    print(Colors.RED + banner + Colors.RESET)
    print(Colors.CYAN + "[*] Internship Portfolio Edition" + Colors.RESET)
    print(Colors.GREEN + "[*] Author: Sajjid" + Colors.RESET)
    print(Colors.YELLOW + "[*] Engine: LSB Message Embed + Extract" + Colors.RESET)
    print("                              ")


def validate_image_path(image_path: str) -> Path:
    path = Path(image_path)

    if not path.exists():
        print_message(Colors.RED + "[!] File Does Not Exist.")
        sys.exit(1)

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        print_message(Colors.RED + "[!] Only PNG and BMP are Supported.")
        sys.exit(1)

    return path


def open_image_rgb(path: Path):
    try:
        img = Image.open(path)
        if img.format not in {"PNG", "BMP"}:
            print_message(Colors.RED + "[!] Only PNG and BMP are Supported for Reliable LSB Operations.")
            sys.exit(1)
        return img.convert("RGB"), img.format
    except Exception as exc:
        print_message(Colors.RED + f"[!] Failed to Open Image: {exc}")
        sys.exit(1)


def text_to_bits(text: str) -> str:
    return "".join(format(ord(char), "08b") for char in text)


def bits_to_text(bits: str) -> str:
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        if len(byte) < 8:
            continue
        chars.append(chr(int(byte, 2)))
    return "".join(chars)


def calculate_capacity(img) -> int:
    width, height = img.size
    total_pixels = width * height
    usable_bits = total_pixels  # 1 bit per pixel using red channel
    usable_chars = usable_bits // 8
    return usable_chars


def embed_message(img, message: str):
    message_with_marker = message + END_MARKER
    bits = text_to_bits(message_with_marker)

    pixels = list(img.getdata())

    if len(bits) > len(pixels):
        print_message(Colors.RED + "[!] Message Too Large for This Image.")
        sys.exit(1)

    new_pixels = []
    bit_index = 0

    for pixel in pixels:
        r, g, b = pixel

        if bit_index < len(bits):
            new_r = (r & ~1) | int(bits[bit_index])
            bit_index += 1
        else:
            new_r = r

        new_pixels.append((new_r, g, b))

    new_img = Image.new(img.mode, img.size)
    new_img.putdata(new_pixels)

    return new_img, len(bits)


def extract_message(img) -> str:
    pixels = list(img.getdata())
    bits = []

    for r, g, b in pixels:
        bits.append(str(r & 1))

    extracted_text = bits_to_text("".join(bits))
    marker_index = extracted_text.find(END_MARKER)

    if marker_index == -1:
        return ""

    return extracted_text[:marker_index]


def render_embed_summary(input_file: str, img_format: str, width: int, height: int, capacity: int, message_len: int, output_file: str):
    print("\n" + Colors.CYAN + Colors.BOLD + "Embedding Summary:" + Colors.RESET)

    border = "+----------------------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'Checking':^38}|{'Status':^25}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)

    rows = [
        ("Input File", input_file[:25], Colors.WHITE),
        ("Format", img_format, Colors.GREEN),
        ("Dimensions", f"{width}x{height}", Colors.CYAN),
        ("Char Capacity", str(capacity), Colors.YELLOW),
        ("Message Length", str(message_len), Colors.MAGENTA),
        ("Output File", output_file[:25], Colors.GREEN),
    ]

    for label, value, color in rows:
        print(
            Colors.WHITE + "|" +
            f"{label:<38}" +
            "|" +
            color + f"{str(value):^25}" +
            Colors.WHITE + "|" +
            Colors.RESET
        )

    print(Colors.CYAN + border + Colors.RESET)


def render_extract_summary(input_file: str, img_format: str, width: int, height: int, message_found: bool, message_len: int):
    print("\n" + Colors.CYAN + Colors.BOLD + "Extraction Summary:" + Colors.RESET)

    border = "+------------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'Checking':^38}|{'Status':^15}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)

    rows = [
        ("Input File", input_file[:15], Colors.WHITE),
        ("Format", img_format, Colors.GREEN),
        ("Dimensions", f"{width}x{height}", Colors.CYAN),
        ("Message Found", "YES" if message_found else "NO", Colors.GREEN if message_found else Colors.RED),
        ("Message Length", str(message_len), Colors.YELLOW),
    ]

    for label, value, color in rows:
        print(
            Colors.WHITE + "|" +
            f"{label:<38}" +
            "|" +
            color + f"{str(value):^15}" +
            Colors.WHITE + "|" +
            Colors.RESET
        )

    print(Colors.CYAN + border + Colors.RESET)


def render_message_table(title: str, message: str):
    print("\n" + Colors.MAGENTA + Colors.BOLD + title + ":" + Colors.RESET)

    border = "+----------------------------------------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'#':^5}|{'Content':^76}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)

    if not message:
        print(
            Colors.WHITE + "|" +
            f"{'-':^5}" +
            "|" +
            Colors.RED + f"{'No message found':^76}" +
            Colors.WHITE + "|" +
            Colors.RESET
        )
    else:
        chunks = [message[i:i + 76] for i in range(0, len(message), 76)]
        for idx, chunk in enumerate(chunks[:10], start=1):
            print(
                Colors.WHITE + "|" +
                f"{idx:^5}" +
                "|" +
                Colors.YELLOW + f"{chunk:<76}" +
                Colors.WHITE + "|" +
                Colors.RESET
            )

    print(Colors.CYAN + border + Colors.RESET)


def render_recommendations(mode: str, output_file: str = ""):
    print("\n" + Colors.CYAN + Colors.BOLD + "Recommendations:" + Colors.RESET)

    border = "+----------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'#':^6}|{'Recommendation':^45}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)

    if mode == "embed":
        recommendations = [
            "Use PNG or BMP only.",
            "Keep original image unchanged for comparison.",
            "Do not exceed image capacity.",
            f"Output saved: {Path(output_file).name}" if output_file else "Save output safely.",
            "Test extraction after embedding."
        ]
    else:
        recommendations = [
            "Use the same script for extraction.",
            "Best results come from PNG or BMP.",
            "If no marker found, image may not contain data.",
            "Compare suspicious and original images.",
            "Preserve evidence before modifying files."
        ]

    for idx, item in enumerate(recommendations[:6], start=1):
        text = item[:45]
        print(
            Colors.WHITE + "|" +
            f"{str(idx):^6}" +
            "|" +
            Colors.YELLOW + f"{text:<45}" +
            Colors.WHITE + "|" +
            Colors.RESET
        )

    print(Colors.CYAN + border + Colors.RESET)


def embed_workflow():
    image_path = ask_input("Enter Input Image Path: ").strip()
    path = validate_image_path(image_path)

    message = ask_input("Enter Secret Message to Embed: ").strip()
    if not message:
        print_message(Colors.RED + "[!] No Message Provided.")
        sys.exit(1)

    output_name = ask_input("Enter Output File Name [ Default: Output.png ] : ").strip()
    if not output_name:
        output_name = "Output.png"

    if not output_name.lower().endswith((".png", ".bmp")):
        output_name += ".png"

    print()
    print_message(Colors.YELLOW + "[-] Embedding Secret Message ...\n")

    img, img_format = open_image_rgb(path)
    width, height = img.size
    capacity = calculate_capacity(img)

    if len(message + END_MARKER) > capacity:
        print_message(Colors.RED + "[!] Message Exceeds Image Capacity.")
        sys.exit(1)

    stego_img, bits_used = embed_message(img, message)
    save_format = "PNG" if output_name.lower().endswith(".png") else "BMP"

    output_dir = Path("Data") / "Output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_name

    stego_img.save(output_path, format=save_format)

    render_embed_summary(path.name, img_format, width, height, capacity, len(message), str(output_path))
    render_message_table("Embedded Message Preview", message)
    render_recommendations("embed", str(output_path))

    print()
    print_message(Colors.GREEN + f"[+] Stego Image Created Successfully: {output_path}")


def extract_workflow():
    image_path = ask_input("Enter Steganography Image Path : ").strip()
    path = validate_image_path(image_path)

    print()
    print_message(Colors.YELLOW + "[-] Extracting Hidden Message...\n")

    img, img_format = open_image_rgb(path)
    width, height = img.size
    message = extract_message(img)

    render_extract_summary(path.name, img_format, width, height, bool(message), len(message))
    render_message_table("Extracted Message", message)
    render_recommendations("extract")

    print()
    if message:
        print_message(Colors.GREEN + "[+] Hidden Message Extracted Successfully.")
    else:
        print_message(Colors.RED + "[!] No Hidden Message Found With This Format.")


def main():
    print_banner()

    print_message(Colors.BLUE + "[i] Mode        : Embed + Extract")
    print_message(Colors.BLUE + "[i] Input Type  : PNG / BMP Image")
    print_message(Colors.BLUE + "[i] Detection   : LSB Message Hide and Retrieve\n")

    if not PIL_AVAILABLE:
        print_message(Colors.RED + "[!] Pillow Is Not Installed.")
        print_message(Colors.YELLOW + "Install It With : py -m pip install pillow colorama")
        sys.exit(1)

    try:
        print(Colors.CYAN + "Choose an Option:" + Colors.RESET)
        print(Colors.WHITE + "1. Embed Message into Image" + Colors.RESET)
        print(Colors.WHITE + "2. Extract Message from Image" + Colors.RESET)
        print(Colors.WHITE + "3. Exit\n" + Colors.RESET)

        choice = ask_input("Enter Choice [ 1 / 2 / 3 ] : ").strip()

        if choice == "1":
            embed_workflow()
        elif choice == "2":
            extract_workflow()
        elif choice == "3":
            print_message(Colors.YELLOW + "[-] Exiting.")
            sys.exit(0)
        else:
            print_message(Colors.RED + "[!] Invalid Choice.")
            sys.exit(1)

    except KeyboardInterrupt:
        print_message("\n" + Colors.RED + "[!] Operation Interrupted by User.")
        sys.exit(0)
    except Exception as exc:
        print_message(Colors.RED + f"[!] Unexpected Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    time.sleep(60)
