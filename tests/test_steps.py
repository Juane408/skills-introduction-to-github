"""Tests for step markdown files."""

import re

import pytest


EXPECTED_STEP_FILES = [
    "0-welcome.md",
    "1-create-a-branch.md",
    "2-commit-a-file.md",
    "3-open-a-pull-request.md",
    "4-merge-your-pull-request.md",
    "X-finish.md",
]

NUMBERED_STEPS = [
    "1-create-a-branch.md",
    "2-commit-a-file.md",
    "3-open-a-pull-request.md",
    "4-merge-your-pull-request.md",
]


class TestStepFilePresence:
    """Verify all expected step files exist."""

    @pytest.mark.parametrize("filename", EXPECTED_STEP_FILES)
    def test_step_file_exists(self, steps_dir, filename):
        assert (steps_dir / filename).is_file(), f"Missing step: {filename}"

    def test_no_unexpected_step_files(self, step_md_files):
        names = {f.name for f in step_md_files}
        expected = set(EXPECTED_STEP_FILES)
        unexpected = names - expected
        assert not unexpected, f"Unexpected step files: {unexpected}"


class TestStepContent:
    """Validate content of step markdown files."""

    @pytest.mark.parametrize("filename", EXPECTED_STEP_FILES)
    def test_step_is_not_empty(self, step_contents, filename):
        assert len(step_contents[filename].strip()) > 0, f"{filename} is empty"

    @pytest.mark.parametrize("filename", NUMBERED_STEPS)
    def test_step_has_heading(self, step_contents, filename):
        content = step_contents[filename]
        assert re.search(r"^##\s+Step\s+\d+", content, re.MULTILINE), (
            f"{filename} should contain a '## Step N' heading"
        )

    @pytest.mark.parametrize("filename", NUMBERED_STEPS)
    def test_step_heading_matches_number(self, step_contents, filename):
        step_num = filename.split("-")[0]
        content = step_contents[filename]
        pattern = rf"^##\s+Step\s+{step_num}"
        assert re.search(pattern, content, re.MULTILINE), (
            f"{filename} heading should reference Step {step_num}"
        )

    def test_finish_has_heading(self, step_contents):
        content = step_contents["X-finish.md"]
        assert re.search(r"^##\s+Finish", content, re.MULTILINE), (
            "X-finish.md should contain a '## Finish' heading"
        )


class TestStepActivity:
    """Verify that steps with activities have an Activity section."""

    @pytest.mark.parametrize("filename", NUMBERED_STEPS)
    def test_step_has_activity_section(self, step_contents, filename):
        content = step_contents[filename]
        has_activity = "Activity" in content
        assert has_activity, f"{filename} should describe an activity"


class TestStepLinks:
    """Verify that steps contain links to GitHub documentation."""

    @pytest.mark.parametrize("filename", NUMBERED_STEPS)
    def test_step_has_docs_links(self, step_contents, filename):
        content = step_contents[filename]
        assert "docs.github.com" in content or "github.com" in content, (
            f"{filename} should link to GitHub documentation"
        )


class TestStepProgression:
    """Ensure steps form a coherent tutorial progression."""

    def test_step_1_introduces_branches(self, step_contents):
        content = step_contents["1-create-a-branch.md"].lower()
        assert "branch" in content

    def test_step_2_introduces_commits(self, step_contents):
        content = step_contents["2-commit-a-file.md"].lower()
        assert "commit" in content

    def test_step_3_introduces_pull_requests(self, step_contents):
        content = step_contents["3-open-a-pull-request.md"].lower()
        assert "pull request" in content

    def test_step_4_introduces_merging(self, step_contents):
        content = step_contents["4-merge-your-pull-request.md"].lower()
        assert "merge" in content

    def test_finish_congratulates(self, step_contents):
        content = step_contents["X-finish.md"].lower()
        assert "congratulations" in content or "finish" in content


class TestWelcomeStep:
    """Validate the welcome step (0-welcome.md)."""

    def test_welcome_exists_and_is_minimal(self, step_contents):
        content = step_contents["0-welcome.md"].strip()
        assert len(content) > 0
