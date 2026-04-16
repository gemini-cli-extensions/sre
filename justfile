list:
    just -l

# runs all tests
test:
    #!/usr/bin/env bash
    set -e
    for f in test/*.py; do \
    	echo "Running $f..."; \
    	python3 "$f"; \
    done

test-skills:
    python3 test/check_skills_frontmatter.py --no-warnings

check-ok-for-commit:
    gemini -p "/pre-publish-checker Che its all good for publication"
