"""
Deprecated location. The LLM-guardrail adapter moved to
postop.adapters.guardrail -- core PosTop should have no LLM-shaped
module at its top level. Import from postop (still re-exported) or
postop.adapters instead.
"""

from __future__ import annotations

import warnings

from .adapters.guardrail import ClaimNormalizer, GuardrailResult, PosTopGuardrail

warnings.warn(
    "postop.llm is deprecated; import from postop.adapters.guardrail "
    "(or from postop, which still re-exports these names) instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ClaimNormalizer", "GuardrailResult", "PosTopGuardrail"]
