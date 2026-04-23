#!/usr/bin/env python3

import sys
import time
import re
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from pathlib import Path
from urllib.parse import urlparse

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


PHISHING_KEYWORDS = [
    "urgent", "immediately", "verify", "account suspended", "click below",
    "reset your password", "confirm your identity", "unusual activity",
    "payment failed", "invoice attached", "security alert", "limited time",
    "final warning", "act now", "your account will be closed", "login now",
    "update your account", "wire transfer", "gift card", "password expires"
]

SUSPICIOUS_TLDS = {
    ".ru", ".cn", ".tk", ".xyz", ".top", ".gq", ".ml", ".work", ".buzz", ".click"
}

SUSPICIOUS_ATTACHMENT_EXTENSIONS = {
    ".exe", ".scr", ".js", ".vbs", ".bat", ".cmd", ".ps1", ".hta", ".zip", ".iso", ".img"
}

TRUSTED_BRAND_KEYWORDS = [
    "microsoft", "paypal", "google", "apple", "amazon", "bank", "office365", "outlook"
]


def print_message(message: str):
    print(message + Colors.RESET)


def ask_input(prompt: str) -> str:
    return input(Colors.YELLOW + prompt + Colors.RESET)


def print_banner():
    banner = r"""
        +-----------------------------------------------------------------+
        |      ____  _     _     _        ____                     _      |
        |     |  _ \| |__ (_)___| |__    / ___|_   _  __ _ _ __ __| |     |
        |     | |_) | '_ \| / __| '_ \  | |  _| | | |/ _` | '__/ _` |     |
        |     |  __/| | | | \__ \ | | | | |_| | |_| | (_| | | | (_| |     |
        |     |_|   |_| |_|_|___/_| |_|  \____|\__,_|\__,_|_|  \__,_|     |
        |                                                                 |
        |                  Phishing Email Analyzer                        |
        +-----------------------------------------------------------------+
"""
    print(Colors.RED + banner + Colors.RESET)
    print(Colors.CYAN + "[*] Internship Portfolio Edition" + Colors.RESET)
    print(Colors.GREEN + "[*] Author: Sajjid" + Colors.RESET)
    print(Colors.YELLOW + "[*] Engine: Email Header / Link / Content Analysis" + Colors.RESET)
    print("                                                       ")


