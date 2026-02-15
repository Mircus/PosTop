"""
Operator helpers and lightweight tracing utilities for PosTop.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Generic, Iterable, Iterator, Set, Tuple, TypeVar

from .core import PosTop

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
    Convenience wrapper re-exporting Ext/Int/Hit/Sel/J with optional tracing.
    """

    def __init__(self, pt: PosTop[X, S]):
        self.pt = pt

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
        result = self.pt.Ext(U_set)
        if trace:
            output, info = self._maybe_trace("Ext", {"U": U_set}, result, trace=True)
            return output, info  # type: ignore[return-value]
        return result

    def Int(
        self, A: Iterable[X], trace: bool = False
    ) -> Set[S] | Tuple[Set[S], OperatorTrace[X, S]]:
        A_set = set(A)
        result = self.pt.Int(A_set)
        if trace:
            output, info = self._maybe_trace("Int", {"A": A_set}, result, trace=True)
            return output, info  # type: ignore[return-value]
        return result

    def hit(
        self, C: Iterable[X], trace: bool = False
    ) -> Set[S] | Tuple[Set[S], OperatorTrace[X, S]]:
        C_set = set(C)
        result = self.pt.Hit(C_set)
        if trace:
            output, info = self._maybe_trace("Hit", {"C": C_set}, result, trace=True)
            return output, info  # type: ignore[return-value]
        return result

    def sel(
        self, U: Iterable[S], trace: bool = False
    ) -> Set[X] | Tuple[Set[X], OperatorTrace[X, S]]:
        U_set = set(U)
        result = self.pt.Sel(U_set)
        if trace:
            output, info = self._maybe_trace("Sel", {"U": U_set}, result, trace=True)
            return output, info  # type: ignore[return-value]
        return result

    def j(
        self, U: Iterable[S], trace: bool = False
    ) -> Set[S] | Tuple[Set[S], OperatorTrace[X, S]]:
        U_set = set(U)
        result = self.pt.J(U_set)
        if trace:
            output, info = self._maybe_trace("J", {"U": U_set}, result, trace=True)
            return output, info  # type: ignore[return-value]
        return result

    def explain_chain(self, observable: S, cover: Iterable[S]) -> Iterator[str]:
        """
        Yield a textual explanation for `observable ◁ cover`.
        """
        cover_set = set(cover)
        explanation = self.pt.explain_cover(observable, cover_set)
        if explanation["holds"]:
            yield f"Cover holds: every witness of '{observable}' hits {cover_set}."
            witnesses: Dict[X, Set[S]] = explanation["witnesses"]
            for point, hits in witnesses.items():
                yield f"- {point} witnesses via {sorted(hits)}"
        else:
            missing = explanation["counterexample"]
            yield f"Cover fails: '{missing}' forces '{observable}' but misses {cover_set}."
