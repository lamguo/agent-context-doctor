from __future__ import annotations

import re
from typing import List, Optional

BEGIN_RE = re.compile(r"<!--\s*agentctx:begin\s*-->")
END_RE = re.compile(r"<!--\s*agentctx:end\s*-->")
AGENTCTX_MARKER_RE = re.compile(r"<!--\s*agentctx:[^>]*-->")
KNOWN_AGENTCTX_MARKER_RE = re.compile(
    r"<!--\s*agentctx:(?:source\s+[^>]+|hash\s+[a-fA-F0-9]+|begin|end)\s*-->"
)
GENERATED_BLOCK_RE = re.compile(
    r"(?:<!--\s*agentctx:source[^\n]*-->\n)?"
    r"(?:<!--\s*agentctx:hash\s+[a-fA-F0-9]+\s*-->\n)?"
    r"<!--\s*agentctx:begin\s*-->\n"
    r".*?"
    r"<!--\s*agentctx:end\s*-->",
    re.DOTALL,
)


def current_generated_block(text: str) -> Optional[str]:
    match = GENERATED_BLOCK_RE.search(text)
    return match.group(0).strip() if match else None


def has_generated_block(text: str) -> bool:
    return GENERATED_BLOCK_RE.search(text) is not None


def find_agentctx_marker_conflicts(text: str) -> List[str]:
    """Return agentctx marker snippets that are unsafe or ambiguous.

    agent-context-doctor owns only these HTML markers:
    source, hash, begin, end. Any other `agentctx:` marker could belong to a
    user or another tool, so sync should not silently overwrite around it.
    Also flag unbalanced begin/end markers because they make replacement
    ambiguous.
    """
    conflicts: List[str] = []
    for match in AGENTCTX_MARKER_RE.finditer(text):
        marker = match.group(0)
        if not KNOWN_AGENTCTX_MARKER_RE.fullmatch(marker):
            conflicts.append(marker)

    begin_count = len(BEGIN_RE.findall(text))
    end_count = len(END_RE.findall(text))
    if begin_count != end_count:
        conflicts.append("unbalanced agentctx:begin/end markers")

    if (begin_count or end_count) and not has_generated_block(text):
        conflicts.append("agentctx generated block markers are malformed")

    return sorted(dict.fromkeys(conflicts))
