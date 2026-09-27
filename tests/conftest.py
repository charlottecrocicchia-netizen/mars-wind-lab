"""External scientific tools are never exercised without owner authorization."""
import pytest
from marswind.mcd import ROOT
from marswind.source_policy import require_mcd_authorization


@pytest.fixture(autouse=True)
def authorized_external_inputs(request):
    if request.node.get_closest_marker('integration'):
        try:
            require_mcd_authorization(ROOT)
        except RuntimeError as exc:
            pytest.skip(str(exc))
