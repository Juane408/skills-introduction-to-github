import os
import pathlib

import pytest
import yaml


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
STEPS_DIR = REPO_ROOT / ".github" / "steps"
IMAGES_DIR = REPO_ROOT / "images"

WORKFLOW_FILES = sorted(WORKFLOWS_DIR.glob("*.yml"))
STEP_MD_FILES = sorted(STEPS_DIR.glob("*.md"))


@pytest.fixture(scope="session")
def repo_root():
    return REPO_ROOT


@pytest.fixture(scope="session")
def workflows_dir():
    return WORKFLOWS_DIR


@pytest.fixture(scope="session")
def steps_dir():
    return STEPS_DIR


@pytest.fixture(scope="session")
def images_dir():
    return IMAGES_DIR


@pytest.fixture(scope="session")
def workflow_files():
    return WORKFLOW_FILES


@pytest.fixture(scope="session")
def parsed_workflows():
    """Return a dict mapping filename -> parsed YAML content."""
    result = {}
    for wf in WORKFLOW_FILES:
        with open(wf) as f:
            result[wf.name] = yaml.safe_load(f)
    return result


@pytest.fixture(scope="session")
def step_md_files():
    return STEP_MD_FILES


@pytest.fixture(scope="session")
def step_contents():
    """Return a dict mapping filename -> file text."""
    result = {}
    for md in STEP_MD_FILES:
        result[md.name] = md.read_text()
    return result
