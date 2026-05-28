list:
  just -l

# Install SRE extension into agy CLI plugins directory
install-agy:
  mkdir -p ~/.gemini/config/plugins
  git clone git@github.com:gemini-cli-extensions/sre.git ~/.gemini/config/plugins/sre-extension

# Install SRE extension into gemini CLI extensions directory
install-geminicli:
  gemini extensions install https://github.com/gemini-cli-extensions/sre
