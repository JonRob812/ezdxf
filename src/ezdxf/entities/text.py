# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# Created 2019-02-15
from typing import TYPE_CHECKING, Tuple, Union
import math
from ezdxf.math import Vector, Matrix44
from ezdxf.math.transformtools import OCSTransform

from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType, DXFValueError
from ezdxf.lldxf import const
from ezdxf.lldxf.const import DXF12, SUBCLASS_MARKER, SPECIAL_CHARS_ENCODING
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Vertex, DXFNamespace, Drawing

__all__ = ['Text', 'acdb_text', 'plain_text']

acdb_text = DefSubclass('AcDbText', {
    'insert': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),  # First alignment point (in OCS)
    'height': DXFAttr(40, default=2.5),  # Text height
    'text': DXFAttr(1, default=''),  # Default value (the string itself)
    'rotation': DXFAttr(50, default=0, optional=True),  # Text rotation (optional) in degrees (circle = 360deg)
    'oblique': DXFAttr(51, default=0, optional=True),  # Oblique angle (optional) in degrees, vertical = 0deg
    'style': DXFAttr(7, default='Standard', optional=True),  # Text style name (optional)
    'width': DXFAttr(41, default=1, optional=True),  # Relative X scale factor—width (optional)
    # This value is also adjusted when fit-type text is used
    'text_generation_flag': DXFAttr(71, default=0, optional=True),  # Text generation flags (optional)
    # 2 = backward (mirror-x),
    # 4 = upside down (mirror-y)

    # Horizontal text justification type (optional) horizontal justification
    'halign': DXFAttr(72, default=0, optional=True),
    # 0 = Left
    # 2 = Right
    # 3 = Aligned (if vertical alignment = 0)
    # 4 = Middle (if vertical alignment = 0)
    # 5 = Fit (if vertical alignment = 0)

    # This value is meaningful only if the value of a 72 or 73 group is nonzero (if the justification is anything other
    # than baseline/left)
    'align_point': DXFAttr(11, xtype=XType.point3d, optional=True),  # Second alignment point (in OCS) (optional)
    'thickness': DXFAttr(39, default=0, optional=True),  # Thickness (optional)
    # Extrusion direction (optional)
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1), optional=True),
})

acdb_text2 = DefSubclass('AcDbText', {
    'valign': DXFAttr(73, default=0, optional=True)  # Vertical text justification type (optional)
    # 0 = Baseline
    # 1 = Bottom
    # 2 = Middle
    # 3 = Top
})


# Formatting codes:
# %%d: '°'
# %%u in TEXT start underline formatting until next %%u or until end of line

