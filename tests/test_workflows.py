"""Tests for GitHub Actions workflow files."""

import re

import pytest
import yaml


EXPECTED_WORKFLOWS = [
    "0-welcome.yml",
    "1-create-a-branch.yml",
    "2-commit-a-file.yml",
    "3-open-a-pull-request.yml",
    "4-merge-your-pull-request.yml",
]


class TestWorkflowFilePresence:
    """Verify all expected workflow files exist."""

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_workflow_file_exists(self, workflows_dir, filename):
        assert (workflows_dir / filename).is_file(), f"Missing workflow: {filename}"

    def test_no_unexpected_workflow_files(self, workflow_files):
        names = {wf.name for wf in workflow_files}
        expected = set(EXPECTED_WORKFLOWS)
        unexpected = names - expected
        assert not unexpected, f"Unexpected workflow files: {unexpected}"


class TestWorkflowYAMLValidity:
    """Verify all workflow files are valid YAML."""

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_yaml_parses(self, workflows_dir, filename):
        path = workflows_dir / filename
        with open(path) as f:
            data = yaml.safe_load(f)
        assert data is not None, f"{filename} parsed to None"
        assert isinstance(data, dict), f"{filename} should parse to a dict"


class TestWorkflowStructure:
    """Validate the internal structure of each workflow."""

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_has_name(self, parsed_workflows, filename):
        wf = parsed_workflows[filename]
        assert "name" in wf, f"{filename} missing 'name'"
        assert isinstance(wf["name"], str)

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_has_on_trigger(self, parsed_workflows, filename):
        wf = parsed_workflows[filename]
        assert True in wf or "on" in wf, f"{filename} missing 'on' trigger"

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_has_jobs(self, parsed_workflows, filename):
        wf = parsed_workflows[filename]
        assert "jobs" in wf, f"{filename} missing 'jobs'"
        assert isinstance(wf["jobs"], dict)
        assert len(wf["jobs"]) > 0

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_has_permissions(self, parsed_workflows, filename):
        wf = parsed_workflows[filename]
        assert "permissions" in wf, f"{filename} missing 'permissions'"

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_contents_write_permission(self, parsed_workflows, filename):
        wf = parsed_workflows[filename]
        perms = wf.get("permissions", {})
        assert perms.get("contents") == "write", (
            f"{filename}: expected contents:write permission"
        )


class TestWorkflowStepProgression:
    """Validate that workflows correctly progress from one step to the next."""

    EXPECTED_PROGRESSION = {
        "0-welcome.yml": ("0", "1"),
        "1-create-a-branch.yml": ("1", "2"),
        "2-commit-a-file.yml": ("2", "3"),
        "3-open-a-pull-request.yml": ("3", "4"),
        "4-merge-your-pull-request.yml": ("4", "X"),
    }

    @pytest.mark.parametrize(
        "filename,expected",
        list(EXPECTED_PROGRESSION.items()),
        ids=list(EXPECTED_PROGRESSION.keys()),
    )
    def test_step_update_progression(self, workflows_dir, filename, expected):
        from_step, to_step = expected
        content = (workflows_dir / filename).read_text()
        assert f"from_step: {from_step}" in content, (
            f"{filename}: expected from_step: {from_step}"
        )
        assert f"to_step: {to_step}" in content, (
            f"{filename}: expected to_step: {to_step}"
        )


class TestGetCurrentStepJob:
    """Every workflow should have a get_current_step job."""

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_has_get_current_step_job(self, parsed_workflows, filename):
        wf = parsed_workflows[filename]
        assert "get_current_step" in wf["jobs"], (
            f"{filename} missing get_current_step job"
        )

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_get_current_step_uses_checkout(self, parsed_workflows, filename):
        job = parsed_workflows[filename]["jobs"]["get_current_step"]
        steps = job.get("steps", [])
        checkout_steps = [s for s in steps if s.get("uses", "").startswith("actions/checkout")]
        assert len(checkout_steps) > 0, (
            f"{filename}: get_current_step should use actions/checkout"
        )

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_get_current_step_has_outputs(self, parsed_workflows, filename):
        job = parsed_workflows[filename]["jobs"]["get_current_step"]
        assert "outputs" in job, (
            f"{filename}: get_current_step should define outputs"
        )
        assert "current_step" in job["outputs"], (
            f"{filename}: get_current_step should output current_step"
        )


class TestMainJobConditions:
    """Validate the conditional logic on the main action job."""

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_main_job_needs_get_current_step(self, parsed_workflows, filename):
        wf = parsed_workflows[filename]
        main_jobs = {
            k: v for k, v in wf["jobs"].items() if k != "get_current_step"
        }
        for job_name, job in main_jobs.items():
            needs = job.get("needs", [])
            if isinstance(needs, str):
                needs = [needs]
            assert "get_current_step" in needs, (
                f"{filename}/{job_name} should depend on get_current_step"
            )

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_main_job_checks_is_not_template(self, workflows_dir, filename):
        content = (workflows_dir / filename).read_text()
        assert "is_template" in content, (
            f"{filename} should check repository.is_template"
        )

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_main_job_runs_on_ubuntu(self, parsed_workflows, filename):
        wf = parsed_workflows[filename]
        main_jobs = {
            k: v for k, v in wf["jobs"].items() if k != "get_current_step"
        }
        for job_name, job in main_jobs.items():
            assert job.get("runs-on") == "ubuntu-latest", (
                f"{filename}/{job_name} should run on ubuntu-latest"
            )


class TestWorkflowUsesUpdateStepAction:
    """Validate the use of the skills/action-update-step action."""

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_uses_action_update_step(self, workflows_dir, filename):
        content = (workflows_dir / filename).read_text()
        assert "skills/action-update-step@v2" in content, (
            f"{filename} should use skills/action-update-step@v2"
        )

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_action_uses_github_token(self, workflows_dir, filename):
        content = (workflows_dir / filename).read_text()
        assert "secrets.GITHUB_TOKEN" in content, (
            f"{filename} should use secrets.GITHUB_TOKEN"
        )

    @pytest.mark.parametrize("filename", EXPECTED_WORKFLOWS)
    def test_action_targets_my_first_branch(self, workflows_dir, filename):
        content = (workflows_dir / filename).read_text()
        assert "branch_name: my-first-branch" in content, (
            f"{filename} should target branch my-first-branch"
        )
