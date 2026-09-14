"""
postop.adapters: provider-neutral, illustrative adapters built on top of
core PosTop (postop.core, postop.formal, postop.certificates).

Nothing under postop.adapters is imported by postop.core, postop.formal,
or postop.certificates -- the dependency only goes one way. Adapters may
be removed or changed more freely than the core package.
"""

from .guardrail import ClaimNormalizer, GuardrailResult, PosTopGuardrail

__all__ = ["ClaimNormalizer", "GuardrailResult", "PosTopGuardrail"]
