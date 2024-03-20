from dataclasses import dataclass
from graphs2go.rdf_stores.rdf_store import RdfStore
from rdflib.plugins.stores.memory import Memory
from rdflib.store import Store


class MemoryRdfStore(RdfStore):
    @dataclass(frozen=True)
    class Descriptor(RdfStore.Descriptor):
        pass

    __descriptor = Descriptor()

    def __init__(self):
        RdfStore.__init__(self)
        self.__rdflib_store = Memory()

    def close(self) -> None:
        pass

    @property
    def descriptor(self) -> Descriptor:
        return self.__descriptor

    @property
    def rdflib_store(self) -> Store:
        return self.__rdflib_store
