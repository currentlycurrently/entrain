"""
Dimension analyzers for the Entrain Framework.

Each dimension has a dedicated analyzer that implements specific
measurement methodologies grounded in published research.
"""

from entrain.dimensions.base import DimensionAnalyzer
from entrain.dimensions.sycophantic_reinforcement import SRAnalyzer
from entrain.dimensions.linguistic_convergence import LCAnalyzer
from entrain.dimensions.autonomy_erosion import AEAnalyzer
from entrain.dimensions.reality_coherence import RCDAnalyzer
from entrain.dimensions.dependency_formation import DFAnalyzer

# PE analyzer is optional (requires audio dependencies)
try:
    from entrain.dimensions.prosodic_entrainment import PEAnalyzer
    _has_pe = True
except ImportError:
    _has_pe = False

__all__ = [
    "DimensionAnalyzer",
    "SRAnalyzer",
    "LCAnalyzer",
    "AEAnalyzer",
    "RCDAnalyzer",
    "DFAnalyzer",
]

if _has_pe:
    __all__.append("PEAnalyzer")
