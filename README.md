# cco-action

GitHub composite action that runs a [cco](https://github.com/gezpage/orchestrator) pipeline stage-by-stage, driven by a GitHub issue overview.

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `profile` | yes | — | Profile name; must match `.github/cco/<profile>/profile.yaml` in your repo |
| `issue-number` | yes | — | Issue number whose body becomes `overview.md` for the pipeline |
| `cco-version` | no | `latest` | cco package version to install |

## Required secrets

Set these as repository or organisation secrets and expose them as job-level environment variables.

| Secret | Description |
|--------|-------------|
| `ANTHROPIC_AUTH_TOKEN` | Anthropic API auth token |
| `ANTHROPIC_BASE_URL` | API base URL (for proxy or gateway setups) |
| `ANTHROPIC_MODEL` | Model identifier (e.g. `claude-opus-4-7`) |

## Caller repo layout

```
.github/
  cco/
    <profile>/
      profile.yaml          # cco schema_version: 2 profile
      prompts/              # optional prompt extensions (can be empty dir)
project.yaml                # cco project config (repo-root, docs-root, etc.)
```

## Usage

```yaml
name: cco
on:
  issues:
    types: [labeled]

jobs:
  run:
    if: contains(github.event.issue.labels.*.name, 'cco-run')
    runs-on: ubuntu-latest
    env:
      ANTHROPIC_AUTH_TOKEN: ${{ secrets.ANTHROPIC_AUTH_TOKEN }}
      ANTHROPIC_BASE_URL: ${{ secrets.ANTHROPIC_BASE_URL }}
      ANTHROPIC_MODEL: ${{ secrets.ANTHROPIC_MODEL }}
    steps:
      - uses: actions/checkout@v4
      - uses: gezpage/cco-action@v1
        with:
          profile: default
          issue-number: ${{ github.event.issue.number }}
```

## What the action does

1. Installs `cco` and `cco-profiles` via `uv tool install`.
2. Fetches the issue body with `gh issue view` and writes it to `$RUNNER_TEMP/overview.md`.
3. Derives a URL-safe feature slug from the issue title.
4. Invokes `cco run` with explicit path flags pointing at `.github/cco/<profile>/` in your checked-out repo.
5. Writes `plan.md` to the GitHub Actions job summary on every exit (pass or fail).
6. Uploads the full run folder (`$RUNNER_TEMP/cco-run/`) as the `cco-run` artifact.

## Notes

- The `gh` CLI must be available on the runner. It is pre-installed on GitHub-hosted runners. Self-hosted runners need it installed separately.
- The `GITHUB_TOKEN` used for `gh issue view` is the default job token; no extra permissions are required beyond `issues: read`.
- `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, and `ANTHROPIC_MODEL` must be set as environment variables at the job level — composite actions cannot reference `secrets` directly.
