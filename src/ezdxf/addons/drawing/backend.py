# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
from abc import ABC, abstractmethod
from typing import Optional, Tuple, TYPE_CHECKING, Iterable

from ezdxf.addons.drawing.properties import Properties
from ezdxf.addons.drawing.type_hints import Color
from ezdxf.entities import DXFGraphic
from ezdxf.math import Vector, Matrix44
from ezdxf.render.path import Path

if TYPE_CHECKING:
    from ezdxf.addons.drawing.text import FontMeasurements


class Backend(ABC):
    def __init__(self):
        self._current_entity = None
        self._current_entity_stack = ()
        # Approximate cubic Bèzier-curves by `n` segments, only used for basic back-ends
        # without draw_path() support.
        self.bezier_approximation_count = 32

    def set_current_entity(self, entity: Optional[DXFGraphic], parent_stack: Tuple[DXFGraphic, ...] = ()) -> None:
        self._current_entity = entity
        self._current_entity_stack = parent_stack

    @property
    def current_entity(self) -> Optional[DXFGraphic]:
        """ obtain the current entity being drawn """
        return self._current_entity

    @property
    def current_entity_stack(self) -> Tuple[DXFGraphic, ...]:
        """ When the entity is virtual, the stack of entities which were exploded to obtain the entity.
        When the entity is 'real', an empty tuple.
        """
        return self._current_entity_stack

    @abstractmethod
    def set_background(self, color: Color) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_line(self, start: Vector, end: Vector, properties: Properties) -> None:
        raise NotImplementedError

    def draw_path(self, path: Path, properties) -> None:
        """ Fall-back implementation, approximate path by line segments.

        Override in inherited back-end for a more efficient implementation.

        """
        if len(path):
            vertices = iter(path.approximate(segments=self.bezier_approximation_count))
            prev = next(vertices)
            for vertex in vertices:
                self.draw_line(prev, vertex, properties)
                prev = vertex

    @abstractmethod
    def draw_point(self, pos: Vector, properties: Properties) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_filled_polygon(self, points: Iterable[Vector], properties: Properties) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_text(self, text: str, transform: Matrix44, properties: Properties, cap_height: float) -> None:
        """ draw a single line of text with the anchor point at the baseline left point """
        raise NotImplementedError

    @abstractmethod
    def get_font_measurements(self, cap_height: float, font: str = None) -> 'FontMeasurements':
        """ note: backends might want to cache the results of these calls """
        raise NotImplementedError

    @abstractmethod
    def get_text_line_width(self, text: str, cap_height: float, font: str = None) -> float:
        """ get the width of a single line of text """
        # https://stackoverflow.com/questions/32555015/how-to-get-the-visual-length-of-a-text-string-in-python
        # https://stackoverflow.com/questions/4190667/how-to-get-width-of-a-truetype-font-character-in-1200ths-of-an-inch-with-python
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """ clear the canvas. Does not reset the internal state of the backend. Make sure that the previous drawing
        is finished before clearing.
        """
        raise NotImplementedError

    def finalize(self) -> None:
        pass
