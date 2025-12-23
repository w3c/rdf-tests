# /// script
# dependencies = [
#   "pyshacl~=0.30.0",
# ]
# ///
"""
Small Python script to validate manifest files
"""

import os
from pathlib import Path
from pyshacl import validate

repository_root = Path(__file__).parent.parent
shape_path = repository_root / "shapes" / "manifest.ttl"
vocab_path = repository_root / "ns" / "rdftest.ttl"


def log_line(message: str, level: str, file: Path | None = None) -> None:
    if "GITHUB_ACTIONS" in os.environ:
        print(
            f"::{level}{f' file={file.relative_to(repository_root)}' if file else ''}::{message}"
        )
    else:
        print(message)


failure_counter = 0
total_counter = 0
for manifest_path in repository_root.rglob("manifest*.ttl"):
    try:
        (conforms, _, results_text) = validate(
            str(manifest_path),
            shacl_graph=str(shape_path),
            ont_graph=str(vocab_path),
            inference="rdfs",
        )
    except SyntaxError as e:
        conforms = False
        results_text = str(e)
    if not conforms:
        log_line(
            f"Error in {manifest_path.relative_to(repository_root)}: {results_text}",
            "error",
            manifest_path,
        )
        failure_counter += 1
    total_counter += 1

log_line(
    f"Found {failure_counter} files with error"
    if failure_counter > 0
    else f"Validated {total_counter} files without errors",
    "notice",
)
exit(int(failure_counter > 0))
