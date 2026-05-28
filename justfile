list:
  just -l

# Install SRE extension into agy CLI plugins directory
install-agy:
  mkdir -p ~/.gemini/config/plugins
  git clone git@github.com:gemini-cli-extensions/sre.git ~/.gemini/config/plugins/sre-extension

# Install SRE extension into gemini CLI extensions directory
install-geminicli:
  gemini extensions install https://github.com/gemini-cli-extensions/sre

# Run Claude Code with the plugin directory flag pointing to this directory
install-claude:
  claude --plugin-dir "{{justfile_directory()}}"

# Run all automated validation tests
test:
  test/run_tests.sh

