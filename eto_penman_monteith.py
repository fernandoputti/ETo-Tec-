"""
Calculo da evapotranspiracao de referencia (ETo) pelo metodo padrao
FAO Penman-Monteith (FAO Irrigation and Drainage Paper No. 56, Allen et al. 1998).

Todas as equacoes seguem a numeracao e as unidades do Capitulo 3 e 4 do FAO-56:
  - Temperatura: graus Celsius
  - Umidade relativa: %
  - Vento: m/s
  - Radiacao: MJ m-2 dia-1
  - Pressao de vapor: kPa
  - ETo: mm/dia

Este modulo so contem as funcoes de calculo (sem leitura de arquivo).
Uso em lote (CSV) esta em calcular_eto.py.
Validacao contra o Exemplo 18 do FAO-56 esta em validar_fao56_exemplo18.py.
"""

import math

# Constantes fisicas fixas do metodo (FAO-56, Cap. 3)
GSC = 0.0820        # constante solar, MJ m-2 min-1
SIGMA = 4.903e-9     # constante de Stefan-Boltzmann, MJ K-4 m-2 dia-1
ALBEDO = 0.23        # albedo da cultura de referencia (grama)
AS_ANGSTROM = 0.25    # coeficiente de Angstrom (fracao de Ra em dia nublado)
BS_ANGSTROM = 0.50    # coeficiente de Angstrom (fracao adicional em dia de ceu limpo)


def pressao_vapor_saturacao(temperatura_c):
    """e°(T) - pressao de vapor de saturacao a uma dada temperatura [kPa]. Eq. 11."""
    return 0.6108 * math.exp((17.27 * temperatura_c) / (temperatura_c + 237.3))


def declividade_curva_pressao_vapor(temperatura_media_c):
    """Delta - declividade da curva de pressao de vapor de saturacao [kPa/degC]. Eq. 13."""
    es = pressao_vapor_saturacao(temperatura_media_c)
    return (4098 * es) / (temperatura_media_c + 237.3) ** 2


def pressao_atmosferica(altitude_m):
    """P - pressao atmosferica em funcao da altitude [kPa]. Eq. 7."""
    return 101.3 * ((293 - 0.0065 * altitude_m) / 293) ** 5.26


def constante_psicrometrica(altitude_m):
    """Gamma - constante psicrometrica [kPa/degC]. Eq. 8."""
    return 0.000665 * pressao_atmosferica(altitude_m)


def pressao_vapor_saturacao_media(tmax_c, tmin_c):
    """es - pressao de vapor de saturacao media diaria [kPa]. Eq. 12."""
    return (pressao_vapor_saturacao(tmax_c) + pressao_vapor_saturacao(tmin_c)) / 2


def pressao_vapor_atual(tmax_c, tmin_c, rhmax_pct, rhmin_pct):
    """ea - pressao de vapor atual, a partir de RHmax e RHmin [kPa]. Eq. 17."""
    termo_min = pressao_vapor_saturacao(tmin_c) * (rhmax_pct / 100)
    termo_max = pressao_vapor_saturacao(tmax_c) * (rhmin_pct / 100)
    return (termo_min + termo_max) / 2


def pressao_vapor_atual_rh_media(tmax_c, tmin_c, rhmedia_pct):
    """ea - versao simplificada quando so ha UR media (menos precisa). Eq. 19."""
    es = pressao_vapor_saturacao_media(tmax_c, tmin_c)
    return es * (rhmedia_pct / 100)


def dia_juliano(data):
    """Numero do dia do ano (1-365/366) a partir de um datetime.date ou datetime.datetime."""
    return data.timetuple().tm_yday


def radiacao_extraterrestre(latitude_graus, dia_juliano_j):
    """Ra - radiacao extraterrestre [MJ m-2 dia-1]. Eq. 21."""
    phi = math.radians(latitude_graus)
    dr = 1 + 0.033 * math.cos((2 * math.pi / 365) * dia_juliano_j)
    delta = 0.409 * math.sin((2 * math.pi / 365) * dia_juliano_j - 1.39)
    ws = math.acos(-math.tan(phi) * math.tan(delta))
    ra = (24 * 60 / math.pi) * GSC * dr * (
        ws * math.sin(phi) * math.sin(delta)
        + math.cos(phi) * math.cos(delta) * math.sin(ws)
    )
    return ra


def horas_luz_solar(latitude_graus, dia_juliano_j):
    """N - numero maximo de horas de brilho solar (fotoperiodo) [horas]. Eq. 34."""
    phi = math.radians(latitude_graus)
    delta = 0.409 * math.sin((2 * math.pi / 365) * dia_juliano_j - 1.39)
    ws = math.acos(-math.tan(phi) * math.tan(delta))
    return (24 / math.pi) * ws


def radiacao_solar_de_insolacao(horas_insolacao_n, horas_luz_n_max, ra,
                                  as_coef=AS_ANGSTROM, bs_coef=BS_ANGSTROM):
    """Rs - radiacao solar estimada a partir de horas de insolacao (formula de Angstrom).
    Usar apenas quando Rs nao foi medido diretamente. Eq. 35."""
    return (as_coef + bs_coef * (horas_insolacao_n / horas_luz_n_max)) * ra


