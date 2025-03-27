from pathlib import Path

from graphs2go.loaders.cypher_directory_loader import CypherDirectoryLoader
from graphs2go.models import cypher


def test_load(
    tmp_path: Path,
) -> None:
    with CypherDirectoryLoader(directory_path=tmp_path) as loader:
        loader.load(cypher.CreateNodeStatement("testnode1"))
        loader.load(cypher.CreateNodeStatement("testnode2"))
        loader.load(cypher.CreateRelationshipStatement("testrel1"))
        loader.load(cypher.CreateRelationshipStatement("testrel2"))

    with Path.open(tmp_path / "create_node.cypher") as file_:
        assert file_.read().strip() == "testnode1\n\ntestnode2"

    with Path.open(tmp_path / "create_relationship.cypher") as file_:
        assert file_.read().strip() == "testrel1\n\ntestrel2"
