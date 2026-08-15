import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

fig, ax = plt.subplots(figsize=(8, 11))
ax.set_xlim(0, 10)
ax.set_ylim(0, 13.5)
ax.axis("off")

verde = "#1b5e20"
marrom = "#6b4a34"
azul = "#0b6e8f"
areia = "#f2e8d5"
branco = "#ffffff"


def caixa(x, y, w, h, texto, cor_borda=verde, cor_fundo=branco, fontsize=8.5):
    box = mpatches.FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                                   linewidth=1.6, edgecolor=cor_borda, facecolor=cor_fundo)
    ax.add_patch(box)
    ax.text(x, y, texto, ha="center", va="center", fontsize=fontsize, color="#2b2018", wrap=True)


def losango(x, y, w, h, texto, fontsize=8.5):
    pts = [(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)]
    diamond = plt.Polygon(pts, closed=True, edgecolor=marrom, facecolor=areia, linewidth=1.6)
    ax.add_patch(diamond)
    ax.text(x, y, texto, ha="center", va="center", fontsize=fontsize, color="#2b2018")


def seta(x1, y1, x2, y2):
    arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14, color="#4e342e", linewidth=1.3)
    ax.add_patch(arrow)


caixa(5, 13.0, 7.0, 0.85,
      "Início: usuário informa data, local (latitude, altitude),\nTmáx, Tmín, URmáx, URmín, vento e Rs (radiação medida)")
seta(5, 12.55, 5, 11.95)

losango(5, 11.0, 5.8, 1.6, "Dados válidos?\n(Tmín ≤ Tmáx; UR 0-100%;\nvento e Rs ≥ 0)")
seta(7.9, 11.0, 8.8, 11.0)
ax.text(8.35, 11.3, "não", fontsize=8, ha="center")
caixa(8.8, 11.0, 2.0, 0.7, "Exibe mensagem\nde erro", cor_borda="#a03030")
seta(8.8, 10.65, 5.9, 9.75)

seta(5, 10.2, 5, 9.6)
ax.text(4.75, 9.9, "sim", fontsize=8, ha="right")

caixa(5, 8.9, 7.2, 1.0,
      "Calcula Tmédia, Δ (declividade da curva de pressão\nde vapor), γ (psicrométrica), es, ea e déficit de pressão")
seta(5, 8.35, 5, 7.75)

caixa(5, 6.95, 7.2, 1.3,
      "Calcula radiação: Ra (extraterrestre, por latitude e dia\ndo ano), Rso (céu limpo), Rns e Rnl (onda curta/longa)\ne Rn = Rns − Rnl")
seta(5, 6.25, 5, 5.65)

caixa(5, 5.15, 7.2, 0.8, "Converte a velocidade do vento para 2 m de altura (u2),\nse medida em outra altura")
seta(5, 4.7, 5, 4.1)

caixa(5, 3.55, 7.4, 1.1,
      "Aplica a equação de Penman-Monteith:\nETo = [0,408·Δ·(Rn−G) + γ·(900/(T+273))·u2·(es−ea)]\n/ [Δ + γ·(1 + 0,34·u2)]",
      cor_borda=azul, fontsize=8)
seta(5, 2.95, 5, 2.35)

caixa(5, 1.8, 6.6, 0.85, "Exibe ETo (mm/dia) e as variáveis intermediárias\n(Δ, γ, es, ea, Ra, Rn, u2)", cor_borda=verde)

ax.set_title("Fluxograma — Aspersor ETo (FAO-56 Penman-Monteith)", fontsize=13, color=verde, fontweight="bold", pad=14)

plt.tight_layout()
plt.savefig("fluxograma.png", dpi=200, facecolor="white")
print("Fluxograma salvo.")
