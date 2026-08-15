"""
Auditoria independente de eto_penman_monteith.py.

Reproduz o "Example 18" do FAO Irrigation and Drainage Paper No. 56
(Allen et al. 1998, Capitulo 4) - o exemplo numerico oficial de calculo
de ETo pelo metodo Penman-Monteith, usado como caso de teste padrao-ouro
em toda a literatura de agrometeorologia.

Dados de entrada e resultados esperados (extraidos do texto original do FAO-56,
fonte: https://www.fao.org/4/x0490e/x0490e08.htm):

  Local: Uccle (Bruxelas, Belgica), 50°48'N, 100 m de altitude
  Data: 6 de julho (dia juliano 187)
  Tmax = 21.5 degC | Tmin = 12.3 degC | Tmedia = 16.9 degC
  RHmax = 84% | RHmin = 63%
  Vento medido a 10 m = 10 km/h  ->  u2 esperado = 2.078 m/s
  Insolacao n = 9.25 horas

  Resultados intermediarios esperados (arredondados no documento original):
  es = 1.997 kPa | ea = 1.409 kPa | deficit = 0.589 kPa
  Ra = 41.09 MJ/m2/dia | N = 16.1 h | Rs = 22.07 MJ/m2/dia
  Rns = 17.00 MJ/m2/dia | Rnl = 3.71 MJ/m2/dia | Rn = 13.28 MJ/m2/dia
  ETo final = 3.9 mm/dia (soma dos componentes: 2.81 + 1.07 = 3.88)

Alem do controle positivo (comparar contra os valores certos, esperando 100%
de acerto), o script roda tambem um CONTROLE NEGATIVO: compara os mesmos
valores calculados contra um conjunto de "esperados" deliberadamente
sabotado (cada valor deslocado em +50%). Isso prova que o comparador
realmente detecta divergencia quando ela existe, e nao so retorna "OK"
sempre - sem essa checagem, um comparador com bug (ex.: tolerancia
absurdamente larga) passaria despercebido.

Rodar: python validar_fao56_exemplo18.py
"""

from eto_penman_monteith import (
    pressao_vapor_saturacao_media,
    pressao_vapor_atual,
    radiacao_extraterrestre,
    horas_luz_solar,
    radiacao_solar_de_insolacao,
    vento_a_2m,
    eto_penman_monteith,
)

# --- dados de entrada do Exemplo 18 ---
LATITUDE = 50.8  # 50°48'N = 50 + 48/60
ALTITUDE = 100.0
DIA_JULIANO = 187  # 6 de julho
TMAX = 21.5
TMIN = 12.3
RHMAX = 84.0
RHMIN = 63.0
VENTO_10M_KMH = 10.0
INSOLACAO_N = 9.25

# --- resultados esperados (do documento FAO-56) ---
ESPERADO = {
    "u2_ms": 2.078,
    "es_kpa": 1.997,
    "ea_kpa": 1.409,
    "deficit_pressao_vapor_kpa": 0.589,
    "ra_mj_m2_dia": 41.09,
    "n_horas": 16.1,
    "rs_mj_m2_dia": 22.07,
    "rns_mj_m2_dia": 17.00,
    "rnl_mj_m2_dia": 3.71,
    "rn_mj_m2_dia": 13.28,
    "eto_mm_dia": 3.9,
}

TOLERANCIA = {
    "u2_ms": 0.01,
    "es_kpa": 0.01,
    "ea_kpa": 0.01,
    "deficit_pressao_vapor_kpa": 0.01,
    "ra_mj_m2_dia": 0.02,
    "n_horas": 0.05,
    "rs_mj_m2_dia": 0.05,
    "rns_mj_m2_dia": 0.05,
    "rnl_mj_m2_dia": 0.05,
    "rn_mj_m2_dia": 0.05,
    "eto_mm_dia": 0.05,
}


FATOR_SABOTAGEM = 1.5  # +50% em cada valor esperado, so para o controle negativo


