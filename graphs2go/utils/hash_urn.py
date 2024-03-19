import hashlib

from rdflib import URIRef


def hash_urn(*args: str, hash_scheme: str = "sha256") -> URIRef:
    hash_ = getattr(hashlib, hash_scheme)()
    for arg in args:
        hash_.update(arg.encode("utf-8"))
    return URIRef(f"urn:hash::{hash_scheme}:{hash_.hexdigest()}")
