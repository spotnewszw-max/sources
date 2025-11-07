---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## Describe the bug
<!-- A clear and concise description of what the bug is -->

## To Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

## Expected behavior
<!-- What you expected to happen -->

## Actual behavior
<!-- What actually happened -->

## Additional context
- Python version:
- OS:
- Package version:

Branch name pattern: main

Check these boxes:
✓ Require a pull request before merging
✓ Require approvals (set to 1)
✓ Dismiss stale pull request approvals when new commits are pushed
✓ Require status checks to pass before merging
✓ Require branches to be up to date before merging
✓ Status checks that are required:
  - test (the CI job from your workflow)

      - name: Run tests with coverage
        run: |
          python -m pytest -v tests/ --cov=src --cov-report=xml --cov-fail-under=80

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
          min_coverage: 80