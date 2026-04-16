"""Built-in cron expression templates with descriptions."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Template:
    name: str
    expression: str
    description: str
    tags: List[str] = field(default_factory=list)
    category: str = "general"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "expression": self.expression,
            "description": self.description,
            "tags": self.tags,
            "category": self.category,
        }

    def __repr__(self) -> str:
        return f"Template(name={self.name!r}, expression={self.expression!r})"


BUILTIN_TEMPLATES: List[Template] = [
    Template("every-minute", "* * * * *", "Run every minute", ["frequent"], "general"),
    Template("every-5-minutes", "*/5 * * * *", "Run every 5 minutes", ["frequent"], "general"),
    Template("every-15-minutes", "*/15 * * * *", "Run every 15 minutes", ["frequent"], "general"),
    Template("every-30-minutes", "*/30 * * * *", "Run every 30 minutes", ["general"], "general"),
    Template("hourly", "0 * * * *", "Run once per hour", ["hourly"], "general"),
    Template("daily-midnight", "0 0 * * *", "Run daily at midnight", ["daily"], "general"),
    Template("daily-noon", "0 12 * * *", "Run daily at noon", ["daily"], "general"),
    Template("weekly-sunday", "0 0 * * 0", "Run every Sunday at midnight", ["weekly"], "general"),
    Template("weekly-monday", "0 0 * * 1", "Run every Monday at midnight", ["weekly"], "general"),
    Template("monthly-first", "0 0 1 * *", "Run on the 1st of each month", ["monthly"], "general"),
    Template("monthly-last", "0 0 28 * *", "Run on the 28th (safe last-ish day)", ["monthly"], "general"),
    Template("weekdays-morning", "0 8 * * 1-5", "Weekdays at 8am", ["weekday", "business"], "business"),
    Template("yearly", "0 0 1 1 *", "Run once a year on Jan 1", ["yearly"], "general"),
    Template("backup-nightly", "0 2 * * *", "Nightly backup at 2am", ["backup", "daily"], "ops"),
    Template("cleanup-weekly", "0 3 * * 0", "Weekly cleanup Sunday 3am", ["cleanup", "weekly"], "ops"),
]


def list_templates(category: Optional[str] = None, tag: Optional[str] = None) -> List[Template]:
    results = BUILTIN_TEMPLATES
    if category:
        results = [t for t in results if t.category == category]
    if tag:
        results = [t for t in results if tag in t.tags]
    return results


def find_template(name: str) -> Optional[Template]:
    for t in BUILTIN_TEMPLATES:
        if t.name == name:
            return t
    return None