def calcular_exemplo_18():
    """Roda a implementacao real sobre os dados do Exemplo 18 e devolve o dict 'calculado'."""
    vento_10m_ms = VENTO_10M_KMH / 3.6
    u2 = vento_a_2m(vento_10m_ms, altura_medicao_m=10)

    es = pressao_vapor_saturacao_media(TMAX, TMIN)
    ea = pressao_vapor_atual(TMAX, TMIN, RHMAX, RHMIN)
    deficit = es - ea

    ra = radiacao_extraterrestre(LATITUDE, DIA_JULIANO)
    n_max = horas_luz_solar(LATITUDE, DIA_JULIANO)
    rs = radiacao_solar_de_insolacao(INSOLACAO_N, n_max, ra)

    resultado = eto_penman_monteith(
        tmax_c=TMAX, tmin_c=TMIN, rhmax_pct=RHMAX, rhmin_pct=RHMIN,
        u2_ms=u2, rs_mj_m2_dia=rs,
        latitude_graus=LATITUDE, altitude_m=ALTITUDE, dia_juliano_j=DIA_JULIANO,
    )

    return {
        "u2_ms": u2,
        "es_kpa": es,
        "ea_kpa": ea,
        "deficit_pressao_vapor_kpa": deficit,
        "ra_mj_m2_dia": ra,
        "n_horas": n_max,
        "rs_mj_m2_dia": rs,
        "rns_mj_m2_dia": resultado["rns_mj_m2_dia"],
        "rnl_mj_m2_dia": resultado["rnl_mj_m2_dia"],
        "rn_mj_m2_dia": resultado["rn_mj_m2_dia"],
        "eto_mm_dia": resultado["eto_mm_dia"],
    }


def comparar(calculado, esperado, tolerancia, titulo):
    """Compara 'calculado' contra 'esperado' dentro da 'tolerancia' e imprime a tabela.
    Retorna (n_ok, n_total, percentual_acerto)."""
    print(f"\n=== {titulo} ===")
    print(f"{'Variavel':<28}{'Calculado':>12}{'Esperado':>14}{'Diferenca':>12}{'Status':>10}")
    print("-" * 76)
    n_ok = 0
    n_total = len(calculado)
    for chave, valor_calc in calculado.items():
        valor_esp = esperado[chave]
        tol = tolerancia[chave]
        diferenca = valor_calc - valor_esp
        ok = abs(diferenca) <= tol
        n_ok += int(ok)
        status = "OK" if ok else "DIVERGIU"
        print(f"{chave:<28}{valor_calc:>12.3f}{valor_esp:>14.3f}{diferenca:>+12.3f}{status:>10}")

    percentual = 100 * n_ok / n_total
    print("-" * 76)
    print(f"Acerto: {n_ok}/{n_total} variaveis ({percentual:.0f}%)")
    return n_ok, n_total, percentual


def rodar_validacao():
    calculado = calcular_exemplo_18()

    # --- controle positivo: contra os valores REAIS do FAO-56 -> deve dar 100% ---
    _, _, pct_positivo = comparar(
        calculado, ESPERADO, TOLERANCIA,
        titulo="CONTROLE POSITIVO - implementacao vs. FAO-56 Exemplo 18 (deve dar 100%)",
    )

    # --- controle negativo: contra valores sabotados (+50%) -> deve dar 0% ---
    esperado_sabotado = {chave: valor * FATOR_SABOTAGEM for chave, valor in ESPERADO.items()}
    _, _, pct_negativo = comparar(
        calculado, esperado_sabotado, TOLERANCIA,
        titulo=f"CONTROLE NEGATIVO - implementacao vs. valores sabotados em +{int((FATOR_SABOTAGEM-1)*100)}% (deve dar 0%)",
    )

    print("\n" + "=" * 76)
    passou_positivo = pct_positivo == 100
    passou_negativo = pct_negativo == 0
    print(f"Controle positivo: {pct_positivo:.0f}% de acerto {'(OK, esperado 100%)' if passou_positivo else '(FALHOU, esperava 100%)'}")
    print(f"Controle negativo: {pct_negativo:.0f}% de acerto {'(OK, esperado 0%)' if passou_negativo else '(FALHOU, esperava 0%)'}")

    if passou_positivo and passou_negativo:
        print("\nRESULTADO: implementacao correta E o comparador detecta divergencia corretamente.")
        print("(100% quando comparado com a verdade; 0% quando comparado com valores errados de proposito)")
    elif not passou_positivo:
        print("\nRESULTADO: ATENCAO - a implementacao diverge do exemplo oficial do FAO-56. Revisar a formula.")
    else:
        print("\nRESULTADO: ATENCAO - o comparador nao detectou os valores sabotados. A logica de comparacao tem um bug (ex.: tolerancia larga demais).")

    return passou_positivo and passou_negativo


if __name__ == "__main__":
    rodar_validacao()
