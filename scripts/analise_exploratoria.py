import os
import pandas as pd
from datetime import datetime

# === CONFIGURAÇÕES ===
ARQUIVO_ENTRADA = "dados/SERVIDOR.xlsx"
NOME_ABA = "SERVIDOR"
DATA_CORTE = datetime(2025, 9, 1)
SALARIO_MINIMO = 1631

# === GARANTIR PASTA DE RESULTADOS ===
os.makedirs("resultados", exist_ok=True)

# === CARREGAR DADOS ===
df = pd.read_excel(ARQUIVO_ENTRADA, sheet_name=NOME_ABA, engine="openpyxl")

# === DICIONÁRIOS DE VOCABULÁRIOS ===
vocab_fundo = {
    1: "FUNPREV",
    2: "FUNFIN",
    3: "Mantidos pelo Tesouro",
    9: "Não consta"
}

vocab_cargo = {
    1: "Magistrados, Membros do Min. Público ou de Tribunal de Contas",
    2: "Professores da Educ. Infantil e do Ensino Fund. e Médio",
    3: "Professores do Ensino Superior",
    4: "Policiais Civis (Federais, Distritais ou Estaduais)",
    5: "Agente Penitenciário",
    6: "Guarda Municipal",
    7: "Demais Servidores"
}

vocab_sexo = {
    1: "feminino",
    2: "masculino",

}

vocab_estado_civil = {
    1: "solteiro(a)",
    2: "casado(a)",
    3: "viúvo(a)",
    4: "separado(a) judicialmente",
    5: "divorciado(a)",
    6: "união estável",
    9: "outros"
}

vocab_situacao_funcional = {
    1: "Em Exercício",
    2: "Licenciado(a) com Remuneração",
    3: "Licenciado(a) sem Remuneração",
    4: "Cedido(a) com Ônus",
    5: "Cedido(a) sem Ônus",
    6: "Requisitado(a) com Ônus",
    7: "Requisitado(a) sem Ônus",
    8: "Em Disponibilidade",
    9: "Afastado Mandato Eletivo",
    10: "Recluso ou Detido",
    11: "Outros"
}

# === MAPEAR CÓDIGOS PARA DESCRIÇÕES ===
df['CO_TIPO_FUNDO'] = df['CO_TIPO_FUNDO'].map(vocab_fundo)
df['CO_TIPO_CARGO'] = df['CO_TIPO_CARGO'].map(vocab_cargo)
df['CO_SEXO_SERVIDOR'] = df['CO_SEXO_SERVIDOR'].map(vocab_sexo)
df['CO_EST_CIVIL_SERVIDOR'] = df['CO_EST_CIVIL_SERVIDOR'].map(vocab_estado_civil)
df['CO_SITUACAO_FUNCIONAL'] = df['CO_SITUACAO_FUNCIONAL'].map(vocab_situacao_funcional)

# === CÁLCULOS DE IDADE ===
df['IDADE'] = (DATA_CORTE - pd.to_datetime(df['DT_NASC_SERVIDOR'], errors='coerce')).dt.days // 365
df['IDADE_ING_SERV_PUB'] = (pd.to_datetime(df['DT_ING_SERV_PUB'], errors='coerce') - pd.to_datetime(df['DT_NASC_SERVIDOR'], errors='coerce')).dt.days // 365
df['IDADE_ING_ENTE'] = (pd.to_datetime(df['DT_ING_ENTE'], errors='coerce') - pd.to_datetime(df['DT_NASC_SERVIDOR'], errors='coerce')).dt.days // 365
# === VERIFICAÇÕES ESPECÍFICAS ===
ingresso_serv_pub_menor_18 = df[df['IDADE_ING_SERV_PUB'] < 18]
ingresso_ente_menor_18 = df[df['IDADE_ING_ENTE'] < 18]
base_abaixo_minimo = df[df['VL_BASE_CALCULO'] < SALARIO_MINIMO]
base_acima_teto = df[df['VL_BASE_CALCULO'] > df['VL_TETO_ESPECIFICO']]
remuneracao_abaixo_minimo = df[df['VL_REMUNERACAO'] < SALARIO_MINIMO]
remuneracao_acima_teto = df[df['VL_REMUNERACAO'] > df['VL_TETO_ESPECIFICO']]

# === CONTAGENS E ESTATÍSTICAS ===
resultado = {
    "Total de linhas": len(df),
    "Servidores por fundo": df['CO_TIPO_FUNDO'].value_counts().rename_axis('Fundo').reset_index(name='Contagem'),
    "Servidores por órgão": df['NO_ORGAO'].value_counts().rename_axis('Órgão').reset_index(name='Contagem'),
    "Servidores por tipo de cargo": df['CO_TIPO_CARGO'].value_counts().rename_axis('Cargo').reset_index(name='Contagem'),
    "CPFs duplicados": df['ID_SERVIDOR_CPF'].duplicated().sum(),
    "Servidores por sexo": df['CO_SEXO_SERVIDOR'].value_counts().rename_axis('Sexo').reset_index(name='Contagem'),
    "Servidores por estado civil": df['CO_EST_CIVIL_SERVIDOR'].value_counts().rename_axis('Estado Civil').reset_index(name='Contagem'),
    "Servidores por situação funcional": df['CO_SITUACAO_FUNCIONAL'].value_counts().rename_axis('Situação').reset_index(name='Contagem'),
    "Faixas de idade": df['IDADE'].describe(),
    "Faixas de idade de ingresso no serviço público": df['IDADE_ING_SERV_PUB'].describe(),
    "Ingressos no serviço público com menos de 18 anos": len(ingresso_serv_pub_menor_18),
    "Faixas de idade de ingresso no ente": df['IDADE_ING_ENTE'].describe(),
    "Ingressos no ente com menos de 18 anos": len(ingresso_ente_menor_18),
    "Base de cálculo abaixo do mínimo": len(base_abaixo_minimo),
    "Base de cálculo acima do teto": len(base_acima_teto),
    "Remuneração abaixo do mínimo": len(remuneracao_abaixo_minimo),
    "Remuneração acima do teto": len(remuneracao_acima_teto),
    "Abono de permanência (Sim)": df[df['IN_ABONO_PERMANENCIA'] == 1].shape[0],
    "Abono de permanência (Não)": df[df['IN_ABONO_PERMANENCIA'] == 2].shape[0],
    "Previdência complementar (Sim)": df[df['IN_PREV_COMP'] == 1].shape[0],
    "Previdência complementar (Não)": df[df['IN_PREV_COMP'] == 2].shape[0]
}

# === SALVAR RESULTADOS EM TXT ===
with open("resultados/SERVIDOR_analise_exploratoria.txt", "w", encoding="utf-8") as f:
    for chave, valor in resultado.items():
        f.write(f"{chave}:\n")
        if isinstance(valor, pd.DataFrame) or isinstance(valor, pd.Series):
            f.write(valor.to_string())
        else:
            f.write(str(valor))
        f.write("\n" + "-"*60 + "\n")

# === EXIBIR RESULTADOS NO TERMINAL ===
for chave, valor in resultado.items():
    print(f"{chave}:")
    print(valor)
    print("\n" + "-"*60 + "\n")

print("Análise exploratória concluída. Resultados salvos em 'resultados/SERVIDOR_analise_exploratoria.txt'.")
