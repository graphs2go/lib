from uuid import uuid4

from graphs2go.models import rdf


def uuid_urn() -> rdf.Iri:
    """
    Generate a UUID URN (https://datatracker.ietf.org/doc/html/rfc4122).
    """
    return rdf.Iri(f"urn:uuid:{uuid4()}")
