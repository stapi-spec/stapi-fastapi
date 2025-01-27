# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed
- Changed method to POST and added body to return of `create-order` link during `search_oppurtunities` calls.

### Deprecated

### Removed

### Fixed

### Security


## [v0.5.0] - 2025-01-08

### Added

- Endpoint `/orders/{order_id}/statuses` supporting `GET` for retrieving statuses. The entity returned by this conforms
  to the change proposed in [stapi-spec#239](https://github.com/stapi-spec/stapi-spec/pull/239).
- RootBackend has new method `get_order_statuses`
- `*args`/`**kwargs` support in RootRouter's `add_product` allows to configure underlyinging ProductRouter

### Changed

- OrderRequest renamed to OrderPayload

### Deprecated

none

### Removed

- Endpoint `/orders/{order_id}/statuses` supporting `POST` for updating current status was added and then
  removed prior to release
- RootBackend method `set_order_status` was added and then removed

### Fixed

- Exception logging

### Security

none

## [v0.4.0] - 2024-12-11

### Added

none

### Changed

- The concepts of Opportunity search Constraint and Opportunity search result Opportunity Properties are now separate,
  recognizing that they have related attributes, but not neither the same attributes or the same values for those attributes.

### Deprecated

none

### Removed

none

### Fixed

none

### Security

none


## [v0.3.0] - 2024-12-6

### Added

none

### Changed

- OrderStatusCode and ProviderRole are now StrEnum instead of (str, Enum)
- All types using `Result[A, Exception]` have been replace with the equivalent type `ResultE[A]`
- Order and OrderCollection extend _GeoJsonBase instead of Feature and FeatureCollection, to allow for tighter
  constraints on fields

### Deprecated

none

### Removed

none

### Fixed

none

### Security

none

## [v0.2.0] - 2024-11-23

### Added

none

### Changed

- RootBackend and ProductBackend protocols use `returns` library types Result and Maybe instead of
  raising exceptions.
- Create Order endpoint from `.../order` to `.../orders`
- Order field `id` must be a string, instead of previously allowing int. This is because while an
  order ID may an integral numeric value, it is not a "number" in the sense that math will be performed
  order ID values, so string represents this better.

### Deprecated

none

### Removed

none

### Fixed

none

### Security

none

## [v0.1.0] - 2024-11-15

Initial release

### Added

- Conformance endpoint `/conformance` and root body `conformsTo` attribute.
- Field `product_id` to Opportunity and Order Properties
- Endpoint /product/{productId}/order-parameters.
- Links in Product entity to order-parameters and constraints endpoints for
  that product.
- Add links `opportunities` and `create-order` to Product
- Add link `create-order` to OpportunityCollection

[unreleased]: https://github.com/stapi-spec/stapi-fastapi/compare/v0.5.0...main
[v0.4.0]: https://github.com/stapi-spec/stapi-fastapi/tree/v0.5.0
[v0.4.0]: https://github.com/stapi-spec/stapi-fastapi/tree/v0.4.0
[v0.3.0]: https://github.com/stapi-spec/stapi-fastapi/tree/v0.3.0
[v0.2.0]: https://github.com/stapi-spec/stapi-fastapi/tree/v0.2.0
[v0.1.0]: https://github.com/stapi-spec/stapi-fastapi/tree/v0.1.0
