import logging
import os
from collections.abc import Callable, Iterable
from multiprocessing import JoinableQueue, Queue, Process
from typing import TypeVar

from dagster import get_dagster_logger
from rdflib import URIRef
from tqdm import tqdm

from graphs2go.models import interchange
from graphs2go.namespaces.interchange import INTERCHANGE

_INPUT_BATCH_SIZE = 100
_OutputModelT = TypeVar("_OutputModelT")
_TransformInterchangeNode = Callable[[interchange.Node], Iterable[_OutputModelT]]


def _consumer(
    interchange_graph_descriptor: interchange.Graph.Descriptor,
    output_queue: Queue,
    transform_interchange_node: _TransformInterchangeNode,
    work_queue: JoinableQueue,
) -> None:
    with interchange.Graph.open(
        interchange_graph_descriptor, read_only=True
    ) as interchange_graph:
        while True:
            interchange_node_uris: tuple[URIRef, ...] | None = work_queue.get()

            if interchange_node_uris is None:
                work_queue.task_done()
                break  # Signal from the producer there's no more work

            outputs: list[_OutputModelT] = []
            for interchange_node_uri in interchange_node_uris:
                interchange_node = interchange_graph.node_by_uri(interchange_node_uri)
                outputs.extend(transform_interchange_node(interchange_node))
            output_queue.put(tuple(outputs))
            work_queue.task_done()

    output_queue.put(None)  # Signal this consumer is done


def _producer(
    consumer_count: int,
    interchange_graph_descriptor: interchange.Graph.Descriptor,
    interchange_node_rdf_type: URIRef,
    work_queue: JoinableQueue,
) -> None:
    interchange_node_uris_batch: list[URIRef] = []
    with interchange.Graph.open(
        interchange_graph_descriptor, read_only=True
    ) as interchange_graph:
        for interchange_node_uri in interchange_graph.node_uris(
            rdf_type=interchange_node_rdf_type
        ):
            interchange_node_uris_batch.append(interchange_node_uri)
            if len(interchange_node_uris_batch) == _INPUT_BATCH_SIZE:
                work_queue.put(tuple(interchange_node_uris_batch))
                interchange_node_uris_batch = []

    if interchange_node_uris_batch:
        work_queue.put(tuple(interchange_node_uris_batch))

    for _ in range(consumer_count):
        work_queue.put(None)  # Signal to the consumers there's no more work

    work_queue.join()


def transform_interchange_graph(
    *,
    interchange_graph_descriptor: interchange.Graph.Descriptor,
    transform_interchange_node: _TransformInterchangeNode,
    interchange_node_rdf_type: URIRef = INTERCHANGE.Node,
    in_process: bool = False
) -> Iterable[_OutputModelT]:
    logger = get_dagster_logger()

    with tqdm(desc="output models", position=0) as output_model_tqdm:
        if in_process:
            with interchange.Graph.open(
                interchange_graph_descriptor, read_only=True
            ) as interchange_graph:
                for interchange_node in tqdm(
                    interchange_graph.nodes(rdf_type=interchange_node_rdf_type),
                    desc="transformed interchange nodes",
                    position=1,
                ):
                    for output_model in transform_interchange_node(interchange_node):
                        output_model_tqdm.update(1)
                        yield output_model
            return

        output_queue = Queue()
        work_queue = JoinableQueue()

        consumer_count = 1  # os.cpu_count()
        logger.info(
            "starting %d interchange graph transformation consumer processes",
            consumer_count,
        )
        consumer_processes = tuple(
            Process(
                target=_consumer,
                args=(
                    interchange_graph_descriptor,
                    output_queue,
                    transform_interchange_node,
                    work_queue,
                ),
            )
            for _ in range(consumer_count)
        )
        for consumer_process in consumer_processes:
            consumer_process.start()
        logger.info(
            "started %d interchange graph transformation consumer processes",
            consumer_count,
        )

        logger.info("starting interchange graph transformation producer process")
        producer_process = Process(
            target=_producer,
            args=(
                consumer_count,
                interchange_graph_descriptor,
                interchange_node_rdf_type,
                work_queue,
            ),
        )
        producer_process.start()
        logger.info("started interchange graph transformation producer process")

        exited_consumer_count = 0
        while True:
            output_model_batch: tuple[_OutputModelT] | None = output_queue.get()
            if output_model_batch is None:
                exited_consumer_count += 1
                logger.info(
                    "%d interchange graph transformation consumers exited",
                    exited_consumer_count,
                )
                if exited_consumer_count == consumer_count:
                    break

            output_model_tqdm.update(len(output_model_batch))
            yield from output_model_batch

        producer_process.join()
        for consumer_process in consumer_processes:
            consumer_process.join()
