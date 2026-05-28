# To install just: brew install just


# lists all targets
list:
  just -l

install-agy:
  #!/usr/bin/env bash
  set -euo pipefail
  TARGET_DIR="$HOME/.gemini/config/plugins/sre-extension"

  if [ -d "$TARGET_DIR" ] && [ -f "$TARGET_DIR/plugin.json" ]; then
      INSTALLED_VERSION=$(test/get_plugin_version.sh "$TARGET_DIR/plugin.json")
      WORKSPACE_VERSION=$(test/get_plugin_version.sh "{{justfile_directory()}}/plugin.json")
      if [ "$INSTALLED_VERSION" = "$WORKSPACE_VERSION" ]; then
          echo "🟢 SRE extension is already installed in $TARGET_DIR (version matches workspace: $INSTALLED_VERSION)"
      else
          echo "🟡 SRE extension is already installed in $TARGET_DIR (installed: $INSTALLED_VERSION vs workspace: $WORKSPACE_VERSION)"
      fi
      exit 0
  fi

  if [ -d "$TARGET_DIR" ]; then
      echo "❌ Directory $TARGET_DIR exists but plugin.json was not found." >&2
      echo "To perform a clean installation, please remove it manually first:" >&2
      echo "  rm -rf \"$TARGET_DIR\"" >&2
      exit 1
  fi

  mkdir -p "$HOME/.gemini/config/plugins"
  git clone https://github.com/gemini-cli-extensions/sre.git "$TARGET_DIR"

# Get the version from any JSON plugin/manifest file (defaults to plugin.json)
plugin-version filepath="plugin.json":
  @test/get_plugin_version.sh "{{filepath}}"

# Install SRE extension into gemini CLI extensions directory
install-geminicli:
  gemini extensions install https://github.com/gemini-cli-extensions/sre

# Run Claude Code with the plugin directory flag pointing to this directory
install-claude:
  claude --plugin-dir "{{justfile_directory()}}"

# Run all automated validation tests
test:
  test/run_tests.sh


