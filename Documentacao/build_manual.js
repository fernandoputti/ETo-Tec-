const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, AlignmentType, PageBreak, LevelFormat,
} = require("docx");
const fs = require("fs");

const VERDE = "1B5E20";
const MARROM = "6B4A34";
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
function bullet(texto) { return new Paragraph({ text: texto, numbering: { reference: "lista-padrao", level: 0 }, spacing: { after: 80 } }); }

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

const capa = [
  new Paragraph({ spacing: { before: 2000 }, children: [] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Aspersor ETo", bold: true, size: 56, color: VERDE })], spacing: { after: 100 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Calculadora de Evapotranspiração de Referência (FAO-56 Penman-Monteith)", size: 24, color: MARROM })], spacing: { after: 200 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Manual de Instalação e Uso", size: 32, color: MARROM })], spacing: { after: 600 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Versão 1.0 — 15/08/2026", size: 22 })], spacing: { after: 100 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Universidade Estadual Paulista (UNESP)", size: 22 })], spacing: { after: 40 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Universidade do Oeste Paulista (UNOESTE)", size: 22 })], spacing: { after: 40 } }),
  new Paragraph({ children: [new PageBreak()] }),
];

const doc = new Document({
  numbering: { config: [{ reference: "lista-padrao", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 480, hanging: 260 } } } }] }] },
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 30, bold: true, color: VERDE }, paragraph: { spacing: { before: 320, after: 160 } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, color: MARROM }, paragraph: { spacing: { before: 240, after: 120 } } },
    ],
  },
  sections: [{
    properties: {},
    children: [
      ...capa,

      h1("1. Introdução"),
      p("Aspersor ETo é um software para cálculo da evapotranspiração de referência (ETo) diária pelo método padrão internacional FAO Penman-Monteith, conforme o FAO Irrigation and Drainage Paper No. 56 (Allen et al., 1998). A ETo indica a demanda hídrica de referência da atmosfera sobre uma cultura hipotética de referência, sendo a base para o cálculo da lâmina de irrigação de culturas reais (ETc = ETo × Kc)."),
      p("O programa está disponível em três formas de uso:"),
      tabela([3400, 6100], [
        ["Variante", "Descrição"],
        ["AspersorETo.exe", "Aplicativo desktop para Windows, executável standalone com interface gráfica"],
        ["index.html", "Mesma interface gráfica, executada em um navegador web"],
        ["calcular_eto.py", "Processamento em lote via linha de comando, para vários dias de uma vez a partir de uma planilha CSV"],
      ]),

      h1("2. Requisitos do Sistema"),
      h2("2.1 Versão Desktop (.exe)"),
      bullet("Windows 10 ou 11 (64 bits)."),
      bullet("Não é necessário instalar Python: o executável é autossuficiente."),
      h2("2.2 Versão Web (navegador)"),
      bullet("Navegador atualizado: Chrome, Edge ou Firefox."),
      h2("2.3 Versão linha de comando (processamento em lote)"),
      bullet("Python 3.9 ou superior instalado."),
      bullet("Nenhuma biblioteca externa é necessária (usa apenas a biblioteca padrão do Python)."),

      h1("3. Instalação"),
      h2("3.1 Versão Desktop (.exe)"),
      bullet("Copie o arquivo AspersorETo.exe para o computador e dê duplo clique — não há instalação."),
      bullet("Se o Windows exibir o aviso do SmartScreen, clique em \"Mais informações\" e depois em \"Executar assim mesmo\"."),
      h2("3.2 Versão Web"),
      bullet("Abra o arquivo index.html diretamente no navegador, ou acesse a página publicada do projeto."),
      h2("3.3 Versão linha de comando"),
      bullet("Copie os arquivos eto_penman_monteith.py e calcular_eto.py para a mesma pasta."),
      bullet("Rode: python calcular_eto.py --entrada dados.csv --saida resultado.csv --latitude <lat> --altitude <m> --altura-vento <m>"),

      h1("4. Utilização"),
      h2("4.1 Interface gráfica (desktop ou web)"),
      p("Campos solicitados:"),
      tabela([2600, 6900], [
        ["Campo", "Descrição"],
        ["Data", "Data da medição, usada para calcular a posição solar (dia do ano)"],
        ["Latitude (°)", "Latitude do local, em graus decimais (positivo = Norte, negativo = Sul)"],
        ["Altitude (m)", "Altitude do local acima do nível do mar"],
        ["Tmáx / Tmín (°C)", "Temperatura máxima e mínima do dia"],
        ["UR máx / UR mín (%)", "Umidade relativa máxima e mínima do dia"],
        ["Vento (m/s)", "Velocidade do vento, medida na altura informada em \"Altura anem.\""],
        ["Altura anem. (m)", "Altura de medição do anemômetro. O programa converte automaticamente para 2 m (padrão FAO-56) quando diferente"],
        ["Rs (MJ/m²/dia)", "Radiação solar incidente medida"],
      ]),
      p("Fórmula aplicada (FAO-56, Equação 6):"),
      p("ETo = [0,408·Δ·(Rn−G) + γ·(900/(T+273))·u2·(es−ea)] / [Δ + γ·(1 + 0,34·u2)]", { font: "Consolas", size: 20 }),
      p("Exemplo validado (Exemplo 18 do FAO-56 — Uccle, Bruxelas, 50°48'N, 100 m, 6 de julho): Tmáx = 21,5 °C; Tmín = 12,3 °C; URmáx = 84%; URmín = 63%; vento = 10 km/h medido a 10 m; Rs = 22,07 MJ/m²/dia → ETo = 3,88 mm/dia (documento oficial: \"≈ 3,9\"). Esse mesmo caso pode ser carregado na interface pelo botão \"Exemplo FAO-56\"."),
      p("O resultado é apresentado em mm/dia (equivalente a litros por metro quadrado por dia) e, ao abrir \"Ver variáveis intermediárias do cálculo\", também em todas as variáveis do modelo (Δ, γ, es, ea, Ra, Rso, Rns, Rnl, Rn, u2)."),

      h2("4.2 Uso em lote (linha de comando)"),
      p("O arquivo de entrada é um CSV com as colunas: data;tmax;tmin;rhmax;rhmin;vento_ms;rs_mj_m2_dia (separador \";\" ou \",\"; aceita vírgula ou ponto como separador decimal). O arquivo dados_exemplo.csv traz um modelo pronto, incluindo o Exemplo 18 do FAO-56 como uma das linhas, para conferência. O comando gera um CSV de saída com a ETo de cada dia e um resumo (mínima, máxima, média e acumulada do período) no terminal."),

      h1("5. Mensagens do Sistema"),
      tabela([3800, 5700], [
        ["Mensagem", "Significado / o que fazer"],
        ["\"Tmín não pode ser maior que Tmáx.\"", "As temperaturas foram trocadas ou digitadas incorretamente."],
        ["\"UR mín não pode ser maior que UR máx.\"", "As umidades relativas foram trocadas ou digitadas incorretamente."],
        ["\"Umidade relativa deve estar entre 0 e 100%.\"", "Um dos valores de UR está fora da faixa válida."],
        ["\"Velocidade do vento não pode ser negativa.\"", "Verifique o valor informado."],
        ["\"Radiação solar não pode ser negativa.\"", "Verifique o valor informado."],
        ["\"Latitude deve estar entre −90 e 90.\"", "A latitude foi digitada incorretamente."],
      ]),

      h1("6. Referência Bibliográfica"),
      p("ALLEN, R. G.; PEREIRA, L. S.; RAES, D.; SMITH, M. Crop evapotranspiration — Guidelines for computing crop water requirements. Rome: FAO, 1998. (FAO Irrigation and Drainage Paper, 56)."),

      h1("7. Autoria e Suporte"),
      p("Titular: Fernando Ferrari Putti — Universidade Estadual Paulista (UNESP)."),
      p("Coautoria: Jéssica Pigatto de Queiroz Barcelos — Universidade do Oeste Paulista (UNOESTE)."),
    ],
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("Manual_Instalacao_Uso_ETo-Tec.docx", buffer);
  console.log("Manual (ETo) gerado com sucesso.");
});