def load_email_content(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        print_message(Colors.RED + f"[!] File not found: {file_path}")
        sys.exit(1)

    if path.suffix.lower() == ".eml":
        return parse_eml_file(path)

    return parse_text_email(path)


def parse_eml_file(path: Path) -> dict:
    try:
        with open(path, "rb") as f:
            msg = BytesParser(policy=policy.default).parse(f)

        subject = str(msg.get("Subject", "")).strip()
        from_header = str(msg.get("From", "")).strip()
        reply_to = str(msg.get("Reply-To", "")).strip()
        return_path = str(msg.get("Return-Path", "")).strip()
        auth_results = str(msg.get("Authentication-Results", "")).strip()
        received_spf = str(msg.get("Received-SPF", "")).strip()
        dkim_sig = str(msg.get("DKIM-Signature", "")).strip()

        body_parts = []
        attachments = []

        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", "")).lower()
                filename = part.get_filename()

                if filename:
                    attachments.append(str(filename))

                if part.get_content_type() == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body_parts.append(part.get_content())
                    except Exception:
                        pass
                elif part.get_content_type() == "text/html" and "attachment" not in content_disposition:
                    try:
                        body_parts.append(part.get_content())
                    except Exception:
                        pass
        else:
            try:
                body_parts.append(msg.get_content())
            except Exception:
                pass

        return {
            "subject": subject,
            "from": from_header,
            "reply_to": reply_to,
            "return_path": return_path,
            "auth_results": auth_results,
            "received_spf": received_spf,
            "dkim_signature": dkim_sig,
            "body": "\n".join(body_parts),
            "attachments": attachments,
            "raw_headers": str(msg)
        }

    except Exception as exc:
        print_message(Colors.RED + f"[!] Failed to parse EML file: {exc}")
        sys.exit(1)


def parse_text_email(path: Path) -> dict:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")

        subject_match = re.search(r"^Subject:\s*(.*)$", content, re.MULTILINE | re.IGNORECASE)
        from_match = re.search(r"^From:\s*(.*)$", content, re.MULTILINE | re.IGNORECASE)
        reply_to_match = re.search(r"^Reply-To:\s*(.*)$", content, re.MULTILINE | re.IGNORECASE)
        return_path_match = re.search(r"^Return-Path:\s*(.*)$", content, re.MULTILINE | re.IGNORECASE)
        auth_results_match = re.search(r"^Authentication-Results:\s*(.*)$", content, re.MULTILINE | re.IGNORECASE)
        received_spf_match = re.search(r"^Received-SPF:\s*(.*)$", content, re.MULTILINE | re.IGNORECASE)

        return {
            "subject": subject_match.group(1).strip() if subject_match else "",
            "from": from_match.group(1).strip() if from_match else "",
            "reply_to": reply_to_match.group(1).strip() if reply_to_match else "",
            "return_path": return_path_match.group(1).strip() if return_path_match else "",
            "auth_results": auth_results_match.group(1).strip() if auth_results_match else "",
            "received_spf": received_spf_match.group(1).strip() if received_spf_match else "",
            "dkim_signature": "",
            "body": content,
            "attachments": re.findall(r"\b[A-Za-z0-9_.-]+\.(?:exe|scr|js|vbs|bat|cmd|ps1|hta|zip|iso|img|pdf|docm|xlsm)\b", content, re.IGNORECASE),
            "raw_headers": content
        }

    except Exception as exc:
        print_message(Colors.RED + f"[!] Failed to parse text email: {exc}")
        sys.exit(1)


def extract_email_domain(value: str) -> str:
    _, email_addr = parseaddr(value)
    if "@" in email_addr:
        return email_addr.split("@", 1)[1].lower()
    return ""


def extract_urls(text: str) -> list:
    urls = re.findall(r"https?://[^\s\"'<>]+", text, re.IGNORECASE)
    cleaned = []
    for url in urls:
        cleaned.append(url.rstrip(").,;>\"'"))
    return sorted(set(cleaned))


def count_phishing_keywords(text: str) -> list:
    lowered = text.lower()
    return [kw for kw in PHISHING_KEYWORDS if kw in lowered]


def detect_brand_impersonation(subject: str, body: str, sender_domain: str) -> list:
    hits = []
    combined = f"{subject} {body}".lower()

    for brand in TRUSTED_BRAND_KEYWORDS:
        if brand in combined and brand not in sender_domain:
            hits.append(brand)

    return sorted(set(hits))


def analyze_urls(urls: list) -> list:
    results = []

    for url in urls:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        suspicious_reasons = []

        if any(host.endswith(tld) for tld in SUSPICIOUS_TLDS):
            suspicious_reasons.append("Suspicious TLD")

        if "@" in url:
            suspicious_reasons.append("Uses @ in URL")

        if re.search(r"\d+\.\d+\.\d+\.\d+", host):
            suspicious_reasons.append("Direct IP in URL")

        if any(word in host for word in ["login", "verify", "secure", "update", "account", "auth"]):
            suspicious_reasons.append("Suspicious hostname keywords")

        if len(host) > 40:
            suspicious_reasons.append("Long hostname")

        results.append({
            "url": url,
            "host": host,
            "suspicious": len(suspicious_reasons) > 0,
            "reasons": suspicious_reasons
        })

    return results


def analyze_attachments(attachments: list) -> list:
    results = []

    for item in attachments:
        lowered = item.lower()
        reasons = []

        for ext in SUSPICIOUS_ATTACHMENT_EXTENSIONS:
            if lowered.endswith(ext):
                reasons.append(f"Suspicious extension {ext}")
                break

        if re.search(r"\.(docm|xlsm|pptm)$", lowered):
            reasons.append("Macro-enabled office file")

        if re.search(r"(invoice|payment|urgent|receipt|remittance)", lowered):
            reasons.append("Social engineering style filename")

        results.append({
            "name": item,
            "suspicious": len(reasons) > 0,
            "reasons": reasons
        })

    return results


def analyze_authentication(email_data: dict) -> dict:
    auth_results = email_data["auth_results"].lower()
    received_spf = email_data["received_spf"].lower()
    dkim_signature = email_data["dkim_signature"]

    spf = "Unknown"
    dkim = "Unknown"
    dmarc = "Unknown"

    if "spf=pass" in auth_results or "pass" in received_spf:
        spf = "PASS"
    elif "spf=fail" in auth_results or "fail" in received_spf:
        spf = "FAIL"

    if "dkim=pass" in auth_results or dkim_signature:
        dkim = "PASS" if "dkim=pass" in auth_results or dkim_signature else "Unknown"
    elif "dkim=fail" in auth_results:
        dkim = "FAIL"

    if "dmarc=pass" in auth_results:
        dmarc = "PASS"
    elif "dmarc=fail" in auth_results:
        dmarc = "FAIL"

    return {
        "spf": spf,
        "dkim": dkim,
        "dmarc": dmarc
    }


def analyze_email(email_data: dict) -> dict:
    subject = email_data["subject"]
    from_header = email_data["from"]
    reply_to = email_data["reply_to"]
    return_path = email_data["return_path"]
    body = email_data["body"]
    attachments = email_data["attachments"]

    sender_domain = extract_email_domain(from_header)
    reply_to_domain = extract_email_domain(reply_to)
    return_path_domain = extract_email_domain(return_path)

    urls = extract_urls(body)
    url_analysis = analyze_urls(urls)
    keyword_hits = count_phishing_keywords(subject + " " + body)
    attachment_analysis = analyze_attachments(attachments)
    auth = analyze_authentication(email_data)
    impersonation_hits = detect_brand_impersonation(subject, body, sender_domain)

    reply_mismatch = False
    if reply_to_domain and sender_domain and reply_to_domain != sender_domain:
        reply_mismatch = True

    return_path_mismatch = False
    if return_path_domain and sender_domain and return_path_domain != sender_domain:
        return_path_mismatch = True

    risk_score = 0

    risk_score += min(len(keyword_hits) * 5, 25)
    risk_score += min(sum(1 for x in url_analysis if x["suspicious"]) * 10, 30)
    risk_score += min(sum(1 for x in attachment_analysis if x["suspicious"]) * 12, 24)

    if reply_mismatch:
        risk_score += 15

    if return_path_mismatch:
        risk_score += 10

    if auth["spf"] == "FAIL":
        risk_score += 15
    if auth["dkim"] == "FAIL":
        risk_score += 15
    if auth["dmarc"] == "FAIL":
        risk_score += 20

    if len(impersonation_hits) > 0:
        risk_score += 15

    if not subject.strip():
        risk_score += 5

    risk_score = min(risk_score, 100)

    if risk_score >= 60:
        risk_level = "High"
    elif risk_score >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "subject": subject or "Not Found",
        "from": from_header or "Not Found",
        "reply_to": reply_to or "Not Found",
        "return_path": return_path or "Not Found",
        "sender_domain": sender_domain or "Unknown",
        "reply_to_domain": reply_to_domain or "Unknown",
        "return_path_domain": return_path_domain or "Unknown",
        "reply_mismatch": reply_mismatch,
        "return_path_mismatch": return_path_mismatch,
        "urls": urls,
        "url_analysis": url_analysis,
        "keyword_hits": keyword_hits,
        "attachments": attachments,
        "attachment_analysis": attachment_analysis,
        "authentication": auth,
        "impersonation_hits": impersonation_hits,
        "risk_score": risk_score,
        "risk_level": risk_level
    }


