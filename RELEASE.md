# Releasing stapi-fastapi

Publishing a stapi-fastapi package build to PyPI is triggered by publishing a
GitHub release. Tags are the [semantic version number](https://semver.org/)
proceeded by a `v`, such as `v0.0.1`.

Release notes for the changes for each release should be tracked in
[CHANGELOG.md](./CHANGELOG.md). The notes for each release in GitHub should
generally match those in the CHANGELOG.

## Release process

1. Prepare the release.
   1. Figure out the next release version (following semantic versioning
      conventions).
   1. Ensure [CHANGELOG.md](./CHANGELOG.md) has all necessary changes and
      release notes under this next release version. Typically this step is
      simply a matter of adding the header for the next version below
      `Unreleased` then reviewing the list of changes therein.
   1. Ensure links are tracked as best as possible to relevant commits and/or
      PRs.
1. Make a PR with the release prep changes, get it reviewed, and merge.
1. Draft a new GitHub release.
   1. Create a new tag with the release version prefixed with the character `v`.
   1. Title the release the same name as the tag.
   1. Copy the release notes from [CHANGELOG.md](./CHANGELOG.md) for this
      release version into the release description.
1. Publish the release and ensure it builds and pushes to PyPI successfully.
