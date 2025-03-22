import pyoxigraph as ox

from graphs2go.models.rdf.quad import (
    Quad,
    Quad_Graph,
    Quad_Object,
    Quad_Predicate,
    Quad_Subject,
)
from graphs2go.models.rdf.blank_node import BlankNode
from graphs2go.models.rdf.iri import Iri
from graphs2go.models.rdf.literal import Literal


class OxigraphAdapters:
    class Literal:
        @staticmethod
        def from_ox(literal: ox.Literal) -> Literal:
            if literal.language:
                return Literal(literal.value, lang=literal.language)
            return Literal(literal.value, datatype=Literal(literal.datatype.value))

        @staticmethod
        def to_ox(literal: Literal) -> ox.Literal:
            return ox.Literal(
                literal,
                language=literal.language,
                datatype=ox.NamedNode(literal.datatype) if literal.datatype else None,
            )

    class Quad:
        class Graph:
            @staticmethod
            def from_ox(
                graph: ox.BlankNode | ox.DefaultGraph | ox.NamedNode,
            ) -> Quad_Graph:
                if isinstance(graph, ox.BlankNode):
                    return BlankNode(graph.value)
                if isinstance(graph, ox.DefaultGraph):
                    return None
                if isinstance(graph, ox.NamedNode):
                    return Iri(graph.value)
                raise TypeError(type(graph))

            @staticmethod
            def to_ox(
                graph: Quad_Graph,
            ) -> ox.BlankNode | ox.DefaultGraph | ox.NamedNode:
                if graph is None:
                    return ox.DefaultGraph()
                if isinstance(graph, BlankNode):
                    return ox.BlankNode(graph)
                if isinstance(graph, Iri):
                    return ox.NamedNode(graph)
                raise TypeError(type(graph))

        class Object:
            @staticmethod
            def from_ox(
                object_: ox.BlankNode | ox.Literal | ox.NamedNode | ox.Triple,
            ) -> Quad_Object:
                if isinstance(object_, ox.BlankNode):
                    return BlankNode(object_.value)
                if isinstance(object_, ox.Literal):
                    return OxigraphAdapters.Literal.from_ox(object_)
                if isinstance(object_, ox.NamedNode):
                    return Iri(object_.value)
                raise TypeError(type(object_))

            @staticmethod
            def to_ox(
                object_: Quad_Object,
            ) -> ox.BlankNode | ox.Literal | ox.NamedNode:
                if isinstance(object_, BlankNode):
                    return ox.BlankNode(object_)
                if isinstance(object_, Literal):
                    return OxigraphAdapters.Literal.to_ox(object_)
                if isinstance(object_, Iri):
                    return ox.NamedNode(object_)
                raise TypeError(type(object_))

        class Predicate:
            @staticmethod
            def from_ox(predicate: ox.NamedNode) -> Iri:
                return Iri(predicate.value)

            @staticmethod
            def to_ox(predicate: Quad_Predicate) -> ox.NamedNode:
                return ox.NamedNode(predicate)

        class Subject:
            @staticmethod
            def from_ox(
                subject: ox.BlankNode | ox.NamedNode | ox.Triple,
            ) -> Quad_Subject:
                if isinstance(subject, ox.BlankNode):
                    return BlankNode(subject.value)
                if isinstance(subject, ox.NamedNode):
                    return Iri(subject.value)
                raise TypeError(type(subject))

            @staticmethod
            def to_ox(subject: Quad_Subject) -> ox.BlankNode | ox.NamedNode:
                if isinstance(subject, BlankNode):
                    return ox.BlankNode(subject)
                if isinstance(subject, Iri):
                    return ox.NamedNode(subject)
                raise TypeError(type(subject))

        @staticmethod
        def from_ox(quad: ox.Quad) -> Quad:
            return Quad(
                OxigraphAdapters.Quad.Subject.from_ox(quad.subject),
                OxigraphAdapters.Quad.Predicate.from_ox(quad.predicate),
                OxigraphAdapters.Quad.Object.from_ox(quad.object),
                OxigraphAdapters.Quad.Graph.from_ox(quad.graph_name),
            )

        @staticmethod
        def to_ox(quad: Quad) -> ox.Quad:
            return ox.Quad(
                OxigraphAdapters.Quad.Subject.to_ox(quad.subject),
                OxigraphAdapters.Quad.Predicate.to_ox(quad.predicate),
                OxigraphAdapters.Quad.Object.to_ox(quad.object_),
                OxigraphAdapters.Quad.Graph.to_ox(quad.graph),
            )
