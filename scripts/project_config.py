"""Project-wide constants used by the reproducible pipeline."""

SOURCE_DOWNLOAD_DATE = "2026-09-08"

ICCU_SNAPSHOT_DATE = "2026-09-08"
ICCU_SNAPSHOT_DATETIME = "2026-09-08T14:11:15"

POSAS_2019_DATE = "2019-01-01"
POSAS_2025_DATE = "2025-01-01"

# Change this only when producing a new project release.
PROJECT_RELEASE_DATE = "2026-09-11"

# Public Web namespace used by the Linked Open Data publication.
PUBLIC_BASE = "https://ameliamorsellino.github.io/biblioteche-fantasma/"

# Public GitHub repository.
GITHUB_REPO = "https://github.com/ameliamorsellino/biblioteche-fantasma"

# The complete RDF knowledge graph is too large for the normal Git repository
# and will be distributed as a GitHub Release asset.
RDF_DATA_DOWNLOAD_URL = (
    "https://github.com/ameliamorsellino/"
    "biblioteche-fantasma/releases/latest/download/data.ttl"
)