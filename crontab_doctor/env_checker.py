"""Environment variable checker for crontab expressions.

Detects references to environment variables in cron commands and
reports whether those variables are defined in the current environment.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional

_ENV_VAR_RE = re.compile(r"\$\{?(\w+)\}?")


@dataclass
class EnvCheckResult:
    expression: str
    command: Optional[str]
    referenced: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    defined: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.missing) == 0

    def summary(self) -> str:
        if not self.referenced:
            return "No environment variables referenced."
        parts = []
        if self.defined:
            parts.append(f"Defined: {', '.join(self.defined)}")
        if self.missing:
            parts.append(f"Missing: {', '.join(self.missing)}")
        return " | ".join(parts)


def extract_env_vars(command: str) -> List[str]:
    """Return unique environment variable names referenced in *command*."""
    return list(dict.fromkeys(_ENV_VAR_RE.findall(command)))


def check_env(expression: str, command: Optional[str] = None,
              environ: Optional[dict] = None) -> EnvCheckResult:
    """Check that every env-var referenced in *command* is present.

    Parameters
    ----------
    expression:
        The raw cron expression string (stored for reporting).
    command:
        The shell command associated with the cron job.
    environ:
        Mapping to check against; defaults to ``os.environ``.
    """
    if environ is None:
        environ = os.environ  # type: ignore[assignment]

    result = EnvCheckResult(expression=expression, command=command)

    if not command:
        return result

    refs = extract_env_vars(command)
    result.referenced = refs
    for var in refs:
        if var in environ:
            result.defined.append(var)
        else:
            result.missing.append(var)
    return result
