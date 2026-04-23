"""Canonical repo-local gate command registry shared by dispatch and audits."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import cast

DEVTOOLS_MODULE = "oaknational.python_repo_template.devtools"
GATE_CONTRACT_PATH = Path(__file__).with_name("gate_contract.toml")


@dataclass(frozen=True, slots=True)
class GateCommand:
    """Map a repo-local devtools command name to its handler."""

    name: str
    handler_name: str


@lru_cache(maxsize=1)
def _load_default_gate_contract() -> dict[str, object]:
    return cast(dict[str, object], tomllib.loads(GATE_CONTRACT_PATH.read_text(encoding="utf-8")))


def load_gate_contract(path: Path = GATE_CONTRACT_PATH) -> dict[str, object]:
    """Load the gate contract from disk."""

    if path == GATE_CONTRACT_PATH:
        return _load_default_gate_contract()
    return cast(dict[str, object], tomllib.loads(path.read_text(encoding="utf-8")))


def _object_mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        msg = "Expected a TOML table."
        raise ValueError(msg)

    mapping: dict[str, object] = {}
    for key, item in cast(dict[object, object], value).items():
        if not isinstance(key, str):
            msg = "Expected a TOML table with string keys."
            raise ValueError(msg)
        mapping[key] = item
    return mapping


def _string_mapping(value: object) -> dict[str, str]:
    raw_mapping = _object_mapping(value)
    mapping: dict[str, str] = {}
    for key, item in raw_mapping.items():
        if not isinstance(item, str):
            msg = "Expected a TOML table containing only string values."
            raise ValueError(msg)
        mapping[key] = item
    return mapping


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        msg = "Expected a TOML list containing only strings."
        raise ValueError(msg)

    items: list[str] = []
    for item in cast(list[object], value):
        if not isinstance(item, str):
            msg = "Expected a TOML list containing only strings."
            raise ValueError(msg)
        items.append(item)
    return tuple(items)


def _canonical_gate_commands(contract: dict[str, object] | None = None) -> tuple[GateCommand, ...]:
    data = load_gate_contract() if contract is None else contract
    repo_local_commands = _string_mapping(data.get("repo_local_commands"))
    return tuple(
        GateCommand(name=name, handler_name=handler_name)
        for name, handler_name in repo_local_commands.items()
    )


CANONICAL_GATE_COMMANDS = _canonical_gate_commands()


def canonical_gate_names() -> tuple[str, ...]:
    """Return the canonical repo-local gate-command names in display order."""

    return tuple(command.name for command in CANONICAL_GATE_COMMANDS)


def repo_local_command_targets(contract: dict[str, object] | None = None) -> dict[str, str]:
    """Return the canonical repo-local command-to-handler mapping."""

    commands = _canonical_gate_commands(contract)
    return {command.name: f"{DEVTOOLS_MODULE}:{command.handler_name}" for command in commands}


def gate_sequence(name: str, contract: dict[str, object] | None = None) -> tuple[str, ...]:
    """Return the named gate-step sequence from the canonical contract."""

    data = load_gate_contract() if contract is None else contract
    raw_sequences = _object_mapping(data.get("gate_sequences"))
    return _string_tuple(raw_sequences.get(name))
