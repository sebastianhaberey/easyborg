# Development Notes

## CI

### Release workflow

The release workflow can be started from everywhere and will dry-run the whole release process as close to the real
thing as possible. Nothing of consequence will happen, unless "live mode" is active.

#### Live mode

Live mode means actual PyPI deploy, release artifact upload, homebrew tap update etc. It's activated either
automatically when a tag is pushed or manually, when the user triggers the release workflow with "live mode" selected.
Live mode is only allowed on tags or main branch.

| Ref                | Live allowed | Live automatic |
|--------------------|--------------|----------------|
| refs/tags/v0.15.2  | yes          | yes            |
| refs/heads/main    | yes          | no             |
| refs/heads/feature | no           | no             |
| refs/pull/2/merge  | no           | no             |

#### Miscellaneous

- Release workflow deploys most recent tag
- Tooling in release workflow is HEAD of current branch
- Use [skip ci] for CI (workflow / tooling only) commits
- Use branch for CI commits and squash before merge
- No source code changes in CI commits