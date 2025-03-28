from graphs2go.namespaces import RDF, SKOS
from graphs2go.stores.interchange import ModelStore as InterchangeModelStore
from graphs2go.stores.rdf import ModelStore as RdfModelStore
from graphs2go.stores.rdf import QuadStore
from graphs2go.transformers.transform_interchange_models_to_direct_rdf_models import (
    transform_interchange_models_to_direct_rdf_models,
)


def test_transform(
    interchange_model_store_descriptor: InterchangeModelStore.Descriptor,
    quad_store: QuadStore,
) -> None:
    with RdfModelStore(quad_store=quad_store) as rdf_model_store:
        rdf_model_store.extend(
            transform_interchange_models_to_direct_rdf_models(
                interchange_model_store_descriptor, in_process=True
            )
        )

        assert (
            rdf_model_store.quad_store.count_matches(
                predicate=RDF.type, object_=SKOS.ConceptScheme
            )
            == 1
        )
        assert (
            rdf_model_store.quad_store.count_matches(
                predicate=RDF.type, object_=SKOS.Concept
            )
            == 2
        )