def render_summary_table(result: dict):
    print("\n" + Colors.CYAN + Colors.BOLD + "Phishing Analysis Summary:" + Colors.RESET)

    border = "+------------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'Checking':^38}|{'Status':^15}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)

    risk_color = Colors.GREEN
    if result["risk_level"] == "Medium":
        risk_color = Colors.YELLOW
    elif result["risk_level"] == "High":
        risk_color = Colors.RED

    rows = [
        ("Subject", result["subject"][:15], Colors.WHITE),
        ("Sender Domain", result["sender_domain"][:15], Colors.GREEN),
        ("Reply-To Domain", result["reply_to_domain"][:15], Colors.YELLOW),
        ("URL Count", str(len(result["urls"])), Colors.CYAN),
        ("Attachment Count", str(len(result["attachments"])), Colors.MAGENTA),
        ("Risk Score", str(result["risk_score"]), risk_color),
        ("Risk Level", result["risk_level"], risk_color),
    ]

    for label, value, color in rows:
        print(
            Colors.WHITE + "|" +
            f"{label:<38}" +
            "|" +
            color + f"{value:^15}" +
            Colors.WHITE + "|" +
            Colors.RESET
        )

    print(Colors.CYAN + border + Colors.RESET)


def render_auth_table(auth: dict, reply_mismatch: bool, return_path_mismatch: bool):
    print("\n" + Colors.MAGENTA + Colors.BOLD + "Authentication and Sender Checks:" + Colors.RESET)

    border = "+------------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'Checking':^38}|{'Status':^15}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)

    def color_for_status(value: str):
        if value == "PASS":
            return Colors.GREEN
        if value == "FAIL":
            return Colors.RED
        return Colors.YELLOW

    rows = [
        ("SPF", auth["spf"], color_for_status(auth["spf"])),
        ("DKIM", auth["dkim"], color_for_status(auth["dkim"])),
        ("DMARC", auth["dmarc"], color_for_status(auth["dmarc"])),
        ("Reply-To Mismatch", "YES" if reply_mismatch else "NO", Colors.RED if reply_mismatch else Colors.GREEN),
        ("Return-Path Mismatch", "YES" if return_path_mismatch else "NO", Colors.RED if return_path_mismatch else Colors.GREEN),
    ]

    for label, value, color in rows:
        print(
            Colors.WHITE + "|" +
            f"{label:<38}" +
            "|" +
            color + f"{value:^15}" +
            Colors.WHITE + "|" +
            Colors.RESET
        )

    print(Colors.CYAN + border + Colors.RESET)


