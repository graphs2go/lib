from rdflib import RDF, Graph, URIRef
from rdflib.resource import Resource


class Model:
    def __init__(self, *, resource: Resource):
        if not isinstance(resource.identifier, URIRef):
            raise ValueError("model resource must be named")  # noqa: TRY004
        self.__resource = resource

    @staticmethod
    def _create_resource(*, type_: URIRef, uri: URIRef) -> Resource:
        resource = Graph().resource(uri)
        resource.add(RDF.type, type_)
        return resource

    @property
    def resource(self) -> Resource:
        return self.__resource

    @property
    def uri(self) -> URIRef:
        return self.__resource.identifier
