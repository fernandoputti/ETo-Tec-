# Aspersor ETo

Software para cálculo da evapotranspiração de referência (ETo) diária pelo
método padrão internacional **FAO Penman-Monteith**, conforme o FAO Irrigation
and Drainage Paper No. 56 (Allen et al., 1998).

**Titular:** Fernando Ferrari Putti — Universidade Estadual Paulista (UNESP)
**Coautoria:** Jéssica Pigatto de Queiroz Barcelos — Universidade do Oeste Paulista (UNOESTE)

Documentação completa (manual de instalação/uso e memorial descritivo)
em [`Documentacao/`](Documentacao/).

## Estrutura

```
index.html                    interface gráfica (web e desktop) - HTML/CSS/JS autocontido
eto_penman_monteith.py        motor de cálculo (Python) - todas as equações do FAO-56
calcular_eto.py                CLI - processa um CSV com vários dias de dados meteorológicos
validar_fao56_exemplo18.py    auditoria - reproduz o Exemplo 18 oficial do FAO-56
dados_exemplo.csv             modelo de planilha de entrada
aspersor_eto_app.py           lançador desktop (pywebview) - abre index.html numa janela nativa
assets/                       logos institucionais (UNESP, UNOESTE)
Documentacao/                 Manual de Instalação e Uso + Memorial Descritivo (INPI)
```

## Validação

A implementação em Python é auditada contra o **Exemplo 18** do FAO-56 (caso-teste
oficial da FAO): 11/11 variáveis intermediárias e a ETo final batem com o
documento original dentro da tolerância de arredondamento (`ETo = 3,88 mm/dia`,
documento oficial: "≈ 3,9"). O script inclui também um controle negativo
(comparação contra valores propositalmente errados) para confirmar que o teste
realmente detecta divergência.

```bash
python validar_fao56_exemplo18.py
```

A implementação em JavaScript (usada em `index.html`) foi cruzada com a
versão Python via Node.js — mesmo resultado até a 3ª casa decimal.

## Rodar a versão desktop a partir do código-fonte

```bash
pip install pywebview
python aspersor_eto_app.py
```

## Gerar o executável Windows (.exe)

```bash
pip install pywebview pyinstaller
pyinstaller --onefile --windowed --name AspersorETo --add-data "index.html;." aspersor_eto_app.py
```

O executável é gerado em `dist/AspersorETo.exe`. Ou simplesmente rode
`gerar_exe.bat`.

## Uso em lote (linha de comando)

```bash
python calcular_eto.py --entrada dados_exemplo.csv --saida eto_resultado.csv --latitude 50.8 --altitude 100 --altura-vento 10
```

CSV de entrada: colunas `data;tmax;tmin;rhmax;rhmin;vento_ms;rs_mj_m2_dia`
(radiação solar **medida** — sem fallback por horas de insolação nesta versão).

## Fórmula implementada (FAO-56, Equação 6)

```
ETo = [0,408·Δ·(Rn−G) + γ·(900/(T+273))·u2·(es−ea)] / [Δ + γ·(1 + 0,34·u2)]
```

## Referência bibliográfica

ALLEN, R. G.; PEREIRA, L. S.; RAES, D.; SMITH, M. Crop evapotranspiration —
Guidelines for computing crop water requirements. Rome: FAO, 1998.
(FAO Irrigation and Drainage Paper, 56).
