"""
Operator helpers and lightweight tracing utilities for PosTop.

Canonical operator names (matching the paper): ext, box, diamond, rest,
reduction. The old Ext/Int/Hit/Sel/J-flavored method names are kept as
deprecated aliases on OperatorSuite for backward compatibility.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Dict, Generic, Iterable, Iterator, Set, Tuple, TypeVar

from .core import IncidenceSystem

X = TypeVar("X")
S = TypeVar("S")


@dataclass(frozen=True)
class OperatorTrace(Generic[X, S]):
    """One-line summary of an operator invocation."""

    operator: str
    inputs: Dict[str, Set[S] | Set[X]]
    output: Set[X] | Set[S]

    def __str__(self) -> str:  # pragma: no cover - repr sugar
        return f"{self.operator}({self.inputs}) -> {self.output}"


class OperatorSuite(Generic[X, S]):
    """
    Convenience wrapper re-exporting ext/box/diamond/rest/reduction with
    optional tracing.
    """

    def __init__(self, system: IncidenceSystem[X, S]):
        self.system = system

    def _maybe_trace(
        self,
        operator: str,
        inputs: Dict[str, Set[S] | Set[X]],
        output: Set[X] | Set[S],
        trace: bool,
    ) -> Tuple[Set[X] | Set[S], OperatorTrace[X, S] | None]:
        info = OperatorTrace(operator=operator, inputs=inputs, output=output)
        return output, info if trace else None

    def ext(
        self, U: Iterable[S], trace: bool = False
    ) -> Set[X] | Tuple[Set[X], OperatorTrace[X, S]]:
        U_set = set(U)
        result = self.system.ext(U_set)
        if trace:
            output, info = self._maybe_trace("ext", {"U": U_set}, result, trace=True)
            return output, info  # type: ignore[return-value]
        return result

    def box(
        self, E: Iterable[X], trace: bool = False
    ) -> Set[S] | Tuple[Set[S], OperatorTrace[X, S]]:
        E_set = set(E)
        result = self.system.box(E_set)
        if trace:
            output, info = self._maybe_trace("box", {"E": E_set}, result, trace=True)
            return output, info  # type: ignore[return-value]
        return result

    def diamond(
        self, D: Iterable[X], trace: bool = False
    ) -> Set[S] | Tuple[Set[S], OperatorTrace[X, S]]:
        D_set = set(D)
        result = self.system.diamond(D_set)
        if trace:
            output, info = self._maybe_trace("diamond", {"D": D_set}, result, trace=True)
            return output, info  # type: ignore[return-value]
        return result

    def rest(
        self, U: Iterable[S], trace: bool = False
    ) -> Set[X] | Tuple[Set[X], OperatorTrace[X, S]]:
        U_set = set(U)
        result = self.system.rest(U_set)
        if trace:
            output, info = self._maybe_trace("rest", {"U": U_set}, result, trace=True)
            return output, info  # type: ignore[return-value]
        return result

    def reduction(
        self, U: Iterable[S], trace: bool = False
    ) -> Set[S] | Tuple[Set[S], OperatorTrace[X, S]]:
        U_set = set(U)
        result = self.system.reduction(U_set)
        if trace:
            output, info = self._maybe_trace("reduction", {"U": U_set}, result, trace=True)
            return output, info  # type: ignore[return-value]
        return result

    def explain_chain(self, observable: S, cover: Iterable[S]) -> Iterator[str]:
        """
        Yield a textual explanation for `observable ◁ cover`.
        """
        cover_set = set(cover)
        cert = self.system.explain_cover(observable, cover_set)
        if cert.holds:
            yield f"Cover holds: every witness of '{observable}' hits {cover_set}."
            for point, hits in cert.witnesses.items():
                yield f"- {point} witnesses via {sorted(hits)}"
        else:
            yield f"Cover fails: '{cert.counterexample}' forces '{observable}' but misses {cover_set}."

    # ---- Deprecated aliases (pre-canonical-rename names) ----

    def Int(self, A: Iterable[X], trace: bool = False):
        warnings.warn(
            "OperatorSuite.Int is deprecated; use .box instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.box(A, trace=trace)

    def hit(self, C: Iterable[X], trace: bool = False):
        warnings.warn(
            "OperatorSuite.hit is deprecated; use .diamond instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.diamond(C, trace=trace)

    def sel(self, U: Iterable[S], trace: bool = False):
        warnings.warn(
            "OperatorSuite.sel is deprecated; use .rest instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.rest(U, trace=trace)

    def j(self, U: Iterable[S], trace: bool = False):
        warnings.warn(
            "OperatorSuite.j is deprecated; use .reduction instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.reduction(U, trace=trace)
