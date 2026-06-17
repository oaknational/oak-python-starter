from __future__ import annotations

from pathlib import Path

import pytest

import oaknational.python_repo_template.gate_registry as subject

GATE_CONTRACT = """
[repo_local_commands]
clean = "clean"
check = "check"
check-ci = "check_ci"

[gate_sequences]
check = ["format", "test"]
check-ci = ["format", "typecheck", "test"]
""".strip()


def test_repo_local_command_targets_and_sequences_follow_the_contract(tmp_path: Path) -> None:
    contract_path = tmp_path / "gate_contract.toml"
    contract_path.write_text(f"{GATE_CONTRACT}\n", encoding="utf-8")

    contract = subject.load_gate_contract(contract_path)

    assert subject.repo_local_command_targets(contract) == {
        "clean": "oaknational.python_repo_template.devtools:clean",
        "check": "oaknational.python_repo_template.devtools:check",
        "check-ci": "oaknational.python_repo_template.devtools:check_ci",
    }
    assert subject.gate_sequence("check-ci", contract) == ("format", "typecheck", "test")


def test_gate_registry_rejects_malformed_contract_shapes() -> None:
    with pytest.raises(ValueError, match="Expected a TOML table containing only string values."):
        subject.repo_local_command_targets({"repo_local_commands": {"check": 1}})

    with pytest.raises(ValueError, match="Expected a TOML list containing only strings."):
        subject.gate_sequence("check-ci", {"gate_sequences": {"check-ci": ["format", 1]}})
