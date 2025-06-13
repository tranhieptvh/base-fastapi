# Git Flow and Commit Convention

## Git Flow

We use Git Flow to manage branches in the project.

### Main Branches

- **main**: The main branch contains production-ready source code.
- **develop**: The main development branch, which contains completed features ready for the next release.

### Supporting Branches

- **feature/**: For developing new features.
  - Before starting, create an issue on GitHub to track the feature.
  - Branches from: `develop`
  - Merges into: `develop`
  - Naming convention: `feature/<issue-id>-<feature-name>`
- **release/**: For preparing a new release.
  - Branches from: `develop`
  - Merges into: `main` and `develop`
  - Naming convention: `release/<version>`
- **hotfix/**: For fixing critical bugs in a released version.
  - Branches from: `main`
  - Merges into: `main` and `develop`
  - Naming convention: `hotfix/<bug-description>`
- **bugfix/**: For fixing non-critical bugs.
    - Branches from: `develop`
    - Merges into: `develop`
    - Naming convention: `bugfix/<bug-description>`

### Basic Workflow

1.  Create an issue on GitHub to describe the new feature.
2.  Start a new feature branch (e.g., for issue #123):
    ```bash
    git checkout develop
    git pull
    git checkout -b feature/123-new-feature
    ```
3.  Finish the feature and merge it into `develop`:
    ```bash
    git checkout develop
    git merge --no-ff feature/123-new-feature
    git push
    git branch -d feature/123-new-feature
    ```

---

## Commit Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

### Commit Format

Each commit message consists of a **header**, a **body**, and a **footer**.

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

### Type

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries such as documentation generation

### Examples

```
feat(api): add new endpoint to get user information
```

```
fix(auth): fix authentication failure with expired token

Details about the bug and how it was fixed.
```

```
docs(readme): update installation guide
``` 