from io import BytesIO
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# def register_fonts():
#     font_name_to_file = {
#         "CMUSerif-Roman": "cmunrm.ttf",
#         "CMUSerif-Italic": "cmunti.ttf",
#         "CMUSerif-Bold": "cmunbx.ttf",
#     }
#     for font_name, font_file in font_name_to_file.items():
#         font = TTFont(font_name, f"static/fonts/cm-unicode-0.7.0/{font_file}")
#         pdfmetrics.registerFont(font)


# register_fonts()


class PDF:
    def __init__(self, header_img: bytes = None):
        self.header_img = header_img

        self._width, self._height = letter

        self._x_margin = 0.1 * self._width
        self._y_margin = 0.1 * self._height

        self._max_width = self._width - 2 * self._x_margin
        self._max_height = self._height - 2 * self._y_margin

        self._x_middle = self._x_margin + ((self._width - (2 * self._x_margin)) / 2)
        self._y_middle = self._y_margin - ((self._height - (2 * self._y_margin)) / 2)

        self._origin = (self._x_margin, self._height - self._y_margin)
        self._x, self._y = self._origin

        self._font_size = 12
        self._line_height = self._font_size * 1.5

        self.the_page = 0
        self.the_section = 0
        self.the_subsection = 0

        self._buffer = BytesIO()
        self._canvas = canvas.Canvas(self._buffer, pagesize=letter)

    def header(self):
        if self.header_img:
            self.add_image(self.header_img, width=150, height=150)
            self.line_break()

    def footer(self):
        self.italic_font()
        self.the_page += 1
        footer_text = f"Page {self.the_page}"
        width = self._canvas.stringWidth(footer_text)
        self._canvas.drawString(
            self._x_middle - width / 2,
            self._y_margin - 2 * self._line_height,
            footer_text,
        )

    def set_font(self, name: str):
        self._canvas.setFont(name, self._font_size)

    def regular_font(self):
        self.set_font("CMUSerif-Roman")

    def italic_font(self):
        self.set_font("CMUSerif-Italic")

    def bold_font(self):
        self.set_font("CMUSerif-Bold")

    def section(self, name: str):
        if self._y - 5 * self._line_height < self._y_margin:
            self.page_break()
        self.the_section += 1
        self.the_subsection = 0
        self._font_size *= 1.2
        self.bold_font()
        self._canvas.drawString(self._x, self._y, f"{self.the_section}  {name.strip()}")
        self._font_size /= 1.2
        self.line_break()
        self.line_break()
        self.regular_font()

    def subsection(self, name: str):
        if self._y - 5 * self._line_height < self._y_margin:
            self.page_break()
        self.the_subsection += 1
        self.bold_font()
        self._canvas.drawString(
            self._x,
            self._y,
            f"{self.the_section}.{self.the_subsection}  {name.strip()}",
        )
        self.line_break()
        self.line_break()
        self.regular_font()

    def draw_text(self, text: str, align: str = "left"):
        lines = []
        words = text.split()
        current_line = words[0].strip()
        for word in words[1:]:
            width = self._canvas.stringWidth(current_line + " " + word.strip())
            if width < self._max_width:
                current_line += " " + word
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)

        for line in lines:
            if self._y - self._line_height < self._y_margin:
                self.page_break()
            self._x, _ = self._origin
            if align == "left":
                pass
            elif align == "center":
                width = self._canvas.stringWidth(line)
                self._x = self._x_middle - width / 2
                pass
            self._canvas.drawString(self._x, self._y, line)
            self._y -= self._line_height

    def add_image(self, image: Image.Image, width: int, height: int):
        if self._y - height < self._y_margin:
            self.page_break()
        self._canvas.drawImage(
            ImageReader(image),
            self._x,
            self._y - height,
            width=width,
            height=height,
            mask="auto",
        )
        self._y -= height

    def line_break(self):
        self._x, _ = self._origin
        self._y -= self._line_height

    def page_break(self):
        self.footer()
        self._canvas.showPage()
        self._x, self._y = self._origin
        self.regular_font()

    def save(self):
        self.footer()
        self._canvas.save()

    def to_bytes(self):
        pdf = self._buffer.getvalue()
        self._buffer.close()
        return pdf
