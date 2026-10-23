# Pull Request CI Validation

This document is used to verify that Jenkins automatically detects and tests a GitHub Pull Request before it is merged into `main`.

The Pull Request should run the security pipeline, including:

- SHA-256 helper-package integrity verification
- Bandit static security analysis
- pip-audit dependency vulnerability scanning
- All 18 automated security and functional tests
- Building and archiving the helper wheel artifact

The validation change does not modify application functionality or security controls.

The Pull Request must pass the required CI checks before it is considered ready for merging.