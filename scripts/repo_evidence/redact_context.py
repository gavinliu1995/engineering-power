#!/usr/bin/env python3
"""Redact credential values before repository evidence enters model context."""

from __future__ import annotations

import re


REDACTION = "[REDACTED]"

SECRET_KEY = (
    r"(?:pass(?:word|wd)?|pwd|secret|token|api[_-]?key|apikey|"
    r"access[_-]?key|client[_-]?secret|private[_-]?key|credentials?|"
    r"set[-_]?cookie|cookie)"
)

PRIVATE_KEY_BEGIN = re.compile(r"-----BEGIN [^-]*PRIVATE KEY-----", re.IGNORECASE)
PRIVATE_KEY_END = re.compile(r"-----END [^-]*PRIVATE KEY-----", re.IGNORECASE)

XML_ELEMENT = re.compile(
    rf"(?P<prefix><(?P<key>{SECRET_KEY})\b[^>]*>)"
    rf"(?P<value>.*?)"
    rf"(?P<suffix></(?P=key)\s*>)",
    re.IGNORECASE,
)

SET_COOKIE_COLLECTION = re.compile(
    r"(?P<prefix>"
    r"(?:\[\s*)?[\"']set[-_]?cookie[\"'](?:\s*\])?\s*[:=,]\s*"
    r")"
    r"(?P<value>\[[^\r\n]*\]|\([^\r\n]*\))",
    re.IGNORECASE,
)

SET_COOKIE_COLLECTION_START = re.compile(
    r"(?P<prefix>"
    r"(?:\[\s*)?[\"']set[-_]?cookie[\"'](?:\s*\])?\s*[:=,]\s*"
    r")"
    r"(?P<open>[\[(])(?P<tail>[^\r\n]*)$",
    re.IGNORECASE,
)

QUOTED_ASSIGNMENT = re.compile(
    rf"(?P<prefix>(?<![\w-])[\"']?{SECRET_KEY}[\"']?\s*[:=,]\s*"
    rf"(?:[rubf]{{1,2}})?)"
    rf"(?P<quote>[\"'])(?P<value>.*?)(?P=quote)",
    re.IGNORECASE,
)

UNQUOTED_ASSIGNMENT = re.compile(
    rf"(?P<prefix>(?<![\w-])[\"']?{SECRET_KEY}[\"']?\s*[:=]\s*)"
    rf"(?P<value>(?![rubf]{{1,2}}[\"'])[^\s,;<>\"']+)",
    re.IGNORECASE,
)

CLI_QUOTED = re.compile(
    rf"(?P<prefix>--{SECRET_KEY}(?:\s+|=))"
    rf"(?P<quote>[\"'])(?P<value>.*?)(?P=quote)",
    re.IGNORECASE,
)

CLI_UNQUOTED = re.compile(
    rf"(?P<prefix>--{SECRET_KEY}(?:\s+|=))(?P<value>[^\s,;]+)",
    re.IGNORECASE,
)

AUTHORIZATION = re.compile(
    r"(?P<prefix>\bAuthorization\s*:\s*(?:Bearer|Basic)\s+)"
    r"(?P<value>[^\s,;]+)",
    re.IGNORECASE,
)

COOKIE_HEADER = re.compile(
    r"(?P<prefix>\b(?:Cookie|Set-Cookie)\s*:\s*)(?P<value>.*)$",
    re.IGNORECASE,
)

URL_USER_INFO = re.compile(
    r"(?P<prefix>\b[a-z][a-z0-9+.-]*://[^\s/@:]+:)"
    r"(?P<value>[^\s/@]+)(?P<suffix>@)",
    re.IGNORECASE,
)


def _replace_value(match: re.Match[str]) -> str:
    return f"{match.group('prefix')}{REDACTION}"


def _replace_quoted_value(match: re.Match[str]) -> str:
    quote = match.group("quote")
    return f"{match.group('prefix')}{quote}{REDACTION}{quote}"


def _replace_wrapped_value(match: re.Match[str]) -> str:
    return f"{match.group('prefix')}{REDACTION}{match.group('suffix')}"


def _replace_structured_value(match: re.Match[str]) -> str:
    return f'{match.group("prefix")}"{REDACTION}"'


def _collection_end(
    value: str,
    opener: str,
    closer: str,
    depth: int,
) -> tuple[int | None, int]:
    quote = None
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if quote is not None:
            if character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in {'"', "'"}:
            quote = character
        elif character == opener:
            depth += 1
        elif character == closer:
            depth -= 1
            if depth == 0:
                return index, depth
    return None, depth


def redact_lines(lines: list[str]) -> list[str]:
    """Return redacted lines without changing their number or order."""
    redacted = []
    inside_private_key = False
    structured_collection: tuple[str, str, int] | None = None
    for line in lines:
        if structured_collection is not None:
            opener, closer, depth = structured_collection
            close_index, depth = _collection_end(line, opener, closer, depth)
            indentation = line[: len(line) - len(line.lstrip())]
            if close_index is None:
                redacted.append(f"{indentation}{REDACTION}")
                structured_collection = (opener, closer, depth)
            else:
                suffix = line[close_index + 1 :]
                redacted.append(f"{indentation}{REDACTION}{suffix}")
                structured_collection = None
            continue

        if PRIVATE_KEY_BEGIN.search(line):
            inside_private_key = True
            redacted.append(line)
            continue
        if inside_private_key:
            if PRIVATE_KEY_END.search(line):
                inside_private_key = False
                redacted.append(line)
            else:
                indentation = line[: len(line) - len(line.lstrip())]
                redacted.append(f"{indentation}{REDACTION}" if line else REDACTION)
            continue

        value = XML_ELEMENT.sub(_replace_wrapped_value, line)
        value = SET_COOKIE_COLLECTION.sub(_replace_structured_value, value)
        collection_start = SET_COOKIE_COLLECTION_START.search(value)
        if collection_start is not None:
            opener = collection_start.group("open")
            closer = "]" if opener == "[" else ")"
            close_index, depth = _collection_end(
                collection_start.group("tail"),
                opener,
                closer,
                1,
            )
            value = (
                value[: collection_start.start()]
                + collection_start.group("prefix")
                + f'"{REDACTION}"'
            )
            if close_index is None:
                structured_collection = (opener, closer, depth)
            else:
                value += collection_start.group("tail")[close_index + 1 :]
        value = COOKIE_HEADER.sub(_replace_value, value)
        value = AUTHORIZATION.sub(_replace_value, value)
        value = URL_USER_INFO.sub(_replace_wrapped_value, value)
        value = CLI_QUOTED.sub(_replace_quoted_value, value)
        value = CLI_UNQUOTED.sub(_replace_value, value)
        value = QUOTED_ASSIGNMENT.sub(_replace_quoted_value, value)
        value = UNQUOTED_ASSIGNMENT.sub(_replace_value, value)
        redacted.append(value)
    return redacted


def redact_text(text: str) -> str:
    """Redact credential values while preserving newline placement exactly."""
    if not text:
        return text
    pieces = text.splitlines(keepends=True)
    bodies = [piece.rstrip("\r\n") for piece in pieces]
    endings = [piece[len(body) :] for piece, body in zip(pieces, bodies)]
    redacted = redact_lines(bodies)
    return "".join(body + ending for body, ending in zip(redacted, endings))
