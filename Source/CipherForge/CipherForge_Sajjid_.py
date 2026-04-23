#!/usr/bin/env python3

import re
import math
import time
import sys
import secrets
import string
from getpass import getpass

# =========================
# OPTIONAL IMPORTS
# =========================
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from colorama import init as colorama_init
    colorama_init()
except ImportError:
    pass


# =========================
# COLORS
# =========================
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


# =========================
# OUTPUT HELPERS
# =========================
if RICH_AVAILABLE:
    console = Console()
else:
    console = None


def print_message(message: str):
    if RICH_AVAILABLE:
        console.print(message)
    else:
        message = message.replace("[bold red]", Colors.BOLD + Colors.RED)
        message = message.replace("[bold green]", Colors.BOLD + Colors.GREEN)
        message = message.replace("[bold yellow]", Colors.BOLD + Colors.YELLOW)
        message = message.replace("[bold blue]", Colors.BOLD + Colors.BLUE)
        message = message.replace("[bold cyan]", Colors.BOLD + Colors.CYAN)
        message = message.replace("[bold white]", Colors.BOLD + Colors.WHITE)
        message = message.replace("[bold magenta]", Colors.BOLD + Colors.MAGENTA)

        message = message.replace("[red]", Colors.RED)
        message = message.replace("[green]", Colors.GREEN)
        message = message.replace("[yellow]", Colors.YELLOW)
        message = message.replace("[blue]", Colors.BLUE)
        message = message.replace("[cyan]", Colors.CYAN)
        message = message.replace("[white]", Colors.WHITE)
        message = message.replace("[magenta]", Colors.MAGENTA)

        message = re.sub(r"\[/?[^\]]+\]", "", message)
        print(message + Colors.RESET)


def ask_input(prompt: str, hidden: bool = False) -> str:
    if hidden:
        if RICH_AVAILABLE:
            console.print(prompt, end="")
            return getpass("")
        clean_prompt = re.sub(r"\[/?[^\]]+\]", "", prompt)
        return getpass(Colors.YELLOW + clean_prompt + Colors.RESET)

    if RICH_AVAILABLE:
        return console.input(prompt)

    clean_prompt = re.sub(r"\[/?[^\]]+\]", "", prompt)
    return input(Colors.YELLOW + clean_prompt + Colors.RESET)


# =========================
# BANNER
# =========================
def print_banner():
    banner = r"""
       +--------------------------------------------------------------------+ 
       |        _____ _       _               ______                        |
       |       / ____(_)     | |             |  ____|                       |
       |      | |     _ _ __ | |__   ___ _ __| |__ ___  _ __ __ _  ___      |
       |      | |    | | '_ \| '_ \ / _ \ '__|  __/ _ \| '__/ _` |/ _ \     |
       |      | |____| | |_) | | | |  __/ |  | | | (_) | | | (_| |  __/     |
       |       \_____|_| .__/|_| |_|\___|_|  |_|  \___/|_|  \__, |\___|     |
       |               | |                                  __/ |           |
       |               |_|                                 |___/            |
       +--------------------------------------------------------------------+ 
       |                  Credential Security Workbench                     |
       +--------------------------------------------------------------------+
"""

    if RICH_AVAILABLE:
        console.print(
            Panel.fit(
                Text(banner, style="bold red"),
                title="[bold cyan]Internship Portfolio Edition[/bold cyan]",
                subtitle="[bold green]Author: Sajjid[/bold green]"
            )
        )
    else:
        print(Colors.RED + banner + Colors.RESET)
        print(Colors.CYAN + "[*] Internship Portfolio Edition" + Colors.RESET)
        print(Colors.GREEN + "[*] Author: StellarSajjid23" + Colors.RESET)
        print(Colors.YELLOW + "[*] Engine: Password Strength + Passphrase Generator" + Colors.RESET)


# =========================
# PASSWORD KNOWLEDGE
# =========================
COMMON_PASSWORDS = {
    "password", "password123", "123456", "12345678", "123456789",
    "qwerty", "qwerty123", "admin", "admin123", "letmein",
    "welcome", "welcome123", "iloveyou", "abc123", "monkey",
    "dragon", "football", "baseball", "login", "root",
    "toor", "passw0rd", "p@ssword", "sajjid123", "administrator",
    "welcome1", "changeme", "default", "test123", "temp123",
    "summer2024", "summer2025", "summer2026", "winter2024",
    "winter2025", "winter2026", "spring2025", "fall2025"
}

