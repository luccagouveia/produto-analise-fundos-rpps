# Projeto Técnico: Análise de Fundos Previdenciários (RPPS)

  # Visão Geral
    
    # Este projeto realiza a análise técnica e atuarial dos dados cadastrais de servidores públicos vinculados ao Regime Próprio de Previdência Social (RPPS) do Município de São Paulo, com base nos critérios legais estabelecidos pelos seguintes normativos:

      # Decreto nº 61.151, de 18 de março de 2022
          - Dispõe sobre o custeio do RPPS, a adesão ao Regime de Previdência Complementar (RPC) e a segregação de massas entre os fundos FUNPREV (capitalização) e FUNFIN (repartição simples). 

      # Decreto nº 64.144, de 1º de abril de 2025
          - Altera o decreto anterior, atualizando critérios de elegibilidade e instituindo contribuições extraordinárias patronais escalonadas ao FUNFIN, com vigência até abril de 2029.

  # Objetivo do Script
    # O script principal realiza:

      1. Classificação do fundo previdenciário (CALCULO_FUNDO) com base em:

          - Data de ingresso no ente (DT_ING_ENTE)
          - Data de nascimento (DT_NASC_SERVIDOR)
          - Indicador de previdência complementar (IN_PREV_COMP)

      2. Verificação de compatibilidade (COMPATIBILIDADE_FUNDO) entre o fundo informado (CO_TIPO_FUNDO) e o fundo calculado.

      3. Identificação de duplicidade de CPF (CPF_DUPLICADO) para controle de registros.

      4. Classificação em cenários (CENARIO_FUNDO):

        - Cenário 1: incompatível e CPF único
        - Cenário 2: incompatível, CPF duplicado e situação funcional = 1
        - Cenário 3: incompatível, CPF duplicado e situação funcional ≠ 1

  # Estrutura do Projeto

    analise_fundos_rpps/
      ├── dados/                        # Arquivos de entrada (.xlsx)
      │   └── SERVIDOR.xlsx
      ├── resultados/                   # Arquivos gerados após análise
      │   ├── SERVIDOR_resultado.xlsx
      │   └── SERVIDOR_analise_exploratoria.txt
      ├── scripts/                      # Scripts de análise
      │   ├── analise_fundos.py         # Script principal
      │   └── analise_exploratoria.py   # Script estatístico
      ├── requirements.txt              # Dependências
      └── README.md                     # Documentação técnica

  # Requisitos Técnicos
    - Python 3.10+
    - Visual Studio Code ou terminal
    - Bibliotecas:
      - pandas
      - openpyxl

        Instalação:
          pip install -r requirements.txt

  # Execução

    1. Preparar o ambiente
      Coloque o arquivo SERVIDOR.xlsx na pasta dados/.

    2. Executar a análise dos fundos
      - python scripts/analise_fundos.py

    3. Executar a análise exploratória
      - python scripts/analise_exploratoria.py

    ## Gera o arquivo SERVIDOR_analise_exploratoria.txt com:

      Gera o arquivo SERVIDOR_analise_exploratoria.txt com:

        - Contagens por fundo, órgão, cargo, sexo, estado civil, situação funcional
        - Estatísticas de idade e idade de ingresso
        - Verificações de valores abaixo do salário mínimo e acima do teto
        - Indicadores de abono de permanência e previdência complementar
        - Resumo estatístico de variáveis numéricas

    4. Verificar os resultados
      Os arquivos gerados estarão na pasta resultados/.

        ## Campos Gerados
          O arquivo SERVIDOR_resultado.xlsx contém:

          - ID_SERVIDOR_MATRICULA
          - ID_SERVIDOR_CPF
          - CO_TIPO_FUNDO
          - NO_ORGAO
          - CO_SITUACAO_FUNCIONAL
          - VL_CONTRIBUICAO
          - DT_ING_ENTE
          - DT_NASC_SERVIDOR
          - IN_PREV_COMP
          - CPF_DUPLICADO
          - CALCULO_FUNDO
          - COMPATIBILIDADE_FUNDO
          - CENARIO_FUNDO

   # Lógica de Classificação
    FUNFIN (2): servidor admitido até 27/12/2018, nascido após 28/02/1957, e não aderiu ao RPC.
    FUNPREV (1): servidor admitido após 27/12/2018, ou nascido até 28/02/1957, ou aderiu ao RPC.

  # Vocabulários Técnicos
    Os códigos são traduzidos conforme os seguintes vocabulários:

      CO_TIPO_FUNDO
        Código	Descrição
          1	FUNPREV
          2	FUNFIN
          3	Mantidos pelo Tesouro
          9	Não consta

      CO_TIPO_CARGO
        Código	Descrição
          1	Magistrados, Membros do MP ou TC
          2	Professores da Educação Básica
          3	Professores do Ensino Superior
          4	Policiais Civis
          5	Agente Penitenciário
          6	Guarda Municipal
          7	Demais Servidores

      CO_SEXO_SERVIDOR
        Código	Sexo
          1	Feminino
          2	Masculino

      CO_EST_CIVIL_SERVIDOR
        Código	Estado Civil
          1	Solteiro(a)
          2	Casado(a)
          3	Viúvo(a)
          4	Separado(a) judicialmente
          5	Divorciado(a)
          6	União estável
          9	Outros

      CO_SITUACAO_FUNCIONAL
        Código	Situação
          1	Em Exercício
          2	Licenciado(a) com Remuneração
          3	Licenciado(a) sem Remuneração
          4	Cedido(a) com Ônus
          5	Cedido(a) sem Ônus
          6	Requisitado(a) com Ônus
          7	Requisitado(a) sem Ônus
          8	Em Disponibilidade
          9	Afastado Mandato Eletivo
          10	Recluso ou Detido
          11	Outros

  # Interpretação dos Resultados

    Os cenários ajudam a identificar inconsistências cadastrais e orientar ajustes.
    O relatório exploratório fornece uma visão geral da base e possíveis anomalias.
    O resumo estatístico permite identificar padrões e outliers em variáveis financeiras e demográficas.
    Os dados podem ser utilizados para validação atuarial junto ao IPREM.
