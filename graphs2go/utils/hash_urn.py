import hashlib

from graphs2go.models import rdf


def hash_urn(*args: str, hash_scheme: str = "sha256") -> rdf.Iri:
    hash_ = getattr(hashlib, hash_scheme)()
    for arg in args:
        hash_.update(arg.encode("utf-8"))
    return rdf.Iri(f"urn:hash::{hash_scheme}:{hash_.hexdigest()}")