def render_list_table(title: str, items: list, color: str, empty_text: str):
    print("\n" + color + Colors.BOLD + title + ":" + Colors.RESET)

    border = "+----------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'#':^6}|{'Value':^45}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)

    if not items:
        print(
            Colors.WHITE + "|" +
            f"{'-':^6}" +
            "|" +
            Colors.GREEN + f"{empty_text:^45}" +
            Colors.WHITE + "|" +
            Colors.RESET
        )
    else:
        for idx, item in enumerate(items, start=1):
            value = str(item)[:45]
            print(
                Colors.WHITE + "|" +
                f"{str(idx):^6}" +
                "|" +
                color + f"{value:<45}" +
                Colors.WHITE + "|" +
                Colors.RESET
            )

    print(Colors.CYAN + border + Colors.RESET)


def render_url_table(url_analysis: list):
    print("\n" + Colors.CYAN + Colors.BOLD + "URL Analysis:" + Colors.RESET)

    border = "+----------------------------------------------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'#':^5}|{'Host':^28}|{'Suspicious':^12}|{'Reason Count':^15}|{'URL':^24}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)

    if not url_analysis:
        print(Colors.WHITE + f"|{'-':^5}|{'None':^28}|{'-':^12}|{'0':^15}|{'None':^24}|" + Colors.RESET)
    else:
        for idx, item in enumerate(url_analysis, start=1):
            suspicious_text = "YES" if item["suspicious"] else "NO"
            suspicious_color = Colors.RED if item["suspicious"] else Colors.GREEN
            print(
                Colors.WHITE + "|" +
                f"{idx:^5}" +
                "|" +
                Colors.YELLOW + f"{item['host'][:28]:<28}" +
                Colors.WHITE + "|" +
                suspicious_color + f"{suspicious_text:^12}" +
                Colors.WHITE + "|" +
                f"{str(len(item['reasons'])):^15}" +
                "|" +
                f"{item['url'][:24]:<24}" +
                "|" +
                Colors.RESET
            )

    print(Colors.CYAN + border + Colors.RESET)


