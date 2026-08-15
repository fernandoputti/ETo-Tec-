const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, AlignmentType, PageBreak, LevelFormat,
  ImageRun,
} = require("docx");
const fs = require("fs");

const VERDE = "1B5E20";
const MARROM = "6B4A34";
const AZUL = "0B6E8F";
const CINZA_BORDA = "CCCCCC";

const cellBorders = {
  top: { style: BorderStyle.SINGLE, size: 4, color: CINZA_BORDA },
  bottom: { style: BorderStyle.SINGLE, size: 4, color: CINZA_BORDA },
  left: { style: BorderStyle.SINGLE, size: 4, color: CINZA_BORDA },
  right: { style: BorderStyle.SINGLE, size: 4, color: CINZA_BORDA },
};

function h1(texto) { return new Paragraph({ text: texto, heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 } }); }
function h2(texto) { return new Paragraph({ text: texto, heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 } }); }
function p(texto, opts = {}) { return new Paragraph({ children: [new TextRun({ text: texto, ...opts })], spacing: { after: 160 } }); }
function codigo(linhas) {
  return linhas.map((linha) => new Paragraph({ children: [new TextRun({ text: linha.length ? linha : " ", font: "Consolas", size: 16 })], spacing: { after: 0 } }));
}
function celula(texto, opts = {}) {
  return new TableCell({
    width: opts.width ? { size: opts.width, type: WidthType.DXA } : undefined,
    shading: opts.header ? { type: ShadingType.CLEAR, fill: VERDE } : undefined,
    borders: cellBorders,
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text: texto, bold: !!opts.header, color: opts.header ? "FFFFFF" : undefined, size: 20 })] })],
  });
}
function tabela(colWidths, linhas) {
  return new Table({
    width: { size: colWidths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: colWidths,
    rows: linhas.map((linha, i) => new TableRow({ children: linha.map((texto, j) => celula(texto, { width: colWidths[j], header: i === 0 })) })),
  });
}

const CALC_INICIO = [
'"""',
"Calculo da evapotranspiracao de referencia (ETo) pelo metodo padrao",
"FAO Penman-Monteith (FAO Irrigation and Drainage Paper No. 56, Allen et al. 1998).",
"",
"Todas as equacoes seguem a numeracao e as unidades do Capitulo 3 e 4 do FAO-56:",
"  - Temperatura: graus Celsius",
"  - Umidade relativa: %",
"  - Vento: m/s",
"  - Radiacao: MJ m-2 dia-1",
"  - Pressao de vapor: kPa",
"  - ETo: mm/dia",
'"""',
"",
"import math",
];

const CALC_FIM = [
"    eto = (numerador_radiacao + numerador_aerodinamico) / denominador",
"",
"    return {",
'        "eto_mm_dia": eto,',
'        "tmedia_c": tmedia,',
'        "delta_kpa_c": delta,',
'        "gamma_kpa_c": gamma,',
'        "es_kpa": es,',
'        "ea_kpa": ea,',
"        ...",
'        "rn_mj_m2_dia": rn,',
"    }",
];

const APP_INICIO = [
'"""',
"Lançador desktop do Aspersor ETo (calculadora de evapotranspiração de referência,",
"FAO-56 Penman-Monteith) - abre index.html numa janela nativa usando pywebview.",
'"""',
"",
"import os",
"import sys",
"",
"import webview",
];

const APP_FIM = [
"def main():",
'    html_path = caminho_recurso("index.html")',
"    webview.create_window(",
'        "Aspersor ETo — Evapotranspiração FAO-56 Penman-Monteith",',
"        html_path, width=1150, height=820, min_size=(820, 640),",
"    )",
"    webview.start()",
];

const JS_INICIO = [
"<script>",
"(function () {",
'  "use strict";',
"",
"  var GSC = 0.0820;",
"  var SIGMA = 4.903e-9;",
"  var ALBEDO = 0.23;",
"",
"  function esT(t) { return 0.6108 * Math.exp((17.27 * t) / (t + 237.3)); }",
];

const JS_FIM = [
"  // calcula automaticamente com os valores do Exemplo FAO-56 ao carregar",
"  form.requestSubmit();",
"})();",
"</script>",
];

const capa = [
  new Paragraph({ spacing: { before: 1400 }, children: [] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "MEMORIAL DESCRITIVO", bold: true, size: 44, color: VERDE })], spacing: { after: 200 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Registro de Programa de Computador — INPI", size: 24, color: MARROM })], spacing: { after: 600 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Aspersor ETo", bold: true, size: 36 })], spacing: { after: 100 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Calculadora de Evapotranspiração de Referência (FAO-56 Penman-Monteith)", size: 24, color: MARROM })], spacing: { after: 600 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Titular: Fernando Ferrari Putti — UNESP", size: 22 })], spacing: { after: 80 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Coautoria: Jéssica Pigatto de Queiroz Barcelos — UNOESTE", size: 22 })], spacing: { after: 80 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Data de criação: 15/08/2026", size: 22 })], spacing: { after: 80 } }),
  new Paragraph({ children: [new PageBreak()] }),
];

