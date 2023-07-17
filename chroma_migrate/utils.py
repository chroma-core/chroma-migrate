from collections.abc import MutableMapping
from typing import Any, Dict

def validate_collection_metadata(metadata: Dict[Any, Any]):
    if metadata is None:
        return
    # The new version of chroma only supports flat metadata. So we validate
    # that the metadata is is a flat dictionary of strings to ints, floats, or strings.
    for key, value in metadata.items():
        if not isinstance(value, (int, float, str, type(None))):
            raise ValueError(f"Metadata value {value} is not an int, float, or string. The new version of chroma only supports flat metadata. Please flatten your metadata using collection.modify() and try again.")