def render_attachment_table(attachment_analysis: list):
    print("\n" + Colors.MAGENTA + Colors.BOLD + "Attachment Analysis:" + Colors.RESET)

    border = "+-----------------------------------------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'#':^5}|{'Attachment':^35}|{'Suspicious':^12}|{'Reason Count':^15}|{'Type':^12}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)

    if not attachment_analysis:
        print(Colors.WHITE + f"|{'-':^5}|{'None':^35}|{'-':^12}|{'0':^15}|{'-':^12}|" + Colors.RESET)
    else:
        for idx, item in enumerate(attachment_analysis, start=1):
            suspicious_text = "YES" if item["suspicious"] else "NO"
            suspicious_color = Colors.RED if item["suspicious"] else Colors.GREEN
            ext = Path(item["name"]).suffix[:12] if item["name"] else "-"
            print(
                Colors.WHITE + "|" +
                f"{idx:^5}" +
                "|" +
                Colors.YELLOW + f"{item['name'][:35]:<35}" +
                Colors.WHITE + "|" +
                suspicious_color + f"{suspicious_text:^12}" +
                Colors.WHITE + "|" +
                f"{str(len(item['reasons'])):^15}" +
                "|" +
                f"{ext:^12}" +
                "|" +
                Colors.RESET
            )

    print(Colors.CYAN + border + Colors.RESET)


def render_recommendations(result: dict):
    print("\n" + Colors.CYAN + Colors.BOLD + "Recommendations:" + Colors.RESET)

    border = "+----------------------------------------------------+"
    print(Colors.CYAN + border + Colors.RESET)
    print(Colors.WHITE + f"|{'#':^6}|{'Recommendation':^45}|" + Colors.RESET)
    print(Colors.CYAN + border + Colors.RESET)

    recommendations = []

    if result["risk_level"] == "High":
        recommendations.append("Treat as likely phishing.")
        recommendations.append("Do not click links or open attachments.")
        recommendations.append("Block sender/domain if confirmed.")
        recommendations.append("Search mailboxes for similar emails.")
    elif result["risk_level"] == "Medium":
        recommendations.append("Review links and sender carefully.")
        recommendations.append("Validate message with sender independently.")
        recommendations.append("Inspect email headers in more detail.")
    else:
        recommendations.append("No strong phishing signs detected.")
        recommendations.append("Continue cautious verification.")

    if result["reply_mismatch"]:
        recommendations.append("Investigate sender vs reply-to mismatch.")

    if result["authentication"]["spf"] == "FAIL" or result["authentication"]["dkim"] == "FAIL" or result["authentication"]["dmarc"] == "FAIL":
        recommendations.append("Authentication checks indicate elevated risk.")

    if result["attachments"]:
        recommendations.append("Sandbox suspicious attachments before opening.")

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


def main():
    print_banner()

    print_message(Colors.BLUE + "[i] Mode        : Phishing Email Analysis")
    print_message(Colors.BLUE + "[i] Input Type  : Text-Based Email or EML File")
    print_message(Colors.BLUE + "[i] Detection   : Sender / Link / Header / Content Risk\n")

    try:
        file_path = ask_input("Enter Email File Path: ").strip()

        if not file_path:
            print_message(Colors.RED + "[!] No File Path Provided.")
            sys.exit(1)

        print()
        print_message(Colors.YELLOW + "[-] Loading Email...")
        email_data = load_email_content(file_path)

        print_message(Colors.YELLOW + "[-] Analyzing Phishing Indicators...\n")
        result = analyze_email(email_data)

        render_summary_table(result)
        render_auth_table(result["authentication"], result["reply_mismatch"], result["return_path_mismatch"])
        render_list_table("Phishing Keyword Hits", result["keyword_hits"], Colors.YELLOW, "None Found")
        render_list_table("Brand Impersonation Hints", result["impersonation_hits"], Colors.RED, "None Found")
        render_url_table(result["url_analysis"])
        render_attachment_table(result["attachment_analysis"])
        render_recommendations(result)

    except KeyboardInterrupt:
        print_message("\n" + Colors.RED + "[!] Analysis Interrupted by User.")
        sys.exit(0)
    except Exception as exc:
        print_message(Colors.RED + f"[!] Unexpected Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    time.sleep(60)