const doc = new Document({
  numbering: { config: [{ reference: "lista-padrao", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 480, hanging: 260 } } } }] }] },
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 28, bold: true, color: VERDE }, paragraph: { spacing: { before: 320, after: 160 } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, color: MARROM }, paragraph: { spacing: { before: 240, after: 120 } } },
    ],
  },
  sections: [{
    properties: {},
    children: [
      ...capa,

      h1("1. Identificação do Programa"),
      tabela([3200, 6300], [
        ["Campo", "Descrição"],
        ["Título do programa", "Aspersor ETo — Calculadora de Evapotranspiração de Referência (FAO-56 Penman-Monteith)"],
        ["Titular", "Fernando Ferrari Putti — Universidade Estadual Paulista (UNESP)"],
        ["Coautoria", "Jéssica Pigatto de Queiroz Barcelos — Universidade do Oeste Paulista (UNOESTE)"],
        ["Data de criação", "15/08/2026"],
        ["Linguagens de programação", "Python 3.14 (motor de cálculo, processamento em lote e validação); HTML5, CSS3 e JavaScript ES6+ (interface gráfica e versão web); pywebview e PyInstaller (empacotamento desktop)"],
        ["Tipo de programa", "Aplicativo utilitário científico (calculadora de evapotranspiração de referência para manejo de irrigação)"],
        ["Campo de aplicação", "Agronomia — Agrometeorologia, Irrigação e Drenagem"],
        ["Ambiente operacional", "Windows 10/11 (executável standalone) e navegadores web modernos (Chrome, Edge, Firefox)"],
        ["Algoritmo/decisão", "Determinístico: aplica a equação fechada de Penman-Monteith (FAO-56) sobre os dados meteorológicos informados"],
      ]),

      h1("2. Resumo / Descrição Geral"),
      p("Aspersor ETo é um software para cálculo da evapotranspiração de referência (ETo) diária pelo método padrão internacional FAO Penman-Monteith, conforme o FAO Irrigation and Drainage Paper No. 56 (Allen et al., 1998). Recebe dados meteorológicos diários — temperatura máxima e mínima, umidade relativa máxima e mínima, velocidade do vento, radiação solar incidente medida, latitude, altitude e data — e calcula a ETo em milímetros por dia, apresentando também as variáveis intermediárias do modelo (declividade da curva de pressão de vapor, constante psicrométrica, pressões de vapor de saturação e atual, radiação extraterrestre, radiação líquida, entre outras) para fins de conferência e uso didático."),
      p("O programa está disponível em três formas de uso, com a mesma equação implementada de forma independente em duas linguagens (Python e JavaScript) e cruzada entre si: (1) módulo Python para uso em lote via linha de comando, processando arquivos de dados meteorológicos diários e gerando a ETo para cada dia; (2) interface gráfica interativa (HTML/JavaScript), com ilustração animada de um aspersor irrigando uma planta de milho cuja intensidade reflete o valor de ETo calculado; (3) aplicativo desktop standalone para Windows, empacotando a mesma interface gráfica numa janela nativa."),

      h1("3. Descrição Funcional"),
      p("O usuário informa a data, a localização (latitude e altitude), a temperatura do ar (máxima e mínima), a umidade relativa (máxima e mínima), a velocidade do vento — e a altura de medição do anemômetro, quando diferente de 2 m — e a radiação solar incidente medida. O programa valida os dados informados, calcula as variáveis termodinâmicas (declividade da curva de pressão de vapor de saturação, constante psicrométrica, pressões de vapor de saturação e atual, déficit de pressão de vapor), as variáveis de radiação (radiação extraterrestre a partir da latitude e do dia do ano, radiação em céu limpo, radiação líquida de onda curta e de onda longa, radiação líquida total) e converte a velocidade do vento para a altura padrão de 2 metros, quando necessário. Em seguida aplica a equação de Penman-Monteith e apresenta a ETo em milímetros por dia (equivalente a litros por metro quadrado por dia), junto das variáveis intermediárias."),

      h1("4. Fundamentação Científica"),
      p("ALLEN, R. G.; PEREIRA, L. S.; RAES, D.; SMITH, M. Crop evapotranspiration — Guidelines for computing crop water requirements. Rome: FAO, 1998. (FAO Irrigation and Drainage Paper, 56)."),

      h1("5. Validação e Auditoria da Implementação"),
      p("A implementação em Python foi conferida integralmente contra o \"Example 18\" do FAO Irrigation and Drainage Paper No. 56 — o caso-teste numérico oficial do método, publicado pela FAO (localidade de Uccle, Bruxelas, 50°48'N, 6 de julho). As 11 variáveis intermediárias do modelo (Δ, γ, es, ea, déficit de pressão de vapor, Ra, N, Rs, Rns, Rnl, Rn) e a ETo final coincidem com os valores oficiais dentro da tolerância de arredondamento do documento fonte (ETo calculado = 3,88 mm/dia; documento oficial: \"≈ 3,9\"), com controle positivo (100% das variáveis dentro da tolerância) e controle negativo — comparação da mesma implementação contra valores propositalmente incorretos, confirmando que o teste de validação de fato detecta divergência quando ela existe (0% de acerto)."),
      p("A implementação em JavaScript, usada na interface gráfica, foi cruzada com a implementação em Python (mesmos dados de entrada) via execução em ambiente Node.js, com resultado idêntico até a terceira casa decimal — não se trata de uma reimplementação independente, mas da mesma equação portada e conferida entre as duas linguagens."),

      h1("6. Arquitetura e Tecnologias Utilizadas"),
      tabela([3400, 6100], [
        ["Componente", "Tecnologia"],
        ["Motor de cálculo (núcleo)", "Python 3.14 — módulo eto_penman_monteith.py, funções puras independentes de interface"],
        ["Processamento em lote (CLI)", "Python — módulo calcular_eto.py, lê um CSV de dados diários e gera a ETo de cada dia"],
        ["Auditoria e validação", "Python — módulo validar_fao56_exemplo18.py, reproduz o Exemplo 18 do FAO-56 com controle positivo e negativo"],
        ["Interface gráfica (web e desktop)", "HTML5, CSS3 e JavaScript ES6+ — arquivo index.html; mesma equação portada e cruzada com a versão Python"],
        ["Empacotamento desktop", "pywebview (janela nativa) e PyInstaller (executável standalone .exe) — módulo aspersor_eto_app.py"],
        ["Visualização", "Ilustração SVG animada (aspersor e planta de milho), com intensidade proporcional à ETo calculada"],
      ]),

      h1("7. Fluxograma de Funcionamento"),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new ImageRun({ type: "png", data: fs.readFileSync("fluxograma.png"), transformation: { width: 380, height: 523 } })],
        spacing: { after: 200 },
      }),

      h1("8. Trechos do Programa-Fonte (representativos)"),
      p("Os trechos a seguir correspondem às linhas iniciais e finais dos três arquivos de código-fonte principais do programa, apresentados para fins de caracterização de autoria e originalidade, conforme praxe do INPI. O código-fonte completo será apresentado em anexo ao processo de registro, conforme exigido."),

      h2("8.1 eto_penman_monteith.py (motor de cálculo)"),
      ...codigo(CALC_INICIO), p("(...)", { italics: true }), ...codigo(CALC_FIM),

      h2("8.2 aspersor_eto_app.py (lançador desktop)"),
      ...codigo(APP_INICIO), p("(...)", { italics: true }), ...codigo(APP_FIM),

      h2("8.3 index.html — bloco <script> (cálculo e interface web)"),
      ...codigo(JS_INICIO), p("(...)", { italics: true }), ...codigo(JS_FIM),
    ],
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("Memorial_Descritivo_ETo-Tec.docx", buffer);
  console.log("Memorial (ETo) gerado com sucesso.");
});
