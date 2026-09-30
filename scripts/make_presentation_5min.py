"""Build the final five-minute oral presentation.

The deck is deliberately short: slides 2--5 map one-to-one to the four items
requested in the presentation brief.  Speaker notes contain a compact script.
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "presentacion_final_ligo_5min.pptx"

NAVY = RGBColor(12, 24, 43)
INK = RGBColor(32, 43, 57)
WHITE = RGBColor(247, 249, 252)
MUTED = RGBColor(189, 202, 216)
TEAL = RGBColor(48, 181, 164)
ORANGE = RGBColor(241, 126, 61)
PALE_TEAL = RGBColor(223, 246, 241)
PALE_ORANGE = RGBColor(255, 236, 220)


def add_text(slide, text, x, y, w, h, size=20, color=WHITE, bold=False,
             align=PP_ALIGN.LEFT, font="Aptos", margin=0.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    p.font.name = font
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    return box


def rect(slide, x, y, w, h, fill, radius=True, line=None):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line:
        shape.line.color.rgb = line
    else:
        shape.line.fill.background()
    return shape


def base_slide(prs, label, title, subtitle=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = NAVY
    rect(slide, 0.65, 0.45, 1.55, 0.32, TEAL)
    add_text(slide, label.upper(), 0.72, 0.43, 1.4, 0.35, 9, NAVY, True, align=PP_ALIGN.CENTER)
    add_text(slide, title, 0.7, 0.93, 12.0, 0.62, 29, WHITE, True)
    if subtitle:
        add_text(slide, subtitle, 0.73, 1.56, 11.7, 0.38, 13, MUTED)
    add_text(slide, "LIGO selection  ·  Proyecto final", 0.7, 7.08, 4.0, 0.2, 9, MUTED)
    return slide


def note(slide, text):
    slide.notes_slide.notes_text_frame.text = text


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# 1. Cover
s = prs.slides.add_slide(prs.slide_layouts[6])
s.background.fill.solid()
s.background.fill.fore_color.rgb = NAVY
rect(s, 0.75, 0.78, 1.72, 0.34, TEAL)
add_text(s, "PROYECTO FINAL", 0.82, 0.76, 1.56, 0.35, 10, NAVY, True, align=PP_ALIGN.CENTER)
add_text(s, "¿De qué es ciego LIGO?\nEfectos de selección en el catálogo de fusiones", 0.78, 1.42, 11.45, 1.85, 31, WHITE, True)
add_text(s, "Proyecto final · Ondas Gravitacionales e Investigación Asistida por IA", 0.82, 3.58, 10.7, 0.42, 17, MUTED)
rect(s, 0.82, 5.25, 3.9, 0.08, ORANGE, radius=False)
add_text(s, "Tomás Carpintieri · Agustín Miculicich\nUniversidad de Buenos Aires", 0.82, 5.55, 5.8, 0.65, 16, WHITE)
add_text(s, "5 min", 11.1, 6.45, 1.3, 0.35, 14, TEAL, True, align=PP_ALIGN.RIGHT)
note(s, "20 s. Presentar la pregunta guía: una detección no es una muestra neutral del universo; el detector favorece ciertas fuentes.")

# 2. Problem
s = base_slide(prs, "1 · Problema", "El catálogo observado no es el universo", "La detectabilidad depende tanto de la fuente como de la geometría del detector.")
for x, heading, body, color in [
    (0.85, "FUENTE", "masa\ndistancia", PALE_TEAL),
    (4.65, "GEOMETRÍA", "cielo\norientación", PALE_ORANGE),
    (8.45, "INSTRUMENTO", "ruido\numbral SNR", PALE_TEAL),
]:
    rect(s, x, 2.45, 2.85, 1.6, color)
    add_text(s, heading, x + .24, 2.65, 2.35, .27, 10, INK, True, align=PP_ALIGN.CENTER)
    add_text(s, body, x + .18, 3.02, 2.48, .65, 19, INK, True, align=PP_ALIGN.CENTER)
add_text(s, "→", 3.78, 2.88, .45, .5, 30, TEAL, True, align=PP_ALIGN.CENTER)
add_text(s, "→", 7.58, 2.88, .45, .5, 30, TEAL, True, align=PP_ALIGN.CENTER)
rect(s, 1.15, 4.9, 10.95, 1.05, RGBColor(24, 47, 70))
add_text(s, "Resultado: se detectan preferentemente fuentes cercanas, masivas y bien orientadas.", 1.45, 5.12, 10.35, .55, 20, WHITE, True, align=PP_ALIGN.CENTER)
note(s, "45 s. La pregunta no es solamente si una fusión existe, sino qué tan probable es que esta red la detecte. Esa probabilidad sesga cualquier conclusión sobre poblaciones de agujeros negros.")

# 3. Main result
s = base_slide(prs, "2 · Resultado principal", "El horizonte óptimo sobrestima el alcance típico", "Para GW150914, la orientación y la posición en el cielo reducen fuertemente el volumen accesible.")
rect(s, .82, 2.15, 3.78, 2.45, PALE_TEAL)
add_text(s, "HORIZONTE ÓPTIMO", 1.1, 2.5, 3.22, .28, 11, INK, True, align=PP_ALIGN.CENTER)
add_text(s, "1 969.9", 1.02, 2.95, 3.35, .62, 31, INK, True, align=PP_ALIGN.CENTER)
add_text(s, "Mpc", 1.02, 3.66, 3.35, .32, 16, INK, align=PP_ALIGN.CENTER)
add_text(s, "mejor caso: fuente alineada", 1.02, 4.07, 3.35, .25, 10, INK, align=PP_ALIGN.CENTER)
add_text(s, "÷ 2.2649", 4.82, 3.0, 3.55, .5, 27, ORANGE, True, align=PP_ALIGN.CENTER)
add_text(s, "factor horizonte / rango", 4.82, 3.55, 3.55, .3, 12, MUTED, align=PP_ALIGN.CENTER)
rect(s, 8.72, 2.15, 3.78, 2.45, PALE_ORANGE)
add_text(s, "VOLUMEN EUCLÍDEO", 8.98, 2.5, 3.25, .28, 11, INK, True, align=PP_ALIGN.CENTER)
add_text(s, "32.02", 8.92, 2.95, 3.35, .62, 31, INK, True, align=PP_ALIGN.CENTER)
add_text(s, "Gpc³", 8.92, 3.66, 3.35, .32, 16, INK, align=PP_ALIGN.CENTER)
add_text(s, "el volumen cambia como D³", 8.92, 4.07, 3.35, .25, 10, INK, align=PP_ALIGN.CENTER)
rect(s, 1.13, 5.23, 11.05, .73, RGBColor(24, 47, 70))
add_text(s, "Una pequeña pérdida de alcance se amplifica cúbicamente en el número de eventos observables.", 1.4, 5.38, 10.5, .35, 16, WHITE, True, align=PP_ALIGN.CENTER)
note(s, "55 s. Este es el resultado central. El horizonte es el caso ideal; al promediar la respuesta angular, horizonte/rango es 2.2649. Como el volumen crece como distancia al cubo, no modelar selección afecta mucho los conteos.")

# 4. Validation
s = base_slide(prs, "3 · Validación", "Antes de estimar selección, recuperamos GW150914", "El mismo pipeline encuentra la señal conocida en datos reales de los dos detectores.")
s.shapes.add_picture(str(ROOT / "figures" / "f01_snr_timeseries.png"), Inches(.83), Inches(2.05), width=Inches(7.25))
for y, value, label, color in [
    (2.25, "19.81", "SNR en H1", PALE_ORANGE),
    (3.55, "13.54", "SNR en L1", PALE_TEAL),
    (4.85, "−7.08 ms", "L1 llega antes", PALE_ORANGE),
]:
    rect(s, 8.55, y, 3.55, 1.02, color)
    add_text(s, value, 8.78, y+.15, 1.5, .38, 21, INK, True)
    add_text(s, label, 10.15, y+.18, 1.68, .3, 13, INK, align=PP_ALIGN.RIGHT)
add_text(s, "Además: match de waveform frente a LAL = 1.000", 8.62, 6.18, 3.42, .35, 12, MUTED, True, align=PP_ALIGN.CENTER)
note(s, "55 s. Mostrar el pico en ambos detectores. El test de control recupera SNR 19.81 en Hanford y 13.54 en Livingston, con el retraso esperado. También contrastamos nuestra waveform con LAL: match 1.000.")

# 5. Experience
s = base_slide(prs, "4 · Experiencia / aprendizaje", "La lección fue validar antes de inferir", "Cada afirmación importante quedó asociada a datos, una prueba y una limitación explícita.")
for x, number, title, body, color in [
    (.85, "01", "Datos reproducibles", "strain y waveforms\nverificados con hash", PALE_TEAL),
    (4.65, "02", "Tests antes que conclusiones", "39 controles automáticos\ny figuras regenerables", PALE_ORANGE),
    (8.45, "03", "Límites declarados", "TaylorF2 subestima\nsistemas pesados", PALE_TEAL),
]:
    rect(s, x, 2.35, 3.0, 2.9, color)
    add_text(s, number, x+.28, 2.62, .7, .43, 22, TEAL, True)
    add_text(s, title, x+.3, 3.27, 2.4, .5, 17, INK, True)
    add_text(s, body, x+.3, 3.97, 2.38, .68, 13, INK)
rect(s, 1.25, 5.86, 10.7, .55, RGBColor(24, 47, 70))
add_text(s, "Un resultado confiable no es solo un número: es un número que puede volver a producirse y discutirse.", 1.52, 5.97, 10.15, .3, 14, WHITE, True, align=PP_ALIGN.CENTER)
note(s, "45 s. Esta fue la dificultad y el aprendizaje del proyecto: no aceptar un número solo porque parece razonable. El pipeline tiene datos hasheados, tests y procedencia. Una limitación importante: inspiral-only subestima la detectabilidad de sistemas pesados como GW150914.")

# 6. Closing
s = base_slide(prs, "Cierre", "Modelar la selección es el primer paso")
rect(s, .9, 2.15, 11.55, 1.1, RGBColor(24, 47, 70))
add_text(s, "El universo observado por LIGO es una población filtrada por distancia, masa y geometría.", 1.22, 2.38, 10.9, .55, 21, WHITE, True, align=PP_ALIGN.CENTER)
add_text(s, "Siguiente paso", 1.0, 4.05, 3.0, .42, 14, TEAL, True)
add_text(s, "Campaña de inyecciones: simular una población, insertarla en datos reales y medir qué fracción recupera la red.", 1.0, 4.48, 10.65, 1.05, 20, WHITE, True)
add_text(s, "Gracias", 10.25, 6.15, 2.0, .45, 23, TEAL, True, align=PP_ALIGN.RIGHT)
note(s, "25 s. Cerrar con el mensaje principal y el próximo paso concreto: una campaña de inyecciones completa. Abrir preguntas.")

# 7. Questions
s = prs.slides.add_slide(prs.slide_layouts[6])
s.background.fill.solid()
s.background.fill.fore_color.rgb = NAVY
rect(s, .78, 1.0, 1.9, .34, TEAL)
add_text(s, "PROYECTO FINAL", .85, .98, 1.75, .35, 10, NAVY, True, align=PP_ALIGN.CENTER)
add_text(s, "Gracias por escucharnos", 1.0, 2.35, 11.3, .75, 35, WHITE, True, align=PP_ALIGN.CENTER)
add_text(s, "Esperamos sus preguntas", 1.0, 3.35, 11.3, .45, 21, TEAL, align=PP_ALIGN.CENTER)
rect(s, 4.75, 4.38, 3.85, .07, ORANGE, radius=False)
add_text(s, "Tomás Carpintieri · Agustín Miculicich", 1.0, 5.25, 11.3, .4, 16, MUTED, align=PP_ALIGN.CENTER)
add_text(s, "Universidad de Buenos Aires", 1.0, 5.75, 11.3, .35, 14, MUTED, align=PP_ALIGN.CENTER)
note(s, "Dejar esta diapositiva visible durante las preguntas. No hace falta decir más que: gracias por escucharnos; esperamos sus preguntas.")

prs.save(OUT)
print(OUT)
