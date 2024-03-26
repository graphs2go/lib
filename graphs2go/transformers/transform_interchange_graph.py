from collections.abc import Callable, Iterable
from multiprocessing import JoinableQueue, Queue
from typing import TypeVar

from rdflib import URIRef

from graphs2go.models import interchange
from graphs2go.namespaces.interchange import INTERCHANGE
from graphs2go.transformers.parallel_transform import parallel_transform

_INTERCHANGE_NODE_BATCH_SIZE = 100
_OutputT = TypeVar("_OutputT")
_TransformInterchangeNode = Callable[[interchange.Node], Iterable[_OutputT]]
_ConsumerInputT = tuple[interchange.Graph.Descriptor, _TransformInterchangeNode]
_ProducerInputT = tuple[interchange.Graph.Descriptor, URIRef]


def _consumer(
    input_: _ConsumerInputT,
    output_queue: Queue,
    work_queue: JoinableQueue,
) -> None:
    (interchange_graph_descriptor, transform_interchange_node) = input_

    with interchange.Graph.open(
        interchange_graph_descriptor, read_only=True
    ) as interchange_graph:
        while True:
            interchange_node_uris: tuple[URIRef, ...] | None = work_queue.get()

            if interchange_node_uris is None:
                work_queue.task_done()
                break  # Signal from the producer there's no more work

            outputs: list[_OutputT] = []  # type: ignore
            for interchange_node_uri in interchange_node_uris:
                interchange_node = interchange_graph.node_by_uri(interchange_node_uri)
                outputs.extend(transform_interchange_node(interchange_node))
            output_queue.put(tuple(outputs))
            work_queue.task_done()


def _producer(
    input_: _ProducerInputT,
    work_queue: JoinableQueue,
) -> None:
    interchange_graph_descriptor, interchange_node_rdf_type = input_

    interchange_node_uris_batch: list[URIRef] = []
    with interchange.Graph.open(
        interchange_graph_descriptor, read_only=True
    ) as interchange_graph:
        for interchange_node_uri in interchange_graph.node_uris(
            rdf_type=interchange_node_rdf_type
        ):
            interchange_node_uris_batch.append(interchange_node_uri)
            if len(interchange_node_uris_batch) == _INTERCHANGE_NODE_BATCH_SIZE:
                work_queue.put(tuple(interchange_node_uris_batch))
                interchange_node_uris_batch = []

    if interchange_node_uris_batch:
        work_queue.put(tuple(interchange_node_uris_batch))


def transform_interchange_graph(
    *,
    interchange_graph_descriptor: interchange.Graph.Descriptor,
    transform_interchange_node: _TransformInterchangeNode,
    interchange_node_rdf_type: URIRef = INTERCHANGE.Node,
    in_process: bool = False
) -> Iterable[_OutputT]:
    if in_process:
        with interchange.Graph.open(
            interchange_graph_descriptor, read_only=True
        ) as interchange_graph:
            for interchange_node in interchange_graph.nodes(
                rdf_type=interchange_node_rdf_type
            ):
                yield from transform_interchange_node(interchange_node)
        return

    yield from parallel_transform(
        consumer=_consumer,
        consumer_input=(
            interchange_graph_descriptor,
            transform_interchange_node,
        ),
        producer=_producer,
        producer_input=(
            interchange_graph_descriptor,
            interchange_node_rdf_type,
        ),
    )
