# Constraints and Opportunity Properties

Previously, the Constraints and Opportunity Properties were the same
concept/representation. However, these represent distinct but related
attributes. Constraints represents the terms that can be used in the filter sent
to the Opportunities Search and Order Create endpoints. These are frequently the
same or related values that will be part of the STAC Items that are used to
fulfill an eventual Order. Opportunity Properties represent the expected range
of values that these STAC Items are expected to have. An opportunity is a
prediction about the future, and as such, the values for the Opportunity are
fuzzy. For example, the sun azimuth angle will (likely) be within a predictable
range of values, but the exact value will not be known until after the capture
occurs. Therefore, it is necessary to describe the Opportunity in a way that
describes these ranges.

For example, for the concept of "off_nadir":

The Constraint will be a term "off_nadir" that can be a value 0 to 45.
This is used in a CQL2 filter to the Opportunities Search endpoint to restrict the allowable values from 0 to 15
The Opportunity that is returned from Search has an Opportunity Property
"off_nadir" with a description that the value of this field in the resulting
STAC Items will be between 4 and 8, which falls within the filter restriction of 0-15.
An Order is created with the original filter and other fields.
The Order is fulfilled with a STAC Item that has an off_nadir value of 4.8.

As of Dec 2024, the STAPI spec says only that the Opportunity Properties must
have a datetime interval field `datetime` and a `product_id` field. The
remainder of the Opportunity description proprietary is up to the provider to
define. The example given this this repo for `off_nadir` is of a custom format
with a "minimum" and "maximum" field describing the limits.

## JSON Schema

Another option would be to use either a full JSON Schema definition for an
attribute value in the properties (e.g., `schema`) or individual attribute
definitions for the properties values. This option should be investigated
further in the future.

JSON Schema is a well-defined specification language that can support this type
of data description. It is already used as the language for OGC API Queryables
to define the constraints on various terms that may be used in CQL2 expressions,
and likewise within STAPI for the Constraints that are used in Opportunity
Search and the Order Parameters that are set on an order. The use of JSON Schema
for Constraints (as with Queryables) is not to specify validation for a JSON
document, but rather to well-define a set of typed and otherwise-constrained
terms. Similarly, JSON Schema would be used for the Opportunity to define the
predicted ranges of properties within the Opportunity that is bound to fulfill
an Order.

The geometry is not one of the fields that will be expressed as a schema
constraint, since this is part of the Opportunity/Item/Feature top-level. The
Opportunity geometry will express both uncertainty about the actual capture area
and a “maximum extent” of capture, e.g., a small area within a larger data strip
– this is intentionally vague so it can be used to express whatever semantics
the provider wants.

The ranges of predicted Opportunity values can be expressed using JSON in the following way:

- numeric value - number with const, enum, or minimum/maximum/exclusiveMinimum/exclusiveMaximum
- string value - string with const or enum
- datetime - type string using format date-time. The limitation wit this is that
    these values are not treated with JSON Schema as temporal, but rather a string
    pattern. As such, there is no formal way to define a temporal interval that the
    instance value must be within. Instead, we will repurpose the description field
    as a datetime interval in the same format as a search datetime field, e.g.,
    2024-01-01T00:00:00Z/2024-01-07T00:00:00Z.  Optionally, the pattern field can be
    defined if the valid datetime values also match a regular expression, e.g.,
    2024-01-0[123456]T.*, which while not as useful semantically as the description
    interval does provide a formal validation of the resulting object, which waving
    hand might be useful in some way waving hand.

```json
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "schema.json",
    "type": "object",
    "properties": {
        "datetime": {
            "title": "Datetime",
            "type": "string",
            "format": "date-time",
            "description": "2024-01-01T00:00:00Z/2024-01-07T00:00:00Z",
            "pattern": "2024-01-0[123456]T.*"
        },
        "sensor_type": {
            "title": "Sensor Type",
            "type": "string",
            "const": "2"
        },
        "craft_id": {
            "title": "Spacecraft ID",
            "type": "string",
            "enum": [
                "7",
                "8"
            ]
        },
        "view:sun_elevation": {
            "title": "View:Sun Elevation",
            "type": "number",
            "minimum": 30.0,
            "maximum": 35.0
        },
        "view:azimuth": {
            "title": "View:Azimuth",
            "type": "number",
            "exclusiveMinimum": 104.0,
            "exclusiveMaximum": 115.0
        },
        "view:off_nadir": {
            "title": "View:Off Nadir",
            "type": "number",
            "minimum": 0.0,
            "maximum": 9.0
        },
        "eo:cloud_cover": {
            "title": "Eo:Cloud Cover",
            "type": "number",
            "minimum": 5.0,
            "maximum": 15.0
        }
    }
}
```

The Item that fulfills and Order placed on this Opportunity might be like:

```json
{
  "type": "Feature",
  ...
  "properties": {
    "datetime": "2024-01-01T00:00:00Z",
    "sensor_type": "2",
    "craft_id": "7",
    "view:sun_elevation": 30.0,
    "view:azimuth": 105.0,
    "view:off_nadir": 9.0,
    "eo:cloud_cover": 10.0
  }
}
```