def radiacao_ceu_limpo(ra, altitude_m):
    """Rso - radiacao solar em dia de ceu limpo [MJ m-2 dia-1]. Eq. 37."""
    return (0.75 + 2e-5 * altitude_m) * ra


def radiacao_liquida_curta(rs, albedo=ALBEDO):
    """Rns - radiacao liquida de onda curta [MJ m-2 dia-1]. Eq. 38."""
    return (1 - albedo) * rs


def radiacao_liquida_longa(tmax_c, tmin_c, ea_kpa, rs, rso):
    """Rnl - radiacao liquida de onda longa [MJ m-2 dia-1]. Eq. 39."""
    tmax_k = tmax_c + 273.16
    tmin_k = tmin_c + 273.16
    termo_temperatura = (tmax_k ** 4 + tmin_k ** 4) / 2
    termo_umidade = 0.34 - 0.14 * math.sqrt(ea_kpa)
    # razao Rs/Rso limitada a 1.0 (nao pode exceder o ceu limpo) e a >=0.3 (limite pratico do FAO-56)
    razao_nebulosidade = max(0.3, min(rs / rso, 1.0)) if rso > 0 else 1.0
    termo_nebulosidade = 1.35 * razao_nebulosidade - 0.35
    return SIGMA * termo_temperatura * termo_umidade * termo_nebulosidade


def radiacao_liquida(rns, rnl):
    """Rn - radiacao liquida total [MJ m-2 dia-1]. Eq. 40."""
    return rns - rnl


def vento_a_2m(u_z, altura_medicao_m):
    """u2 - converte velocidade do vento medida a altura z para 2 m de altura [m/s]. Eq. 47."""
    if altura_medicao_m == 2:
        return u_z
    return u_z * (4.87 / math.log(67.8 * altura_medicao_m - 5.42))


def eto_penman_monteith(tmax_c, tmin_c, rhmax_pct, rhmin_pct, u2_ms, rs_mj_m2_dia,
                          latitude_graus, altitude_m, dia_juliano_j, g_mj_m2_dia=0.0):
    """
    Calcula a ETo diaria pelo metodo FAO Penman-Monteith [mm/dia]. Eq. 6.

    Parametros
    ----------
    tmax_c, tmin_c : temperaturas maxima e minima do dia [degC]
    rhmax_pct, rhmin_pct : umidade relativa maxima e minima do dia [%]
    u2_ms : velocidade do vento JA CONVERTIDA para 2 m de altura [m/s]
            (usar vento_a_2m() antes, se a medicao nao for a 2 m)
    rs_mj_m2_dia : radiacao solar incidente medida [MJ m-2 dia-1]
                   (usar radiacao_solar_de_insolacao() se so houver horas de sol)
    latitude_graus : latitude do local [graus decimais, positivo = Norte, negativo = Sul]
    altitude_m : altitude do local acima do nivel do mar [m]
    dia_juliano_j : dia do ano (1-366)
    g_mj_m2_dia : fluxo de calor no solo [MJ m-2 dia-1] (0 para calculo diario, padrao FAO-56)

    Retorna
    -------
    dict com a ETo final e todas as variaveis intermediarias (para auditoria/depuracao).
    """
    tmedia = (tmax_c + tmin_c) / 2

    delta = declividade_curva_pressao_vapor(tmedia)
    gamma = constante_psicrometrica(altitude_m)

    es = pressao_vapor_saturacao_media(tmax_c, tmin_c)
    ea = pressao_vapor_atual(tmax_c, tmin_c, rhmax_pct, rhmin_pct)
    deficit_pressao_vapor = es - ea

    ra = radiacao_extraterrestre(latitude_graus, dia_juliano_j)
    rso = radiacao_ceu_limpo(ra, altitude_m)
    rns = radiacao_liquida_curta(rs_mj_m2_dia)
    rnl = radiacao_liquida_longa(tmax_c, tmin_c, ea, rs_mj_m2_dia, rso)
    rn = radiacao_liquida(rns, rnl)

    numerador_radiacao = 0.408 * delta * (rn - g_mj_m2_dia)
    numerador_aerodinamico = gamma * (900 / (tmedia + 273)) * u2_ms * deficit_pressao_vapor
    denominador = delta + gamma * (1 + 0.34 * u2_ms)

    eto = (numerador_radiacao + numerador_aerodinamico) / denominador

    return {
        "eto_mm_dia": eto,
        "tmedia_c": tmedia,
        "delta_kpa_c": delta,
        "gamma_kpa_c": gamma,
        "es_kpa": es,
        "ea_kpa": ea,
        "deficit_pressao_vapor_kpa": deficit_pressao_vapor,
        "ra_mj_m2_dia": ra,
        "rso_mj_m2_dia": rso,
        "rns_mj_m2_dia": rns,
        "rnl_mj_m2_dia": rnl,
        "rn_mj_m2_dia": rn,
        "componente_radiativo_mm_dia": numerador_radiacao / denominador,
        "componente_aerodinamico_mm_dia": numerador_aerodinamico / denominador,
    }
