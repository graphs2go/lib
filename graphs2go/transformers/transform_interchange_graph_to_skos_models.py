from collections.abc import Iterable
from graphs2go.models import interchange, skos


def transform_interchange_graph_to_skos_models(
    interchange_graph: interchange.Graph,
) -> Iterable[skos.Model]:
    for interchange_concept in interchange_graph.concepts:
        skos_concept_builder = skos.Concept.builder(uri=interchange_concept.uri).build()

        for label in interchange_concept.