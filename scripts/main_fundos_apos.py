import pandas as pd
from datetime import datetime
import os

# === CONFIGURAÇÕES DINÂMICAS ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(BASE_DIR, "..", "dados")
PASTA_RESULTADOS = os.path.join(BASE_DIR, "..", "resultados")
ARQUIVO_SAIDA_EXCEL = os.path.join(PASTA_RESULTADOS, "APOSENTADOS_resultado.xlsx")
ARQUIVO_SAIDA_TXT = os.path.join(PASTA_RESULTADOS, "APOSENTADOS_resumo_analise.txt")

# === GARANTIR PASTA DE RESULTADOS ===
os.makedirs(PASTA_RESULTADOS, exist_ok=True)

# === SELECIONAR ARQUIVO DE ENTRADA ===
arquivos = [f for f in os.listdir(PASTA_DADOS) if "aposentado" in f.lower() and f.lower().endswith(".xlsx")]
if not arquivos:
    raise FileNotFoundError("Nenhum arquivo contendo 'aposentado' encontrado na pasta de dados.")

arquivos.sort(key=lambda f: os.path.getmtime(os.path.join(PASTA_DADOS, f)), reverse=True)
ARQUIVO_ENTRADA = os.path.join(PASTA_DADOS, arquivos[0])
print(f"Arquivo selecionado: {ARQUIVO_ENTRADA}")

# === SELECIONAR ABA AUTOMATICAMENTE ===
abas = pd.ExcelFile(ARQUIVO_ENTRADA, engine="openpyxl").sheet_names
aba_selecionada = next((aba for aba in abas if "aposentado" in aba.lower()), abas[0])
print(f"Aba selecionada: {aba_selecionada}")

# === DATAS DE CORTE ===
DATA_CORTE_ENTE = datetime(2018, 12, 27)
DATA_CORTE_NASC = datetime(1957, 2, 28)

# === CARREGAR DADOS ===
df = pd.read_excel(ARQUIVO_ENTRADA, sheet_name=aba_selecionada, engine="openpyxl")

# Padronizar coluna
if "DATA DE INGRESSO NO ENTE" in df.columns:
    df.rename(columns={"DATA DE INGRESSO NO ENTE": "DT_ING_ENTE"}, inplace=True)

# === DICIONÁRIOS ===
vocab_fundo = {1: "FUNPREV", 2: "FUNFIN", 3: "Mantidos pelo Tesouro", 9: "Não consta"}
vocab_prev_comp = {1: "Sim", 2: "Não"}
vocab_tipo_aposentadoria = {
    1: "Aposentadoria por Idade",
    2: "Aposentadoria por Tempo de Contribuição",
    3: "Aposentadoria Compulsória",
    4: "Aposentadoria por Invalidez",
    5: "Aposentadoria como Professor",
    6: "Aposentadoria Especial - atividade de risco (Art. 40, § 4º, inc. II, CF)",
    7: "Aposentadoria Especial - atividade prejudiciais à saúde ou integridade física (Art. 40, § 4º, inc. III, CF)",
    9: "Militares Inativos - Reserva Remunerada",
    10: "Militares Inativos - Reforma"
}

# === CONVERSÃO DE DATAS ===
df['DT_ING_ENTE'] = pd.to_datetime(df['DT_ING_ENTE'], errors='coerce')
df['DT_NASC_APOSENTADO'] = pd.to_datetime(df['DT_NASC_APOSENTADO'], errors='coerce')

# === CLASSIFICAÇÃO DO FUNDO ===
cond_funfin = (df['DT_ING_ENTE'] <= DATA_CORTE_ENTE) & (df['DT_NASC_APOSENTADO'] > DATA_CORTE_NASC) & (df['IN_PREV_COMP'] == 2)
cond_funprev = (df['DT_ING_ENTE'] > DATA_CORTE_ENTE) | (df['DT_NASC_APOSENTADO'] <= DATA_CORTE_NASC) | (df['IN_PREV_COMP'] == 1)

df['CALCULO_FUNDO'] = None
df.loc[cond_funfin, 'CALCULO_FUNDO'] = 2
df.loc[cond_funprev, 'CALCULO_FUNDO'] = 1

# === COMPATIBILIDADE ===
df['COMPATIBILIDADE_FUNDO'] = (df['CO_TIPO_FUNDO'] == df['CALCULO_FUNDO']).map({True: 'compativel', False: 'incompativel'})

