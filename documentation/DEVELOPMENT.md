# Development Notes

## CI

* Push tag to release

If it fails:

* Major CI changes: 
  * Work in branch _ci-test_ (starts dry-run automatically on push)
  * No code changes allowed (only CI and tooling)
  * Merge back into main
* Minor CI changes:
  * Fix in main
  * Trigger rebuild with SHA of release commit and "dry run" flag
* Once everything works, trigger rebuild with SHA of relese commit