from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class VAEM(DefinedNamespace):
    _NS = Namespace("http://www.linkedmodel.org/schema/vaem#")
    _SCHEMA = Namespace("http://www.linkedmodel.org/2.0/schema/vaem")

    _fail = True

    BridgeGraph: URIRef  # Bridge graph
    CodelistGraph: URIRef  # A graph that holds enumerations that are codelists
    ConnectSetGraph: URIRef  # A graph that specifies mapings between external data sources and a neutral model
    CollectionGraph: URIRef  # Collection graph
    ControllersGraph: (
        URIRef  # A graph that configures as a controller in a data mesh control plane
    )
    CurationGraph: URIRef  # A curation graph is one whose purpose is to hold metadata that is needed to describe, govern and provision another graph. A curation graph will likely use VOAG and VAEM for this purpose
    DataGraph: URIRef  #
    FunctionsGraph: URIRef  #
    GraphRole: URIRef  # GraphRole is used to characterize how a graph of resources participates in an ontology set
    GraphMetaData: (
        URIRef  # Defines basic metadata for the registration and publishing of a graph
    )
    LicenseModel: URIRef
    MappingGraph: URIRef  # A graph that specifies a transformation of a graph into another graph or graphs. Invariably this is a SPINMap graph using SPARQL Rules (SPIN) to express the transforms
    ProxyGraph: URIRef  #
    RulesGraph: URIRef  #
    SchemaGraph: URIRef  #
    ScriptGraph: URIRef  #
    TransformsGraph: URIRef  #
    ViewGraph: URIRef  #
    VocabularyGraph: URIRef  #
    curationGraph: URIRef  #  Used to link to the graph (or graphs) being curated
    effectiveStartDate: URIRef  # The date when the item becomes valid.
    effectiveEndDate: URIRef
    filePrefix: URIRef  #  For specifying a preferred file prefix for a graph. For example a schema graph may be given the file prefix "SCHEMA" followed by an underscore
    graphName: URIRef  #
    graphTitle: URIRef  #
    hasCatalogEntry: URIRef
    hasGraphRole: (
        URIRef  # used to characterize the role a graph plays in an ontology set.
    )
    hasLicenseType: URIRef
    isElaboratedIn: URIRef  # An annotation used to reference a graph that elaborates (adds properties and axioms to) a resource
    lastUpdated: URIRef  #  Intended for general use as the name implies
    namespace: URIRef  #  Provides a means to specify the ontology URI with which a graph is primarily associated
    namespacePrefix: URIRef  #  Specifies a short handle or label for the URI of an Ontology.  Multiple graphs can define statements for resources in the same Ontology namespace
    normativeReference: URIRef
    ownedBy: URIRef  #  A general property that in some cases could have scalar values or may refer to some concept of "Party"
    owner: URIRef  #
    owningParty: URIRef  # Used to refer to some concept of "Party" and is a sub-property of "vaem:ownedBy"
    rationale: URIRef  #  A justification for some other assertion or value
    reifiableBy: URIRef  # To express how statements in a model can be reifiable, this property is used to explicitly associate a property with a user-defined sub-class of "rdf:Statement"
    releaseDate: URIRef  #  Intended for general use as the name implies
    revision: URIRef  #  Intended for general use as the name implies. " ;
    specificity: URIRef  #  Intended to specify the level of detail of an ontology
    todo: URIRef  #  A way to attach an annotation about a "todo" task
    turtleFileURL: (
        URIRef  #  Used to provide a link to the location of the ontology's turtle file
    )
    url: URIRef  #  Intended for general use as the name implies.  The range of the property is set as an XSD URI.
    urlForHTML: URIRef  # Provides a link to the location of the ontology's HTML file
    usesNonImportedResource: URIRef  # Used to express dependencies on resources from graphs that are not imported.
    withAttributionTo: URIRef  #
    website: URIRef  #  Provides a link to a party's website, where a party is typically an organization
