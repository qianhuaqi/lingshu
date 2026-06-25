from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_handoff_scripts_exist():
    assert (ROOT / "scripts" / "resume-work.ps1").exists()
    assert (ROOT / "scripts" / "verify-handoff.ps1").exists()


def test_handoff_scripts_avoid_disallowed_git_operations():
    script_text = "\n".join(
        [
            _read("scripts/resume-work.ps1"),
            _read("scripts/verify-handoff.ps1"),
        ]
    ).lower()

    forbidden = [
        "reset --hard",
        "clean -fd",
        "push --force",
        "rebase",
        "stash",
    ]
    assert [term for term in forbidden if term in script_text] == []


def test_handoff_scripts_use_github_remote_and_fail_closed_checks():
    resume = _read("scripts/resume-work.ps1")
    verify = _read("scripts/verify-handoff.ps1")
    combined = f"{resume}\n{verify}"

    assert '"github"' in combined
    assert "Assert-CleanWorktree" in combined
    assert "Assert-HeadMatchesRemote" in combined
    assert "docs/codex/HANDOFF.md is missing" in combined
    assert "status\", \"--porcelain\"" in combined
    assert "\"rev-parse\"" in verify
    assert "github/$Branch" in verify


def test_agents_records_single_writer_rule_and_sources_of_truth():
    agents = _read("AGENTS.md")

    assert "GitHub remote is always `github`" in agents
    assert "A phase branch may be written by only one computer at a time." in agents
    assert "Codex chat history is not a source of truth." in agents
    assert "Business code must not import `lingshu.system`." in agents
    assert "Do not start phases C, D, E, or F." in agents


def test_current_phase_and_handoff_docs_exist_with_phase_b_context():
    current_phase = _read("docs/codex/CURRENT_PHASE.md")
    handoff = _read("docs/codex/HANDOFF.md")

    assert "Current phase: B" in current_phase
    assert "Current branch: codex/phase-b-lingshu-context" in current_phase
    assert "Current PR: #8" in current_phase
    assert "Next phase allowed: no" in current_phase
    assert "Branch: codex/phase-b-lingshu-context" in handoff
    assert "Work commit:" in handoff
    assert "Handoff commit:" in handoff


def test_readme_contains_cross_device_handoff_flow():
    readme = _read("README.md")

    assert "## 双机开发交接" in readme
    assert "scripts\\resume-work.ps1" in readme
    assert "scripts\\verify-handoff.ps1" in readme
    assert "[WORKING]" in readme
    assert "[HANDOFF]" in readme
    assert "office" in readme
    assert "home" in readme


def test_handoff_docs_do_not_contain_obvious_secret_examples():
    paths = [
        "AGENTS.md",
        "docs/codex/CURRENT_PHASE.md",
        "docs/codex/HANDOFF.md",
        "README.md",
        "scripts/resume-work.ps1",
        "scripts/verify-handoff.ps1",
    ]
    combined = "\n".join(_read(path) for path in paths)

    risky_patterns = [
        r"gh[pousr]_[A-Za-z0-9_]{20,}",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"sk-[A-Za-z0-9]{20,}",
        r"(?i)codex[_-]?token\s*=",
        r"(?i)password\s*=\s*['\"][^'\"]+['\"]",
    ]

    assert [pattern for pattern in risky_patterns if re.search(pattern, combined)] == []
