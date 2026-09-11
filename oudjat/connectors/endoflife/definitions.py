"""
A module that centralize package variables.
"""

from oudjat.utils import FileUtils

EOL_API_URL = "https://endoflife.date/api/v1/"
EOL_CACHE_PATH  = FileUtils.project_root() / ".cache" / "software"
