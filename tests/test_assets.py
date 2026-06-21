"""Tests for image assets and markdown image references."""

import re

import pytest


EXPECTED_IMAGES = [
    "profile-readme-example.png",
    "code-tab.png",
    "main-branch-dropdown.png",
    "create-branch-button.png",
    "my-profile-file.png",
    "commit-full-screen.png",
    "create-new-file.png",
    "compare-and-pull-request.png",
    "pull-request-branches.png",
    "Pull-request-description.png",
    "Actions-to-step-4.png",
    "Green-merge-pull-request.png",
    "delete-branch.png",
    "create-new-repository.png",
]


class TestImageFilePresence:
    """Verify all expected image files exist."""

    @pytest.mark.parametrize("filename", EXPECTED_IMAGES)
    def test_image_exists(self, images_dir, filename):
        assert (images_dir / filename).is_file(), f"Missing image: {filename}"

    def test_images_directory_is_not_empty(self, images_dir):
        images = list(images_dir.glob("*.png"))
        assert len(images) > 0, "images/ directory should contain PNG files"


class TestImageReferencesInReadme:
    """Verify that images referenced in README.md actually exist."""

    def test_all_image_refs_resolve(self, repo_root):
        readme = (repo_root / "README.md").read_text()
        refs = re.findall(r"!\[.*?\]\((/images/[^)]+)\)", readme)
        missing = []
        for ref in refs:
            img_path = repo_root / ref.lstrip("/")
            if not img_path.is_file():
                missing.append(ref)
        assert not missing, f"README references missing images: {missing}"


class TestImageReferencesInSteps:
    """Verify that images referenced in step markdown files exist."""

    def test_all_step_image_refs_resolve(self, repo_root, step_contents):
        missing = []
        for filename, content in step_contents.items():
            refs = re.findall(r"!\[.*?\]\((/images/[^)]+)\)", content)
            for ref in refs:
                img_path = repo_root / ref.lstrip("/")
                if not img_path.is_file():
                    missing.append(f"{filename}: {ref}")
        assert not missing, f"Step files reference missing images: {missing}"


class TestImageFileSizes:
    """Ensure image files are not zero-length."""

    @pytest.mark.parametrize("filename", EXPECTED_IMAGES)
    def test_image_is_not_empty(self, images_dir, filename):
        path = images_dir / filename
        if path.is_file():
            assert path.stat().st_size > 0, f"{filename} is empty (0 bytes)"


class TestImageFormats:
    """Validate image file format by checking PNG header bytes."""

    PNG_HEADER = b"\x89PNG\r\n\x1a\n"

    @pytest.mark.parametrize("filename", EXPECTED_IMAGES)
    def test_png_has_valid_header(self, images_dir, filename):
        path = images_dir / filename
        if path.is_file():
            with open(path, "rb") as f:
                header = f.read(8)
            assert header == self.PNG_HEADER, (
                f"{filename} does not have a valid PNG header"
            )
