# crontab-doctor

> A CLI tool that audits and validates crontab expressions with human-readable explanations and conflict detection.

---

## Installation

```bash
pip install crontab-doctor
```

Or install from source:

```bash
git clone https://github.com/yourname/crontab-doctor.git
cd crontab-doctor && pip install .
```

---

## Usage

Validate a single cron expression:

```bash
crontab-doctor check "*/5 * * * *"
# ✔ Runs every 5 minutes
```

Audit an entire crontab file:

```bash
crontab-doctor audit /etc/cron.d/myjobs

# Output:
# [line 3] ✔  0 9 * * 1-5   → Every weekday at 9:00 AM
# [line 7] ✔  30 2 * * 0    → Every Sunday at 2:30 AM
# [line 9] ⚠  0 9 * * 1-5   → Conflict: duplicate schedule detected (see line 3)
# [line 12] ✖  60 * * * *   → Invalid: minute value '60' out of range (0-59)
```

Explain a cron expression in plain English:

```bash
crontab-doctor explain "0 0 1 * *"
# Runs at midnight on the 1st of every month
```

---

## Features

- ✅ Validates cron expression syntax with detailed error messages
- 📖 Translates expressions into plain-English descriptions
- 🔍 Detects duplicate and conflicting schedules within a crontab file
- 📂 Supports reading from files or standard input

---

## License

[MIT](LICENSE) © 2024 yourname