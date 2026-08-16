import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DOCS = ROOT / "docs"

TEXT = README.read_text()


def slug(heading):
    """GitHub's heading-anchor rule: lowercase, punctuation dropped, spaces hyphenated."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"\s+", "-", s)


def headings():
    return {slug(h) for h in re.findall(r"^#{2,3} (.+)$", TEXT, re.MULTILINE)}


def toc_anchors():
    block = re.search(r"^## Contents\n(.*?)^---", TEXT, re.MULTILINE | re.DOTALL)
    assert block, "README.md has no '## Contents' table of contents"
    return re.findall(r"\]\(#([\w-]+)\)", block.group(1))


def doc_files():
    return sorted(p for p in DOCS.rglob("*.md"))


def test_table_of_contents_exists_and_is_not_empty():
    assert len(toc_anchors()) >= 5


@pytest.mark.parametrize("anchor", toc_anchors())
def test_every_toc_entry_points_at_a_real_heading(anchor):
    """A table of contents whose links go nowhere is worse than none — it looks
    navigable and silently drops the reader at the top of the page."""
    assert anchor in headings(), f"'#{anchor}' matches no heading in README.md"


def test_every_section_is_listed_in_the_contents():
    """Adding a section without listing it makes the contents quietly incomplete."""
    listed = set(toc_anchors())
    missing = headings() - listed - {"contents"}
    assert not missing, f"sections missing from the table of contents: {sorted(missing)}"


@pytest.mark.parametrize("path", doc_files(), ids=lambda p: str(p.relative_to(ROOT)))
def test_every_docs_file_is_linked_from_the_readme(path):
    """An unlinked document is an unread one. The README is the only entry point
    most people use, so docs/ has to be reachable from it."""
    rel = str(path.relative_to(ROOT))
    assert f"({rel})" in TEXT, f"{rel} is not linked from README.md"


def test_docs_files_were_actually_found():
    assert len(doc_files()) >= 6