COMMON_PATTERNS = [
    r"1234", r"12345", r"123456", r"abcd", r"qwerty", r"asdf",
    r"zxcv", r"admin", r"password", r"letmein", r"welcome",
    r"iloveyou", r"login", r"root"
]

KEYBOARD_WALKS = [
    "qwerty", "asdfgh", "zxcvbn", "123456", "098765", "1qaz", "qazwsx"
]

LEET_MAP = {
    "@": "a", "4": "a",
    "3": "e",
    "1": "l",
    "!": "i",
    "0": "o",
    "$": "s",
    "5": "s",
    "7": "t"
}

WORDLIST = [
    "orbit", "falcon", "ember", "delta", "forest", "river", "anchor", "titan",
    "copper", "shadow", "violet", "signal", "cactus", "aurora", "summit", "matrix",
    "rocket", "phoenix", "marble", "ocean", "granite", "harbor", "echo", "storm",
    "secure", "shield", "cipher", "vertex", "cloud", "silver", "quantum", "hazel"
]

POLICY_PROFILES = {
    "1": {
        "name": "Standard User",
        "min_length": 12,
        "require_upper": True,
        "require_lower": True,
        "require_digit": True,
        "require_special": True,
        "max_repeats": 2,
        "passphrase_ok": True
    },
    "2": {
        "name": "Administrator",
        "min_length": 16,
        "require_upper": True,
        "require_lower": True,
        "require_digit": True,
        "require_special": True,
        "max_repeats": 2,
        "passphrase_ok": True
    },
    "3": {
        "name": "Service Account",
        "min_length": 20,
        "require_upper": True,
        "require_lower": True,
        "require_digit": True,
        "require_special": True,
        "max_repeats": 1,
        "passphrase_ok": False
    },
    "4": {
        "name": "Student / Personal",
        "min_length": 10,
        "require_upper": True,
        "require_lower": True,
        "require_digit": True,
        "require_special": False,
        "max_repeats": 2,
        "passphrase_ok": True
    }
}


# =========================
# BASIC CHECKS
# =========================
def has_uppercase(password: str) -> bool:
    return bool(re.search(r"[A-Z]", password))


def has_lowercase(password: str) -> bool:
    return bool(re.search(r"[a-z]", password))


def has_digit(password: str) -> bool:
    return bool(re.search(r"\d", password))


def has_special(password: str) -> bool:
    return bool(re.search(r"[^A-Za-z0-9\s]", password))


def has_spaces(password: str) -> bool:
    return " " in password.strip()


def has_repeated_chars(password: str, max_repeat: int = 2) -> bool:
    pattern = r"(.)\1{" + str(max_repeat) + r",}"
    return bool(re.search(pattern, password))


def only_letters(password: str) -> bool:
    return password.isalpha()


def only_numbers(password: str) -> bool:
    return password.isdigit()


def normalize_for_similarity(password: str) -> str:
    lowered = password.lower()
    for old, new in LEET_MAP.items():
        lowered = lowered.replace(old, new)
    return lowered


def has_common_pattern(password: str) -> bool:
    lowered = password.lower()
    for pattern in COMMON_PATTERNS:
        if re.search(pattern, lowered):
            return True
    return False


def has_keyboard_walk(password: str) -> bool:
    lowered = normalize_for_similarity(password)
    for walk in KEYBOARD_WALKS:
        if walk in lowered or walk[::-1] in lowered:
            return True
    return False


def has_year_like_token(password: str) -> bool:
    return bool(re.search(r"(19\d{2}|20\d{2}|202\d)", password))


def has_sequential_chars(password: str) -> bool:
    lowered = normalize_for_similarity(password)
    sequences = "abcdefghijklmnopqrstuvwxyz"
    digits = "0123456789"

    for i in range(len(lowered) - 3):
        chunk = lowered[i:i + 4]
        if chunk in sequences or chunk in sequences[::-1]:
            return True
        if chunk in digits or chunk in digits[::-1]:
            return True
    return False


def count_character_sets(password: str) -> int:
    count = 0
    if has_uppercase(password):
        count += 1
    if has_lowercase(password):
        count += 1
    if has_digit(password):
        count += 1
    if has_special(password):
        count += 1
    if has_spaces(password):
        count += 1
    return count


def is_passphrase(password: str) -> bool:
    words = [word for word in password.strip().split() if word]
    return len(words) >= 3 and len(password) >= 16


