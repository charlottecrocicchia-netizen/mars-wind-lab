"""Check explicit source-use decisions before loading external software or data."""
import json
from pathlib import Path


def require_mcd_authorization(root):
    path = Path(root) / 'local_settings.json'
    settings = json.loads(path.read_text()) if path.exists() else {}
    if settings.get('MCD_AUTHORIZED') is not True:
        raise RuntimeError(
            'MCD software use is awaiting authorization. Use an installation obtained '
            'with the producers’ permission, then record MCD_AUTHORIZED=true in '
            'local_settings.json. Previously extracted research products remain available.'
        )


def require_source_permission(source):
    if source.get('reuse_approved') is not True:
        raise RuntimeError(
            f"Source {source['id']} is excluded from new acquisition: "
            + source.get('permission_note', 'reuse permission has not been established.')
        )
