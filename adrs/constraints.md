# Constraints and Opportunity Properties

Previously, the Constraints and Opportunity Properties were the same concept/representation. However, these represent distinct but related attributes. Constraints represents the terms that can be used in the filter sent to the Opportunities Search and Order Create endpoints. These are frequently the same or related values that will be part of the STAC Items that are used to fulfill an eventual Order. Opportunity Properties represent the expected range of values that these STAC Items are expected to have.

For example, for the concept of "off_nadir":

The Constraint will be a term "off_nadir" that can be a value 0 to 45.
This is used in a CQL2 filter to the Opportunities Search endpoint to restrict the allowable values from 0 to 15
The Opportunity that is returned from Search has an Opportunity Property "off_nadir" with a description that the value of this field in the resulting STAC Items will be between 4 and 8, which falls within the filter restriction of 0-15.
An Order is created with the original filter and other fields.
The Order is fulfilled with a STAC Item that has an off_nadir value of 4.8.