def estimate_charset_size(password: str) -> int:
    charset = 0
    if has_lowercase(password):
        charset += 26
    if has_uppercase(password):
        charset += 26
    if has_digit(password):
        charset += 10
    if has_special(password):
        charset += 33
    if has_spaces(password):
        charset += 1

    if charset == 0:
        charset = 1

    return charset


def estimate_entropy(password: str) -> float:
    charset_size = estimate_charset_size(password)
    return round(len(password) * math.log2(charset_size), 2)


def estimate_crack_profile(entropy_bits: float) -> str:
    if entropy_bits >= 100:
        return "Excellent Resistance"
    if entropy_bits >= 80:
        return "Very Strong Resistance"
    if entropy_bits >= 60:
        return "Strong Resistance"
    if entropy_bits >= 45:
        return "Moderate Resistance"
    if entropy_bits >= 30:
        return "Weak Resistance"
    return "Very Weak Resistance"


def mutation_risk(password: str) -> str:
    lowered = normalize_for_similarity(password)

    if lowered in COMMON_PASSWORDS:
        return "High"

    if has_common_pattern(password) or has_keyboard_walk(password) or has_year_like_token(password):
        return "High"

    if len(password) < 10:
        return "Medium"

    return "Low"


def detect_personal_pattern(password: str) -> bool:
    suspicious_tokens = [
        "name", "user", "admin", "root", "sap", "cloud",
        "hello", "welcome", "family", "wife", "love"
    ]
    lowered = normalize_for_similarity(password)
    return any(token in lowered for token in suspicious_tokens)


# =========================
# POLICY CHECKING
# =========================
def evaluate_policy(password: str, policy: dict) -> dict:
    checks = {
        "Minimum Length": len(password) >= policy["min_length"],
        "Uppercase Required": has_uppercase(password) if policy["require_upper"] else True,
        "Lowercase Required": has_lowercase(password) if policy["require_lower"] else True,
        "Digit Required": has_digit(password) if policy["require_digit"] else True,
        "Special Required": has_special(password) if policy["require_special"] else True,
        "Repeat Limit": not has_repeated_chars(password, policy["max_repeats"]),
        "Passphrase Allowed": True if policy["passphrase_ok"] else not has_spaces(password)
    }

    passed = all(checks.values())
    return {
        "checks": checks,
        "passed": passed
    }


