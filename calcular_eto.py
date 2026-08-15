"""
Calculo em lote da ETo (evapotranspiracao de referencia) diaria pelo metodo
FAO Penman-Monteith (FAO-56), a partir de uma planilha/CSV com dados
meteorologicos diarios.

A formula esta implementada e validada em eto_penman_monteith.py
(ver validar_fao56_exemplo18.py para a auditoria contra o exemplo oficial da FAO).

FORMATO DO ARQUIVO DE ENTRADA (CSV, separador ";" ou ","):
    data          - data no formato AAAA-MM-DD (ou DD/MM/AAAA)
    tmax          - temperatura maxima do dia [degC]
    tmin          - temperatura minima do dia [degC]
    rhmax         - umidade relativa maxima do dia [%]
    rhmin         - umidade relativa minima do dia [%]
    vento_ms      - velocidade do vento [m/s], medida na altura informada em --altura-vento
    rs_mj_m2_dia  - radiacao solar incidente medida [MJ m-2 dia-1]

Ver dados_exemplo.csv para um modelo pronto (contem o Exemplo 18 do FAO-56).

USO:
    python calcular_eto.py --entrada dados_exemplo.csv --saida eto_resultado.csv ^
        --latitude 50.8 --altitude 100 --altura-vento 10

    (no Windows/PowerShell use ^ para quebrar linha; no Git Bash use \\)

Se a radiacao solar (rs_mj_m2_dia) nao estiver disponivel, mas houver horas de
insolacao (n), calcule Rs antes com radiacao_solar_de_insolacao() e inclua o
resultado na coluna rs_mj_m2_dia do CSV - ver eto_penman_monteith.py.
"""

import argparse
import csv
import sys
from pathlib import Path

from eto_penman_monteith import eto_penman_monteith, vento_a_2m, dia_juliano

try:
    from datetime import datetime
except ImportError:  # pragma: no cover
    raise

FORMATOS_DATA_ACEITOS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y")


def parse_data(texto):
    texto = texto.strip()
    for formato in FORMATOS_DATA_ACEITOS:
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue
    raise ValueError(
        f"Data '{texto}' nao reconhecida. Use AAAA-MM-DD ou DD/MM/AAAA."
    )


def ler_numero(texto):
    """Aceita numeros com virgula ou ponto decimal."""
    return float(texto.strip().replace(",", "."))


def detectar_separador(caminho_csv):
    with open(caminho_csv, encoding="utf-8-sig") as f:
        primeira_linha = f.readline()
    return ";" if primeira_linha.count(";") >= primeira_linha.count(",") else ","


def processar_arquivo(caminho_entrada, caminho_saida, latitude, altitude, altura_vento):
    separador = detectar_separador(caminho_entrada)
    linhas_saida = []
    avisos = []

    with open(caminho_entrada, encoding="utf-8-sig", newline="") as f:
        leitor = csv.DictReader(f, delimiter=separador)
        colunas_esperadas = {"data", "tmax", "tmin", "rhmax", "rhmin", "vento_ms", "rs_mj_m2_dia"}
        colunas_presentes = {c.strip().lower() for c in leitor.fieldnames or []}
        faltando = colunas_esperadas - colunas_presentes
        if faltando:
            raise ValueError(
                f"Colunas faltando no CSV de entrada: {sorted(faltando)}. "
                f"Colunas encontradas: {sorted(colunas_presentes)}"
            )

        for n_linha, linha in enumerate(leitor, start=2):
            linha = {k.strip().lower(): v for k, v in linha.items()}
            try:
                data = parse_data(linha["data"])
                tmax = ler_numero(linha["tmax"])
                tmin = ler_numero(linha["tmin"])
                rhmax = ler_numero(linha["rhmax"])
                rhmin = ler_numero(linha["rhmin"])
                vento = ler_numero(linha["vento_ms"])
                rs = ler_numero(linha["rs_mj_m2_dia"])
            except (KeyError, ValueError) as exc:
                avisos.append(f"Linha {n_linha}: ignorada ({exc})")
                continue

            if tmin > tmax:
                avisos.append(
                    f"Linha {n_linha} ({linha['data']}): tmin ({tmin}) > tmax ({tmax}) - verifique os dados."
                )

            u2 = vento_a_2m(vento, altura_vento)
            j = dia_juliano(data)

            resultado = eto_penman_monteith(
                tmax_c=tmax, tmin_c=tmin, rhmax_pct=rhmax, rhmin_pct=rhmin,
                u2_ms=u2, rs_mj_m2_dia=rs,
                latitude_graus=latitude, altitude_m=altitude, dia_juliano_j=j,
            )

            linhas_saida.append({
                "data": data.strftime("%Y-%m-%d"),
                "dia_juliano": j,
                "tmax_c": tmax,
                "tmin_c": tmin,
                "tmedia_c": round(resultado["tmedia_c"], 2),
                "rhmax_pct": rhmax,
                "rhmin_pct": rhmin,
                "u2_ms": round(u2, 3),
                "rs_mj_m2_dia": rs,
                "rn_mj_m2_dia": round(resultado["rn_mj_m2_dia"], 3),
                "es_kpa": round(resultado["es_kpa"], 3),
                "ea_kpa": round(resultado["ea_kpa"], 3),
                "eto_mm_dia": round(resultado["eto_mm_dia"], 2),
            })

    if not linhas_saida:
        raise ValueError("Nenhuma linha valida foi processada. Verifique o arquivo de entrada.")

    campos_saida = list(linhas_saida[0].keys())
    with open(caminho_saida, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos_saida, delimiter=";")
        escritor.writeheader()
        escritor.writerows(linhas_saida)

    return linhas_saida, avisos


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--entrada", required=True, help="CSV de entrada com os dados meteorologicos diarios")
    parser.add_argument("--saida", required=True, help="CSV de saida com a ETo calculada")
    parser.add_argument("--latitude", type=float, required=True, help="Latitude do local em graus decimais (positivo = Norte, negativo = Sul)")
    parser.add_argument("--altitude", type=float, required=True, help="Altitude do local em metros")
    parser.add_argument("--altura-vento", type=float, default=2.0, help="Altura de medicao do vento em metros (padrao: 2 m, ou seja, sem conversao)")
    args = parser.parse_args()

    caminho_entrada = Path(args.entrada)
    if not caminho_entrada.exists():
        print(f"Erro: arquivo de entrada '{caminho_entrada}' nao encontrado.", file=sys.stderr)
        sys.exit(1)

    linhas, avisos = processar_arquivo(
        caminho_entrada, args.saida, args.latitude, args.altitude, args.altura_vento
    )

    print(f"{len(linhas)} dia(s) processado(s). Resultado salvo em: {args.saida}")
    if avisos:
        print(f"\n{len(avisos)} aviso(s):")
        for aviso in avisos:
            print(f"  - {aviso}")

    etos = [l["eto_mm_dia"] for l in linhas]
    print(f"\nETo minima:  {min(etos):.2f} mm/dia")
    print(f"ETo maxima:  {max(etos):.2f} mm/dia")
    print(f"ETo media:   {sum(etos)/len(etos):.2f} mm/dia")
    print(f"ETo acumulada no periodo: {sum(etos):.2f} mm")


if __name__ == "__main__":
    main()
