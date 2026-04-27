# HashGuard 🧾

HashGuard is the file hashing and integrity verification module inside the ForensicBox forensic toolkit.

This module is built to validate whether a file has remained unchanged by calculating cryptographic hash values.

---

## 🔍 Module Purpose

In digital forensics, one of the most critical requirements is preserving evidence integrity.

HashGuard helps verify:

- whether a file was modified
- whether two files are identical
- whether digital evidence remains trustworthy

---

## ⚙️ Features

- Generate File Hashes
- Compare Hash Values
- Detect File Tampering
- Evidence Integrity Validation

---

## 🔐 Supported Algorithms

- MD5
- SHA1
- SHA256

---

## ▶️ Run Module

```bash
python hashguard.py
