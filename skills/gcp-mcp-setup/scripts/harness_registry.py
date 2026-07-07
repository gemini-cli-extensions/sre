#!/usr/bin/env python3
"""Central harness registry for the gcp-mcp-setup skill.

Single source of truth for:
  - MCP config file paths (global and local) per harness
  - MCP server entry format builders per harness
  - CLI commands per harness (keyed by HarnessCommand enum)

To add a new harness, add one HarnessConfig entry to HARNESS_REGISTRY below.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class HarnessCommand(str, Enum):
    """Abstract command names supported across harnesses.
    Using str mixin allows instances to be used directly as dict keys and in string contexts.
    """
    MCP_LIST = "mcp_list"


class HarnessName(str, Enum):
    """Known CLI harness identifiers.
    Using str mixin means HARNESS_REGISTRY[args.harness] works without casting,
    since argparse returns a plain string that compares equal to the enum value.
    """
    GEMINI      = "gemini"
    ANTIGRAVITY = "antigravity"
    COPILOT     = "copilot"


@dataclass(frozen=True)
class HarnessConfig:
    """Typed configuration for a single CLI harness."""
    global_paths: list[str]
    local_paths: list[str]
    builder: Callable[..., dict]
    commands: dict[HarnessCommand, list[str]]

    def paths(self, scope: str) -> list[str]:
        """Returns config file paths for the given scope ('global' or 'local')."""
        return self.global_paths if scope == "global" else self.local_paths

    def get_command(self, key: "HarnessCommand") -> list[str]:
        """Returns the command list for the given key.

        Raises ValueError if the key is absent, None, or maps to an empty list.
        """
        cmd = self.commands.get(key)
        if not cmd:
            raise ValueError(f"No command defined for '{key}' in this harness config.")
        return cmd


def _gemini_mcp_format(url, *, project_id=None, api_key=None):
    """Returns an MCP server entry in the Gemini/Antigravity format."""
    if api_key:
        return {"httpUrl": url, "serverUrl": url, "headers": {"X-Goog-Api-Key": api_key}}
    return {
        "httpUrl": url,
        "serverUrl": url,
        "authProviderType": "google_credentials",
        "oauth": {"scopes": ["https://www.googleapis.com/auth/cloud-platform"]},
        "headers": {"X-goog-user-project": project_id},
    }


def _copilot_mcp_format(url, *, project_id=None, api_key=None):
    """Returns an MCP server entry in the Copilot CLI format."""
    headers = {"X-Goog-Api-Key": api_key} if api_key else {"X-goog-user-project": project_id}
    return {"type": "http", "url": url, "headers": headers, "tools": ["*"]}


HARNESS_REGISTRY: dict[HarnessName, HarnessConfig] = {
    HarnessName.GEMINI: HarnessConfig(
        global_paths=["~/.gemini/settings.json"],
        local_paths=[".gemini/settings.json"],
        builder=_gemini_mcp_format,
        commands={HarnessCommand.MCP_LIST: ["gemini", "-p", "/mcp list"]},
    ),
    HarnessName.ANTIGRAVITY: HarnessConfig(
        global_paths=["~/.gemini/antigravity/mcp_config.json", "~/.gemini/config/mcp_config.json"],
        local_paths=[".gemini/antigravity/mcp_config.json", ".gemini/config/mcp_config.json"],
        builder=_gemini_mcp_format,
        commands={HarnessCommand.MCP_LIST: ["agy", "-p", "/mcp list"]},
    ),
    HarnessName.COPILOT: HarnessConfig(
        # Copilot CLI has no workspace-level MCP config; both scopes resolve to
        # the same global path, so --local and --global behave identically.
        global_paths=["~/.copilot/mcp-config.json"],
        local_paths=["~/.copilot/mcp-config.json"],
        builder=_copilot_mcp_format,
        commands={HarnessCommand.MCP_LIST: ["copilot", "mcp", "list"]},
    ),
}
