# Contributing

TODO: Move most of the readme into here.

## Design Principles

### Route Names and Links

The route names used in route defintions should be constants in `stapi_fastapi.routers.route_names`. This
makes it easier to populate these links in numerous places, including in apps that use this library.

The general scheme for route names should follow:

- `create-{x}` - create a resource `x`
- `create-{x}-for-{y}` - create a resource `x` as a sub-resource or associated resource of `y`
- `get-{x}` - retrieve a resource `x`
- `list-{xs}` - retrieve a list of resources of type `x`
- `list-{xs}-for-{y}` - retrieve a list of subresources of type `x` of a resource `y`
- `set-{x}` - update an existing resource `x`
- `set-{x}-for-{y}` - set a sub-resource `x` of a resource `y`, e.g., `set-status-for-order`
