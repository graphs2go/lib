from rdflib import URIRef
from rdflib.resource import Resource


class Model:
    def __init__(self, *, resource: Resource):
        if not isinstance(resource.identifier, URIRef):
            raise ValueError("model resource must be named")  # noqa: TRY004
        self.__resource = resource

    @property
    def resource(self) -> Resource:
        return self.__resource

    @property
    def uri(self) -> URIRef:
        return self.__resource.identifier