# =========================
# MAIN ANALYSIS
# =========================
def analyze_password(password: str, policy: dict) -> dict:
    feedback = []
    checks = {}

    length = len(password)
    entropy = estimate_entropy(password)
    entropy_profile = estimate_crack_profile(entropy)
    set_count = count_character_sets(password)
    passphrase_mode = is_passphrase(password)
    common_password_hit = normalize_for_similarity(password) in COMMON_PASSWORDS

    checks["Length >= 8"] = length >= 8
    checks[f"Length >= {policy['min_length']}"] = length >= policy["min_length"]
    checks["Uppercase"] = has_uppercase(password)
    checks["Lowercase"] = has_lowercase(password)
    checks["Numbers"] = has_digit(password)
    checks["Special Characters"] = has_special(password)
    checks["Multi-Character Sets"] = set_count >= 3
    checks["No Common Pattern"] = not has_common_pattern(password)
    checks["No Keyboard Walk"] = not has_keyboard_walk(password)
    checks["No Long Repeats"] = not has_repeated_chars(password, policy["max_repeats"])
    checks["No Sequential Chars"] = not has_sequential_chars(password)
    checks["Not Common Password"] = not common_password_hit
    checks["Not Only Letters"] = not only_letters(password)
    checks["Not Only Numbers"] = not only_numbers(password)
    checks["No Year-Like Token"] = not has_year_like_token(password)
    checks["No Personal Pattern Hint"] = not detect_personal_pattern(password)
    checks["Passphrase Style"] = passphrase_mode

    score = 0

    if length >= 8:
        score += 8
    else:
        feedback.append("Use at least 8 characters.")

    if length >= policy["min_length"]:
        score += 15
    else:
        feedback.append(f"Increase length to at least {policy['min_length']} characters.")

    if length >= 16:
        score += 10

    if has_uppercase(password):
        score += 8
    else:
        feedback.append("Add uppercase letters.")

    if has_lowercase(password):
        score += 8
    else:
        feedback.append("Add lowercase letters.")

    if has_digit(password):
        score += 8
    else:
        feedback.append("Add numbers.")

    if has_special(password):
        score += 10
    else:
        feedback.append("Add special characters for stronger resistance.")

    if set_count >= 3:
        score += 8
    else:
        feedback.append("Use at least 3 character types.")

    if not has_repeated_chars(password, policy["max_repeats"]):
        score += 5
    else:
        feedback.append("Avoid repeated characters like aaa or 111.")

    if not has_common_pattern(password):
        score += 8
    else:
        feedback.append("Avoid common patterns like password, admin, qwerty, 1234.")

    if not has_keyboard_walk(password):
        score += 6
    else:
        feedback.append("Avoid keyboard walks like qwerty, asdf, 1qaz.")

    if not has_sequential_chars(password):
        score += 6
    else:
        feedback.append("Avoid sequential character strings like abcd or 1234.")

    if not common_password_hit:
        score += 10
    else:
        feedback.append("Do not use a common or easily guessed password.")

    if not only_letters(password):
        score += 4
    else:
        feedback.append("Avoid letters-only passwords.")

    if not only_numbers(password):
        score += 4
    else:
        feedback.append("Avoid numbers-only passwords.")

    if not has_year_like_token(password):
        score += 4
    else:
        feedback.append("Avoid obvious year values like 2024, 2025, or 2026.")

    if not detect_personal_pattern(password):
        score += 4
    else:
        feedback.append("Avoid words that may relate to personal habits or predictable context.")

    if passphrase_mode:
        score += 6

    if entropy >= 80:
        score += 8
    elif entropy >= 60:
        score += 5
    elif entropy < 35:
        feedback.append("Entropy is low; length and randomness should be improved.")

    policy_result = evaluate_policy(password, policy)
    if policy_result["passed"]:
        score += 8
    else:
        feedback.append(f"Password does not fully satisfy the '{policy['name']}' policy profile.")

    score = min(score, 100)

    if score >= 90:
        rating = "Very Strong"
        rating_color = "green"
    elif score >= 75:
        rating = "Strong"
        rating_color = "green"
    elif score >= 55:
        rating = "Moderate"
        rating_color = "yellow"
    elif score >= 35:
        rating = "Weak"
        rating_color = "yellow"
    else:
        rating = "Very Weak"
        rating_color = "red"

    usability = "Good"
    if length >= 20 and not passphrase_mode:
        usability = "Hard to Memorize"
    elif passphrase_mode:
        usability = "Memorable Passphrase"
    elif score < 40:
        usability = "Easy but Unsafe"

    return {
        "score": score,
        "rating": rating,
        "rating_color": rating_color,
        "entropy": entropy,
        "entropy_profile": entropy_profile,
        "mutation_risk": mutation_risk(password),
        "usability": usability,
        "checks": checks,
        "feedback": feedback,
        "passphrase_mode": passphrase_mode,
        "policy_result": policy_result,
        "policy_name": policy["name"]
    }


# =========================
# PASSWORD / PASSPHRASE GENERATION
# =========================
def generate_strong_password(length: int = 18) -> str:
    if length < 12:
        length = 12

    lower = secrets.choice(string.ascii_lowercase)
    upper = secrets.choice(string.ascii_uppercase)
    digit = secrets.choice(string.digits)
    special = secrets.choice("!@#$%^&*()-_=+[]{};:,.?/")

    remaining_pool = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{};:,.?/"
    remaining = [secrets.choice(remaining_pool) for _ in range(length - 4)]

    password_chars = [lower, upper, digit, special] + remaining
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def generate_passphrase(word_count: int = 4, include_number: bool = True, include_symbol: bool = True) -> str:
    if word_count < 3:
        word_count = 3

    words = [secrets.choice(WORDLIST).capitalize() for _ in range(word_count)]
    phrase = "-".join(words)

    if include_number:
        phrase += "-" + str(secrets.randbelow(9000) + 1000)

    if include_symbol:
        phrase += secrets.choice("!@#$%^&*")

    return phrase


# =========================
# RENDERING
# =========================
def render_score(score: int, rating: str, rating_color: str):
    if RICH_AVAILABLE:
        print_message(f"[bold {rating_color}][+] Password Score : {score}/100[/bold {rating_color}]")
        print_message(f"[bold {rating_color}][+] Strength       : {rating}[/bold {rating_color}]")
    else:
        color_map = {
            "green": Colors.GREEN,
            "yellow": Colors.YELLOW,
            "red": Colors.RED
        }
        chosen = color_map.get(rating_color, Colors.WHITE)
        print(chosen + f"[+] Password Score : {score}/100" + Colors.RESET)
        print(chosen + f"[+] Strength       : {rating}" + Colors.RESET)


