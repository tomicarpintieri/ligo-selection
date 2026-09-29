"""Create a self-contained PDF presentation from verified project outputs."""
import pathlib
import sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg

slides = [
    ("Sesgo de selección y observabilidad en LIGO", ["El caso GW150914", "Proyecto reproducible · UBA", "[Tu nombre] · 2026"], None),
    ("Motivación", ["Un catálogo de detecciones es un universo filtrado.", "La detectabilidad depende de distancia, masa, orientación y cielo.", "Población observada ≠ población intrínseca."], None),
    ("Validación: GW150914", ["SNR H1 = 19.810; SNR L1 = 13.543.", "Delay L1−H1 = −7.080 ms.", "Control en datos reales antes de inferir selección."], "f01_snr_timeseries.png"),
    ("Waveform propia frente a LAL", ["TaylorF2 no giratoria, fase 3.5PN.", "Match contra LAL = 1.000.", "Inspiral-only subestima sistemas pesados."], "f02_waveform_vs_lal.png"),
    ("Sensibilidad, horizonte y volumen", ["ρ ∝ 1/D; V ∝ D³.", "Horizonte óptimo: 1969.9 Mpc.", "Volumen euclídeo: 32.02 Gpc³."], "f03_horizon_vs_mchirp.png"),
    ("Geometría y red", ["Cuatro puntos ciegos exactos en un interferómetro L.", "Horizonte/rango = 2.26487.", "Delay máximo H1−L1 = 10.00274 ms.", "La red mejora cobertura, pero un delay define un anillo, no un punto."], None),
    ("Conclusiones", ["La demografía de agujeros negros requiere corregir selección.", "El sesgo favorece fuentes cercanas, masivas y bien orientadas.", "Pipeline reproducible: results, provenance, figuras y tests."], None),
]

with PdfPages(ROOT / "presentacion_sesgo_seleccion_ligo_10min.pdf") as pdf:
    for title, points, figure in slides:
        fig, ax = plt.subplots(figsize=(13.333, 7.5)); fig.patch.set_facecolor("#0d182b"); ax.set_facecolor("#0d182b"); ax.axis("off")
        ax.text(.05,.91,title,color="white",fontsize=26,fontweight="bold",transform=ax.transAxes)
        for i, point in enumerate(points): ax.text(.07,.73-i*.11,"• "+point,color="white",fontsize=17,transform=ax.transAxes)
        if figure:
            img=mpimg.imread(ROOT / "figures" / figure); ax.imshow(img,extent=(.52,.96,.08,.68),aspect="auto",transform=ax.transAxes)
        ax.text(.05,.04,"LIGO selection · resultados verificados y reproducibles",color="#aabccc",fontsize=10,transform=ax.transAxes)
        pdf.savefig(fig,bbox_inches="tight"); plt.close(fig)
