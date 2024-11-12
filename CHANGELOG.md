# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Conformance endpoint `/conformance` and root body `conformsTo` attribute.
- Endpoint /product/{productId}/order-parameters.
- Links in Product entity to order-parameters and constraints endpoints for that product.
- Add links `opportunities` and `create-order` to Product
- Add link `create-order` to OpportunityCollection

### Changed

none

### Deprecated

none

### Removed

none

### Fixed

none

### Security

none

## [v0.1.0] - 2024-10-23

Initial release

[unreleased]: https://github.com/stapi-spec/stapi-fastapi/compare/v0.1.0...main
[v0.1.0]: https://github.com/stapi-spec/stapi-fastapi/tree/v0.1.0