def render_profile_summary(result: dict):
    print("\n" + Colors.CYAN + Colors.BOLD + "Credential Security Summary:" + Colors.RESET)

    border = "+------------------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'Checking':^30}|{'Status':^29}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)

    mutation_color = Colors.GREEN
    if result["mutation_risk"] == "Medium":
        mutation_color = Colors.YELLOW
    elif result["mutation_risk"] == "High":
        mutation_color = Colors.RED

    rows = [
        ("Policy Profile", result["policy_name"], Colors.CYAN),
        ("Entropy Bits", str(result["entropy"]), Colors.YELLOW),
        ("Crack Resistance", result["entropy_profile"], Colors.GREEN if result["entropy"] >= 60 else Colors.YELLOW if result["entropy"] >= 35 else Colors.RED),
        ("Mutation Risk", result["mutation_risk"], mutation_color),
        ("Usability", result["usability"], Colors.MAGENTA),
        ("Passphrase Mode", "YES" if result["passphrase_mode"] else "NO", Colors.GREEN if result["passphrase_mode"] else Colors.WHITE),
        ("Policy Compliant", "PASS" if result["policy_result"]["passed"] else "FAIL", Colors.GREEN if result["policy_result"]["passed"] else Colors.RED),
    ]

    for label, value, color in rows:
        print(
            Colors.WHITE + "|" +
            f"{label:<30}" +
            "|" +
            color + f"{str(value)[:29]:^29}" +
            Colors.WHITE + "|" +
            Colors.RESET
        )

    print(Colors.CYAN + border + Colors.RESET)


def render_checks_table(checks: dict, title: str = "Password Rule Checks"):
    print("\n" + Colors.CYAN + Colors.BOLD + title + ":" + Colors.RESET)

    border = "+----------------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'Checking':^42}|{'Status':^15}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)

    for check_name, passed in checks.items():
        status_text = "PASS" if passed else "FAIL"
        status_color = Colors.GREEN if passed else Colors.RED

        print(
            Colors.WHITE + "|" +
            f"{check_name:<42}" +
            "|" +
            status_color + f"{status_text:^15}" +
            Colors.WHITE + "|" +
            Colors.RESET
        )

    print(Colors.CYAN + border + Colors.RESET)


def render_feedback(feedback: list):
    print("\n" + Colors.MAGENTA + Colors.BOLD + "Improvement Suggestions:" + Colors.RESET)

    border = "+----------------------------------------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'#':^6}|{'Suggestions':^75}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)

    if not feedback:
        print(
            Colors.WHITE + "|" +
            f"{'-':^6}" +
            "|" +
            Colors.GREEN + f"{'No improvements needed':^75}" +
            Colors.WHITE + "|" +
            Colors.RESET
        )
    else:
        for idx, item in enumerate(feedback[:10], start=1):
            suggestion = item[:75]
            print(
                Colors.WHITE + "|" +
                f"{str(idx):^6}" +
                "|" +
                Colors.YELLOW + f"{suggestion:<75}" +
                Colors.WHITE + "|" +
                Colors.RESET
            )

    print(Colors.CYAN + border + Colors.RESET)


def render_generated_output(title: str, value: str):
    print("\n" + Colors.CYAN + Colors.BOLD + title + ":" + Colors.RESET)

    border = "+--------------------------------------------------------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'Generated Value':^98}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + "|" + Colors.GREEN + f"{value[:98]:^98}" + Colors.WHITE + "|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)


def render_generation_notes(kind: str):
    print("\n" + Colors.CYAN + Colors.BOLD + "Usage Notes:" + Colors.RESET)

    border = "+--------------------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'#':^6}|{'Recommendation':^55}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)

    if kind == "password":
        notes = [
            "Store it in a password manager.",
            "Avoid reusing it across systems.",
            "Prefer MFA for important accounts.",
            "Do not share it in chat or email.",
            "Rotate if exposure is suspected."
        ]
    else:
        notes = [
            "Passphrases are easier to remember.",
            "Use 4 or more words when possible.",
            "Keep separators and symbols included.",
            "Avoid famous quotes or public phrases.",
            "Still store securely if reused."
        ]

    for idx, item in enumerate(notes, start=1):
        print(
            Colors.WHITE + "|" +
            f"{str(idx):^6}" +
            "|" +
            Colors.YELLOW + f"{item[:55]:<55}" +
            Colors.WHITE + "|" +
            Colors.RESET
        )

    print(Colors.CYAN + border + Colors.RESET)


