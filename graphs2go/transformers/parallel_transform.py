import os
from collections.abc import Callable, Iterable
from multiprocessing import JoinableQueue, Process, Queue
from typing import TypeVar

from dagster import get_dagster_logger

_ConsumerInputT = TypeVar("_ConsumerInputT")
_OutputT = TypeVar("_OutputT")
_OutputQueue = Queue
_ProducerInputT = TypeVar("_ProducerInputT")
_WorkQueue = JoinableQueue

_Consumer = Callable[[_ConsumerInputT, _OutputQueue, _WorkQueue], None]
_Producer = Callable[[_ProducerInputT, _WorkQueue], None]


def _consumer_wrapper(
    consumer: _Consumer,
    input_: _ConsumerInputT,
    output_queue: _OutputQueue,
    work_queue: _WorkQueue,
) -> None:
    consumer(input_, output_queue, work_queue)

    output_queue.put(None)  # Signal this consumer is done


def _producer_wrapper(
    consumer_count: int,
    input_: _ProducerInputT,
    producer: _Producer,
    work_queue: _WorkQueue,
) -> None:
    producer(input_, work_queue)

    for _ in range(consumer_count):
        work_queue.put(None)  # Signal to the consumers there's no more work

    work_queue.join()


def parallel_transform(
    *,
    consumer: _Consumer,
    consumer_input: _ConsumerInputT,
    producer: _Producer,
    producer_input: _ProducerInputT,
    consumer_count: int | None = None,
) -> Iterable[_OutputT]:
    """
    Generic function for performing parallel transformation of an input to zero or more outputs.
    """

    if consumer_count is None:
        consumer_count = os.cpu_count()
        if consumer_count is None or consumer_count > 4:
            consumer_count = 4

    logger = get_dagster_logger()
    output_queue: _OutputQueue = Queue()
    work_queue: _WorkQueue = JoinableQueue()

    logger.info(
        "starting %d transformation consumer processes",
        consumer_count,
    )
    consumer_processes = tuple(
        Process(
            target=_consumer_wrapper,
            args=(
                consumer,
                consumer_input,
                output_queue,
                work_queue,
            ),
        )
        for _ in range(consumer_count)
    )
    for consumer_process in consumer_processes:
        consumer_process.start()
    logger.info(
        "started %d transformation consumer processes",
        consumer_count,
    )

    logger.info("starting transformation producer process")
    producer_process = Process(
        target=_producer_wrapper,
        args=(
            consumer_count,
            producer_input,
            producer,
            work_queue,
        ),
    )
    producer_process.start()
    logger.info("started transformation producer process")

    exited_consumer_count = 0
    while True:
        output_model_batch: tuple[_OutputT] | None = output_queue.get()

        if output_model_batch is None:
            exited_consumer_count += 1
            logger.info(
                "%d transformation consumers exited",
                exited_consumer_count,
            )
            if exited_consumer_count == consumer_count:
                break
            continue

        yield from output_model_batch

    producer_process.join()
    for consumer_process in consumer_processes:
        consumer_process.join()
