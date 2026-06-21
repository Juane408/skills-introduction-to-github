"""Tests for repository structure and required files."""

import pathlib


REQUIRED_ROOT_FILES = [
    "README.md",
    "LICENSE",
    ".gitignore",
]

REQUIRED_DIRECTORIES = [
    ".github",
    ".github/workflows",
    ".github/steps",
    "images",
]


class TestRequiredFiles:
    """Verify that all required top-level files exist."""

    def test_readme_exists(self, repo_root):
        assert (repo_root / "README.md").is_file()

    def test_license_exists(self, repo_root):
        assert (repo_root / "LICENSE").is_file()

    def test_gitignore_exists(self, repo_root):
        assert (repo_root / ".gitignore").is_file()

    def test_dependabot_config_exists(self, repo_root):
        assert (repo_root / ".github" / "dependabot.yml").is_file()

    def test_step_tracker_exists(self, repo_root):
        step_file = repo_root / ".github" / "steps" / "-step.txt"
        assert step_file.is_file(), "-step.txt tracker file is missing"

    def test_step_tracker_contains_valid_value(self, repo_root):
        step_file = repo_root / ".github" / "steps" / "-step.txt"
        content = step_file.read_text().strip()
        valid_values = {"0", "1", "2", "3", "4", "X"}
        assert content in valid_values, (
            f"Step tracker contains '{content}', expected one of {valid_values}"
        )


class TestRequiredDirectories:
    """Verify that required directories exist."""

    def test_github_dir(self, repo_root):
        assert (repo_root / ".github").is_dir()

    def test_workflows_dir(self, repo_root):
        assert (repo_root / ".github" / "workflows").is_dir()

    def test_steps_dir(self, repo_root):
        assert (repo_root / ".github" / "steps").is_dir()

    def test_images_dir(self, repo_root):
        assert (repo_root / "images").is_dir()


class TestLicense:
    """Validate the license file content."""

    def test_license_is_mit(self, repo_root):
        content = (repo_root / "LICENSE").read_text()
        assert "MIT License" in content or "Permission is hereby granted" in content

    def test_license_not_empty(self, repo_root):
        content = (repo_root / "LICENSE").read_text().strip()
        assert len(content) > 0


class TestGitignore:
    """Validate .gitignore has expected entries."""

    def test_gitignore_not_empty(self, repo_root):
        content = (repo_root / ".gitignore").read_text().strip()
        assert len(content) > 0

    def test_gitignore_excludes_os_files(self, repo_root):
        content = (repo_root / ".gitignore").read_text()
        assert ".DS_Store" in content

    def test_gitignore_excludes_compiled_files(self, repo_root):
        content = (repo_root / ".gitignore").read_text()
        assert "*.exe" in content or "*.o" in content


class TestDependabotConfig:
    """Validate dependabot.yml structure."""

    def test_dependabot_has_version(self, repo_root):
        import yaml

        path = repo_root / ".github" / "dependabot.yml"
        with open(path) as f:
            config = yaml.safe_load(f)
        assert config.get("version") == 2

    def test_dependabot_has_updates(self, repo_root):
        import yaml

        path = repo_root / ".github" / "dependabot.yml"
        with open(path) as f:
            config = yaml.safe_load(f)
        assert "updates" in config
        assert len(config["updates"]) > 0

    def test_dependabot_monitors_github_actions(self, repo_root):
        import yaml

        path = repo_root / ".github" / "dependabot.yml"
        with open(path) as f:
            config = yaml.safe_load(f)
        ecosystems = [u["package-ecosystem"] for u in config["updates"]]
        assert "github-actions" in ecosystems
