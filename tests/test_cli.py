"""Tests for OK Graphics CLI - Schema validation and command parsing.

These tests verify the CLI structure without requiring GPU/heavy dependencies.
Run with: pytest tests/ -v
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
CLI_PATH = PROJECT_ROOT / "scripts" / "cli.py"


def run_cli(args: list[str] | None = None) -> subprocess.CompletedProcess:
    """Run the CLI with given arguments."""
    cmd = [sys.executable, str(CLI_PATH)]
    if args:
        cmd.extend(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=10)


class TestMainHelp:
    """Test main help and version flags."""

    def test_help_flag(self):
        """Test --help shows usage."""
        result = run_cli(["--help"])
        assert result.returncode == 0
        assert "Usage: okgraphics" in result.stdout
        assert "generate:vector" in result.stdout
        assert "generate:anime" in result.stdout

    def test_help_short_flag(self):
        """Test -h shows usage."""
        result = run_cli(["-h"])
        assert result.returncode == 0
        assert "Usage: okgraphics" in result.stdout

    def test_version_flag(self):
        """Test --version shows version."""
        result = run_cli(["--version"])
        assert result.returncode == 0
        assert "okgraphics 0.1.0" in result.stdout

    def test_version_short_flag(self):
        """Test -v shows version."""
        result = run_cli(["-v"])
        assert result.returncode == 0
        assert "okgraphics" in result.stdout

    def test_no_args_shows_help(self):
        """Test no arguments shows help."""
        result = run_cli()
        assert result.returncode == 0
        assert "Usage: okgraphics" in result.stdout


class TestCommandHelp:
    """Test command-specific help."""

    def test_generate_vector_help(self):
        """Test generate:vector --help."""
        result = run_cli(["generate:vector", "--help"])
        assert result.returncode == 0
        assert "Command: generate:vector" in result.stdout
        assert "--lora" in result.stdout
        assert "--width" in result.stdout
        assert "Examples:" in result.stdout

    def test_generate_anime_help(self):
        """Test generate:anime --help."""
        result = run_cli(["generate:anime", "--help"])
        assert result.returncode == 0
        assert "Command: generate:anime" in result.stdout
        assert "--style" in result.stdout
        assert "--strength" in result.stdout

    def test_server_start_help(self):
        """Test server:start --help."""
        result = run_cli(["server:start", "--help"])
        assert result.returncode == 0
        assert "Command: server:start" in result.stdout
        assert "--port" in result.stdout
        assert "/generate/anime" in result.stdout

    def test_model_list_help(self):
        """Test model:list --help."""
        result = run_cli(["model:list", "--help"])
        assert result.returncode == 0
        assert "Command: model:list" in result.stdout


class TestCommandAliases:
    """Test command aliases work correctly."""

    @pytest.mark.parametrize("alias,expected_command", [
        ("vector", "generate:vector"),
        ("gen:vector", "generate:vector"),
        ("anime", "generate:anime"),
        ("gen:anime", "generate:anime"),
        ("style:anime", "generate:anime"),
        ("serve", "server:start"),
        ("api", "server:start"),
        ("models", "model:list"),
        ("loras", "model:list"),
    ])
    def test_alias_shows_correct_command(self, alias, expected_command):
        """Test that alias resolves to correct command."""
        result = run_cli([alias, "--help"])
        assert result.returncode == 0
        assert f"Command: {expected_command}" in result.stdout


class TestInvalidCommands:
    """Test error handling for invalid commands."""

    def test_invalid_command(self):
        """Test invalid command shows error."""
        result = run_cli(["invalid:command"])
        assert result.returncode == 1
        assert "Unknown command" in result.stderr

    def test_missing_required_argument(self):
        """Test missing required argument shows error."""
        result = run_cli(["generate:vector"])
        assert result.returncode != 0


class TestSchemaValidation:
    """Test that command schemas are valid."""

    def test_all_commands_have_schemas(self):
        """Test all commands are registered."""
        from src.commands import ALL_COMMANDS

        command_names = [cmd.name for cmd in ALL_COMMANDS]
        assert "generate:vector" in command_names
        assert "generate:anime" in command_names
        assert "server:start" in command_names
        assert "model:list" in command_names

    def test_all_schemas_have_required_fields(self):
        """Test all schemas have required fields."""
        from src.commands import ALL_COMMANDS

        for schema in ALL_COMMANDS:
            assert schema.name, f"Schema missing name"
            assert schema.category, f"{schema.name} missing category"
            assert schema.description, f"{schema.name} missing description"
            assert schema.handler, f"{schema.name} missing handler"

    def test_handler_references_format(self):
        """Test handler references are in correct format."""
        from src.commands import ALL_COMMANDS

        for schema in ALL_COMMANDS:
            assert ":" in schema.handler, f"{schema.name} handler not in 'module:function' format"
            parts = schema.handler.split(":")
            assert len(parts) == 2, f"{schema.name} handler has invalid format"
            assert parts[0].startswith("src."), f"{schema.name} handler module should start with 'src.'"
            assert parts[1].startswith("handle_"), f"{schema.name} handler function should start with 'handle_'"

    def test_no_duplicate_commands(self):
        """Test no duplicate command names."""
        from src.commands import ALL_COMMANDS

        names = [cmd.name for cmd in ALL_COMMANDS]
        assert len(names) == len(set(names)), "Duplicate command names found"

    def test_aliases_unique(self):
        """Test all aliases are unique."""
        from src.commands import ALL_COMMANDS

        all_aliases = []
        for cmd in ALL_COMMANDS:
            all_aliases.extend(cmd.aliases)

        assert len(all_aliases) == len(set(all_aliases)), "Duplicate aliases found"


class TestSeeAlsoReferences:
    """Test that see_also references point to valid commands."""

    def test_see_also_references_exist(self):
        """Test all see_also references point to valid commands."""
        from src.commands import ALL_COMMANDS

        valid_names = set()
        for cmd in ALL_COMMANDS:
            valid_names.add(cmd.name)
            valid_names.update(cmd.aliases)

        for schema in ALL_COMMANDS:
            for ref in schema.see_also:
                assert ref in valid_names, f"{schema.name} references unknown command: {ref}"


class TestConfigValidation:
    """Test configuration file is valid."""

    def test_config_is_valid_yaml(self):
        """Test config.yaml is valid YAML."""
        import yaml

        config_path = PROJECT_ROOT / "configs" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert config is not None
        assert "base_model" in config
        assert "loras" in config
        assert "generation" in config

    def test_lora_references_in_config(self):
        """Test LoRA references in config are consistent."""
        import yaml

        config_path = PROJECT_ROOT / "configs" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

        lora_names = set(config.get("loras", {}).keys())

        # Check generation presets reference valid LoRAs
        for preset_name, preset in config.get("generation", {}).items():
            if "lora" in preset:
                assert preset["lora"] in lora_names, f"Preset {preset_name} references unknown LoRA: {preset['lora']}"
