"""Tests for format preservation."""
import pytest
from hookglot.format_preservation import preserve, PRESERVE_PATTERNS


def test_code_block_preservation():
    text = "Run this:\n```bash\nls -la\n```\nDone."
    doc = preserve(text)
    # Code block should be replaced with placeholder
    assert "ls -la" not in doc.text
    assert "⟨⟨" in doc.text and "⟩⟩" in doc.text
    # Restoration should give exact original
    assert doc.restore(doc.text) == text


def test_inline_code():
    text = "Use the `sudo -l` command"
    doc = preserve(text)
    assert "sudo -l" not in doc.text
    assert doc.restore(doc.text) == text


def test_url():
    text = "Visit https://example.com/path?q=1 for more"
    doc = preserve(text)
    assert "https://example.com" not in doc.text
    assert doc.restore(doc.text) == text


def test_ip_address():
    text = "Connect to 10.10.10.5:8080 first"
    doc = preserve(text)
    assert "10.10.10.5" not in doc.text


def test_email():
    text = "Email admin@example.com for help"
    doc = preserve(text)
    assert "admin@example.com" not in doc.text


def test_env_var():
    text = "Set $HOME and ${PATH} variables"
    doc = preserve(text)
    assert "$HOME" not in doc.text
    assert "${PATH}" not in doc.text


def test_path():
    text = "Edit /etc/passwd file"
    doc = preserve(text)
    assert "/etc/passwd" not in doc.text


def test_constants():
    text = "Use NTLM_HASH and NOPASSWD entry"
    doc = preserve(text)
    assert "NTLM_HASH" not in doc.text
    assert "NOPASSWD" not in doc.text


def test_simulated_translation_with_restoration():
    """Simulate translator preserving placeholders."""
    text = "Run `nmap -sV 10.10.10.5` to scan."
    doc = preserve(text)

    # Simulate translator output (preserving placeholders)
    # English: "Run X to scan." → Thai: "รัน X เพื่อ scan"
    translated = doc.text.replace("Run", "รัน").replace("to scan", "เพื่อ scan")

    result = doc.restore(translated)
    assert "nmap -sV 10.10.10.5" in result
    assert "รัน" in result


def test_multiple_code_blocks():
    text = "```py\nprint('a')\n```\nand\n```bash\necho hi\n```"
    doc = preserve(text)
    assert "print" not in doc.text
    assert "echo hi" not in doc.text
    assert doc.restore(doc.text) == text
