"""Human-readable explanation generator for crontab expressions."""

from .parser import CronExpression

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

DOW_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _explain_field(raw: str, unit: str, names: list = None) -> str:
    if raw == "*":
        return f"every {unit}"

    parts = []
    for segment in raw.split(","):
        segment = segment.strip()
        if "/" in segment:
            base, step = segment.split("/", 1)
            base_desc = "every" if base == "*" else f"starting at {unit} {base}"
            parts.append(f"every {step} {unit}s ({base_desc})")
        elif "-" in segment:
            low, high = segment.split("-", 1)
            low_name = names[int(low)] if names else low
            high_name = names[int(high)] if names else high
            parts.append(f"{low_name} through {high_name}")
        else:
            val = int(segment)
            label = names[val] if names else str(val)
            parts.append(label)

    return ", ".join(parts)


def explain(expr: CronExpression) -> str:
    """Generate a human-readable description of a cron expression."""
    fields = {f.name: f.raw for f in expr.fields}

    minute = _explain_field(fields["minute"], "minute")
    hour = _explain_field(fields["hour"], "hour")
    dom = _explain_field(fields["day_of_month"], "day")
    month = _explain_field(fields["month"], "month", MONTH_NAMES)
    dow = _explain_field(fields["day_of_week"], "weekday", DOW_NAMES)

    parts = []

    if fields["minute"] == "*" and fields["hour"] == "*":
        parts.append("every minute")
    elif fields["minute"] == "*":
        parts.append(f"every minute of {hour}")
    else:
        parts.append(f"at {minute} past {hour}")

    if fields["day_of_month"] != "*":
        parts.append(f"on day {dom} of the month")

    if fields["month"] != "*":
        parts.append(f"in {month}")

    if fields["day_of_week"] != "*":
        parts.append(f"on {dow}")

    description = ", ".join(parts)
    if expr.command:
        description += f" — runs: {expr.command}"

    return description.capitalize()