# === DUPLICIDADE DE CPF ===
df['CPF_DUPLICADO'] = df['ID_APOSENTADO_CPF'].duplicated(keep=False)

# === CENÁRIOS ===
df['CENARIO_FUNDO'] = None
mask_incomp = df['COMPATIBILIDADE_FUNDO'] == 'incompativel'
df.loc[mask_incomp & (~df['CPF_DUPLICADO']), 'CENARIO_FUNDO'] = 'Cenario 1'
df.loc[mask_incomp & (df['CPF_DUPLICADO']) & (df['CO_TIPO_APOSENTADORIA'] == 1), 'CENARIO_FUNDO'] = 'Cenario 2'
df.loc[mask_incomp & (df['CPF_DUPLICADO']) & (df['CO_TIPO_APOSENTADORIA'] != 1), 'CENARIO_FUNDO'] = 'Cenario 3'

# === MAPEAR PARA DESCRIÇÕES ===
df['CO_TIPO_FUNDO'] = df['CO_TIPO_FUNDO'].map(vocab_fundo)
df['IN_PREV_COMP'] = df['IN_PREV_COMP'].map(vocab_prev_comp)
df['CALCULO_FUNDO'] = df['CALCULO_FUNDO'].map(vocab_fundo)
df['CO_TIPO_APOSENTADORIA'] = df['CO_TIPO_APOSENTADORIA'].map(vocab_tipo_aposentadoria)

# === COLUNAS DE SAÍDA ===
colunas_saida = [
    'ID_APOSENTADO_MATRICULA', 'ID_APOSENTADO_CPF', 'CO_TIPO_FUNDO', 'NO_ORGAO',
    'CO_TIPO_APOSENTADORIA', 'VL_APOSENTADORIA', 'VL_CONTRIBUICAO', 'DT_ING_ENTE',
    'DT_NASC_APOSENTADO', 'IN_PREV_COMP', 'CPF_DUPLICADO', 'CALCULO_FUNDO',
    'COMPATIBILIDADE_FUNDO', 'CENARIO_FUNDO'
]

df[colunas_saida].to_excel(ARQUIVO_SAIDA_EXCEL, index=False)

# === RESUMO FORMATADO ===
total = len(df)
compat = (df['COMPATIBILIDADE_FUNDO'] == 'compativel').sum()
incompat = (df['COMPATIBILIDADE_FUNDO'] == 'incompativel').sum()
cpf_duplicados = df['CPF_DUPLICADO'].sum()
incomp_df = df[df['COMPATIBILIDADE_FUNDO'] == 'incompativel']
cenarios = incomp_df['CENARIO_FUNDO'].value_counts()
vl_total_incomp = incomp_df['VL_CONTRIBUICAO'].sum()

resumo = [
    f"1. Total de linhas: {total}\n",
    f"2. Fundos Compatíveis: {compat} ({compat/total:.2%})\n",
    f"3. Fundos Incompatíveis: {incompat} ({incompat/total:.2%})"
]

for i, (fundo, count) in enumerate(incomp_df['CO_TIPO_FUNDO'].value_counts().items(), start=1):
    resumo.append(f"3.1.{i} - Incompatíveis no fundo {fundo}: {count}")

resumo.append("\n4. Incompatíveis por NO_ORGAO:")
for i, (orgao, count) in enumerate(incomp_df['NO_ORGAO'].value_counts().head(3).items(), start=1):
    resumo.append(f"4.{i} - {orgao}: {count}")

resumo.append("\n5 - Cenários de incompatibilidade:")
for i, cenario in enumerate(['Cenario 1', 'Cenario 2', 'Cenario 3'], start=1):
    resumo.append(f"5.{i} - {cenario}: {cenarios.get(cenario, 0)}")

resumo.append(f"\n6. Valor total VL_CONTRIBUICAO incompatível: {vl_total_incomp:.2f}")
resumo.append(f"\n7. CPF_DUPLICADO verdadeiro: {cpf_duplicados}")

with open(ARQUIVO_SAIDA_TXT, "w", encoding="utf-8") as f:
    for linha in resumo:
        f.write(linha + "\n")

print("\n".join(resumo))
print(f"\nAnálise concluída. Arquivos salvos em:\n- {ARQUIVO_SAIDA_EXCEL}\n- {ARQUIVO_SAIDA_TXT}")