@register_entity
class Text(DXFGraphic):
    """ DXF TEXT entity """
    DXFTYPE = 'TEXT'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_text, acdb_text2)
    # horizontal align values
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    # vertical align values
    BASELINE = 0
    BOTTOM = 1
    MIDDLE = 2
    TOP = 3
    # text generation flags
    MIRROR_X = 2
    MIRROR_Y = 4
    BACKWARD = MIRROR_X
    UPSIDE_DOWN = MIRROR_Y

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        """ Loading interface. (internal API) """
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_text, 2)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_text.name)

            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_text2, 3)
            if len(tags) and not processor.r12:
                processor.log_unprocessed_tags(tags, subclass=acdb_text2.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. (internal API) """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        self.export_acdb_text(tagwriter)
        self.export_acdb_text2(tagwriter)

    def export_acdb_text(self, tagwriter: 'TagWriter') -> None:
        """ Export TEXT data as DXF tags. (internal API) """
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_text.name)
        # for all DXF versions
        if self.dxf.hasattr('text'):
            self.dxf.text = safe_text(self.dxf.text)
        self.dxf.export_dxf_attribs(tagwriter, [
            'insert', 'height', 'text', 'thickness', 'rotation', 'oblique', 'style', 'width', 'text_generation_flag',
            'halign', 'align_point', 'extrusion'
        ])

    def export_acdb_text2(self, tagwriter: 'TagWriter') -> None:
        """ Export TEXT data as DXF tags. (internal API) """
        if tagwriter.dxfversion > DXF12:
            tagwriter.write_tag2(SUBCLASS_MARKER, acdb_text2.name)
        self.dxf.export_dxf_attribs(tagwriter, 'valign')

    def set_pos(self, p1: 'Vertex', p2: 'Vertex' = None, align: str = None) -> 'Text':
        """
        Set text alignment, valid alignments are:

        ============   =============== ================= =====
        Vertical       Left            Center            Right
        ============   =============== ================= =====
        Top            TOP_LEFT        TOP_CENTER        TOP_RIGHT
        Middle         MIDDLE_LEFT     MIDDLE_CENTER     MIDDLE_RIGHT
        Bottom         BOTTOM_LEFT     BOTTOM_CENTER     BOTTOM_RIGHT
        Baseline       LEFT            CENTER            RIGHT
        ============   =============== ================= =====

        Alignments ``'ALIGNED'`` and ``'FIT'`` are special, they require a second alignment point, text is aligned
        on the virtual line between these two points and has vertical alignment `Baseline`.

        - ``'ALIGNED'``: Text is stretched or compressed to fit exactly between `p1` and `p2` and the text height is also
          adjusted to preserve height/width ratio.
        - ``'FIT'``: Text is stretched or compressed to fit exactly between `p1` and `p2` but only the text width is
          adjusted, the text height is fixed by the :attr:`dxf.height` attribute.
        - ``'MIDDLE'``: also a special adjustment, but the result is the same as for ``'MIDDLE_CENTER'``.

        Args:
            p1: first alignment point as (x, y[, z]) tuple
            p2: second alignment point as (x, y[, z]) tuple, required for ``'ALIGNED'`` and ``'FIT'`` else ignored
            align: new alignment, ``None`` for preserve existing alignment.

        """
        if align is None:
            align = self.get_align()
        align = align.upper()
        self.set_align(align)
        self.set_dxf_attrib('insert', p1)
        if align in ('ALIGNED', 'FIT'):
            if p2 is None:
                raise DXFValueError("Alignment '{}' requires a second alignment point.".format(align))
        else:
            p2 = p1
        self.set_dxf_attrib('align_point', p2)
        return self

    def get_pos(self) -> Tuple[str, 'Vertex', Union['Vertex', None]]:
        """
        Returns a tuple (`align`, `p1`, `p2`), `align` is the alignment method, `p1` is the alignment point, `p2` is
        only relevant if `align` is ``'ALIGNED'`` or ``'FIT'``, otherwise it is ``None``.

        """
        p1 = self.dxf.insert
        p2 = self.get_dxf_attrib('align_point', (0., 0., 0.))
        align = self.get_align()
        if align == 'LEFT':
            return align, p1, None
        if align in ('FIT', 'ALIGN'):
            return align, p1, p2
        return align, p2, None

    def set_align(self, align: str = 'LEFT') -> 'Text':
        """
        Just for experts: Sets the text alignment without setting the alignment points, set adjustment points
        attr:`dxf.insert` and :attr:`dxf.align_point` manually.

        Args:
            align: test alignment, see also :meth:`set_pos`

        """
        align = align.upper()
        halign, valign = const.TEXT_ALIGN_FLAGS[align]
        self.set_dxf_attrib('halign', halign)
        self.set_dxf_attrib('valign', valign)
        return self

    def get_align(self) -> str:
        """ Returns the actual text alignment as string, see also :meth:`set_pos`. """
        halign = self.get_dxf_attrib('halign', 0)
        valign = self.get_dxf_attrib('valign', 0)
        if halign > 2:
            valign = 0
        return const.TEXT_ALIGNMENT_BY_FLAGS.get((halign, valign), 'LEFT')

    def transform(self, m: Matrix44) -> 'Text':
        """ Transform TEXT entity by transformation matrix `m` inplace.

        .. versionadded:: 0.13

        """
        dxf = self.dxf
        if not dxf.hasattr('align_point'):
            dxf.align_point = dxf.insert
        ocs = OCSTransform(self.dxf.extrusion, m)
        dxf.insert = ocs.transform_vertex(dxf.insert)
        dxf.align_point = ocs.transform_vertex(dxf.align_point)
        old_rotation = dxf.rotation
        new_rotation = ocs.transform_deg_angle(old_rotation)
        x_scale = ocs.transform_length(Vector.from_deg_angle(old_rotation))
        y_scale = ocs.transform_length(Vector.from_deg_angle(old_rotation + 90.0))

        if not ocs.scale_uniform:
            oblique_vec = Vector.from_deg_angle(old_rotation + 90.0 - dxf.oblique)
            new_oblique_deg = new_rotation + 90.0 - ocs.transform_direction(oblique_vec).angle_deg
            dxf.oblique = new_oblique_deg
            y_scale *= math.cos(math.radians(new_oblique_deg))

        dxf.width *= x_scale / y_scale
        dxf.height *= y_scale
        dxf.rotation = new_rotation

        if dxf.hasattr('thickness'):  # can be negative
            dxf.thickness = ocs.transform_length((0, 0, dxf.thickness), reflection=dxf.thickness)
        dxf.extrusion = ocs.new_extrusion
        return self

    def translate(self, dx: float, dy: float, dz: float) -> 'Text':
        """ Optimized TEXT/ATTRIB/ATTDEF translation about `dx` in x-axis, `dy` in y-axis and `dz` in z-axis,
        returns `self` (floating interface).

        .. versionadded:: 0.13

        """
        ocs = self.ocs()
        dxf = self.dxf
        vec = Vector(dx, dy, dz)

        dxf.insert = ocs.from_wcs(vec + ocs.to_wcs(dxf.insert))
        if dxf.hasattr('align_point'):
            dxf.align_point = ocs.from_wcs(vec + ocs.to_wcs(dxf.align_point))
        return self

    def remove_dependencies(self, other: 'Drawing' = None) -> None:
        """
        Remove all dependencies from actual document.
        (internal API)

        """
        if not self.is_alive:
            return

        super().remove_dependencies()
        has_style = (bool(other) and (self.dxf.style in other.styles))
        if not has_style:
            self.dxf.style = 'Standard'

    def plain_text(self) -> str:
        """
        Returns text content without formatting codes.

        .. versionadded:: 0.13

        """
        return plain_text(self.dxf.text)


def plain_text(text: str) -> str:
    chars = []
    raw_chars = list(reversed(safe_text(text)))
    while len(raw_chars):
        char = raw_chars.pop()
        if char == '%':  # special characters
            if len(raw_chars) and raw_chars[-1] == '%':
                raw_chars.pop()  # discard next '%'
                if len(raw_chars):
                    special_char = raw_chars.pop()
                    # replace or discard formatting code
                    chars.append(SPECIAL_CHARS_ENCODING.get(special_char, ''))
            else:  # char is just a single '%'
                chars.append(char)
        else:  # char is what it is, a character
            chars.append(char)

    return "".join(chars)


def safe_text(t: str):
    # Writing '\n' or '\r' into DXF files creates invalid files.
    return t.replace('\n', '').replace('\r', '')
