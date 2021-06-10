from __future__ import annotations
import typing

from .alphabet import Alphabet
from .subseq import SubSeq

S = typing.TypeVar('S', bound="String")


class String(SubSeq[int]):
    alpha: Alphabet

    def __init__(self,
                 x: str,
                 alpha: typing.Optional[Alphabet] = None,
                 add_sentinel: bool = True
                 ) -> None:

        # Handle the alphabet
        self.alpha = alpha or Alphabet(x)

        # Generate the underlying bytes.
        underlying = self.alpha.map(x)
        if add_sentinel:
            underlying.append(0)  # add sentinel

        # Use the underlying bytes as a Sequence[int]
        # that we hold as a subseq[int].
        super().__init__(underlying)

    def __str__(self) -> str:
        return self.alpha.revmap(self)

    def __repr__(self) -> str:  # pragma: no cover
        cls_name = self.__class__.__name__
        return f"{cls_name}('{self.alpha.revmap(self)}')"

    # Hooking into the subseq's slicing here to add the
    # alphabet to sub-strings.
    def init_slice(self: S, clone: S,
                   x: typing.Sequence[int], start: int, stop: int
                   ) -> None:
        super().init_slice(clone, x, start, stop)
        clone.alpha = self.alpha