# =========================
# USER FLOWS
# =========================
def choose_policy_profile() -> dict:
    print(Colors.CYAN + "Choose a Policy Profile:" + Colors.RESET)
    for key, profile in POLICY_PROFILES.items():
        print(Colors.WHITE + f"{key}. {profile['name']}" + Colors.RESET)
    print()

    choice = ask_input("[bold yellow]Enter Choice [ 1 / 2 / 3 / 4 ] : [/bold yellow]").strip()
    return POLICY_PROFILES.get(choice, POLICY_PROFILES["1"])


def analyze_password_workflow():
    print()
    policy = choose_policy_profile()
    print()

    password = ask_input("[bold yellow]Enter Password to Analyze: [/bold yellow]", hidden=True)

    if not password:
        print_message("[bold red][!] Empty password entered. Exiting.[/bold red]")
        sys.exit(1)

    print()
    print_message(" A[yellow][-] Analyzing Password ...[/yellow]\n")

    result = analyze_password(password, policy)

    render_score(result["score"], result["rating"], result["rating_color"])
    print()
    render_profile_summary(result)
    print()
    render_checks_table(result["checks"], "Password Rule Checks")
    print()
    render_checks_table(result["policy_result"]["checks"], f"{policy['name']} Policy Checks")
    print()
    render_feedback(result["feedback"])


def generate_password_workflow():
    print()
    length_input = ask_input("[bold yellow]Enter Password Length [ Default 18 ] : [/bold yellow]").strip()
    length = 18
    if length_input.isdigit() and int(length_input) > 0:
        length = int(length_input)

    print()
    print_message(" G[yellow][-] Generating Strong Password ...[/yellow]\n")

    generated = generate_strong_password(length)
    result = analyze_password(generated, POLICY_PROFILES["2"])

    render_generated_output("Generated Strong Password", generated)
    print()
    render_score(result["score"], result["rating"], result["rating_color"])
    print()
    render_profile_summary(result)
    print()
    render_generation_notes("password")


def generate_passphrase_workflow():
    print()
    count_input = ask_input("[bold yellow]Enter Word Count [ Default 4 ] : [/bold yellow]").strip()
    word_count = 4
    if count_input.isdigit() and int(count_input) > 0:
        word_count = int(count_input)

    include_number = ask_input("[bold yellow]Include Number ? [Y/N]: [/bold yellow]").strip().lower() == "y"
    include_symbol = ask_input("[bold yellow]Include Symbol ? [Y/N]: [/bold yellow]").strip().lower() == "y"

    print()
    print_message("[yellow][-] Generating Secure Passphrase ...[/yellow]\n")

    generated = generate_passphrase(word_count, include_number, include_symbol)
    result = analyze_password(generated, POLICY_PROFILES["1"])

    render_generated_output("Generated Secure Passphrase", generated)
    print()
    render_score(result["score"], result["rating"], result["rating_color"])
    print()
    render_profile_summary(result)
    print()
    render_generation_notes("passphrase")


# =========================
# MAIN
# =========================
def main():
    print_banner()
    print("                                                   ")
    print_message(" M[blue][i] Mode        : Credential Security Workbench[/blue]")
    print_message(" I[blue][i] Input Style : Hidden Entry Enabled for Analysis[/blue]")
    print_message(" F[blue][i] Features    : Policy Profiles + Entropy + Mutation Risk + Generator[/blue]\n")

    try:
        print(Colors.CYAN + "Choose an Option:" + Colors.RESET)
        print(Colors.WHITE + "1. Analyze Password" + Colors.RESET)
        print(Colors.WHITE + "2. Generate Strong Password" + Colors.RESET)
        print(Colors.WHITE + "3. Generate Secure Passphrase" + Colors.RESET)
        print(Colors.WHITE + "4. Exit\n" + Colors.RESET)

        choice = ask_input("[bold yellow]Enter Choice [ 1 / 2 / 3 / 4 ] : [/bold yellow]").strip()

        if choice == "1":
            analyze_password_workflow()
        elif choice == "2":
            generate_password_workflow()
        elif choice == "3":
            generate_passphrase_workflow()
        elif choice == "4":
            print_message("[bold yellow][-] Exiting.[/bold yellow]")
            sys.exit(0)
        else:
            print_message("[bold red][!] Invalid Choice.[/bold red]")
            sys.exit(1)

    except KeyboardInterrupt:
        print_message("\n[bold red][!] Operation interrupted by user.[/bold red]")
        sys.exit(0)
    except Exception as exc:
        print_message(f"[bold red][!] Unexpected error: {exc}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
    time.sleep(60)
