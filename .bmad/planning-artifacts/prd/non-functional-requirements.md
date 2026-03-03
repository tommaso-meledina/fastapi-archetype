# Non-Functional Requirements

## Code Quality & Maintainability

- NFR1: The codebase follows a consistent code style enforced by linting tools (e.g., ruff, flake8, or similar)
- NFR2: The project structure is logically organized so that a developer unfamiliar with the codebase can locate any capability (model, route, test, AOP, config) within minutes
- NFR3: Each capability area (ORM, AOP, observability, configuration, etc.) is cleanly separated so it can be understood, modified, or replaced independently
- NFR4: The codebase contains no dead code, commented-out blocks, or placeholder implementations
- NFR5: Code comments are avoided altogether; comments are only permitted where they explain non-obvious intent or constraints that the code itself cannot convey

## Portability

- NFR6: The Docker image runs consistently across Linux and macOS environments without modification
- NFR7: The application has no host-specific dependencies beyond what is declared in `pyproject.toml` and the `.env` file

## Developer Experience

- NFR8: A developer can understand the project structure and the role of each module by reading the project's documentation and code organization alone
- NFR9: The patterns used for the `/dummies` resource (model, route, validation, tests, AOP, constants) are clear enough to serve as a copy-and-adapt template for new resources
- NFR10: All configuration values have sensible defaults or clear documentation of required values, so a developer can get the application running with minimal setup
