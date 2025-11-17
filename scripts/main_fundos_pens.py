import pandas as pd
from datetime import datetime
import os

# === CONFIGURAÇÕES DINÂMICAS ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(BASE_DIR, "..", "dados")
PASTA_RESULTADOS = os.path.join(BASE_DIR, "..", "resultados")
ARQUIVO_SAIDA_EXCEL = os.path.join(PASTA_RESULTADOS, "PENSIONISTAS_incompativeis.xlsx")
ARQUIVO_SAIDA_TXT = os.path.join(PASTA_RESULTADOS, "PENSIONISTAS_resumo_analise.txt")

# === GARANTIR PASTA DE RESULTADOS ===
os.makedirs(PASTA_RESULTADOS, exist_ok=True)

# === SELECIONAR ARQUIVO DE ENTRADA ===
arquivos = [f for f in os.listdir(PASTA_DADOS) if "pensionista" in f.lower() and f.lower().endswith(".xlsx")]
if not arquivos:
    raise FileNotFoundError("Nenhum arquivo contendo 'pensionista' encontrado na pasta de dados.")

arquivos.sort(key=lambda f: os.path.getmtime(os.path.join(PASTA_DADOS, f)), reverse=True)
ARQUIVO_ENTRADA = os.path.join(PASTA_DADOS, arquivos[0])
print(f"Arquivo selecionado: {ARQUIVO_ENTRADA}")

# === SELECIONAR ABA AUTOMATICAMENTE ===
abas = pd.ExcelFile(ARQUIVO_ENTRADA, engine="openpyxl").sheet_names
aba_selecionada = next((aba for aba in abas if "pensionista" in aba.lower()), abas[0])
print(f"Aba selecionada: {aba_selecionada}")

# === DATA DE CORTE ===
DATA_CORTE_NASC = datetime(1957, 2, 28)

# === CARREGAR DADOS ===
df = pd.read_excel(ARQUIVO_ENTRADA, sheet_name=aba_selecionada, engine="openpyxl")

# === CONVERSÃO DE DATAS ===
df['DT_NASC_INSTITUIDOR'] = pd.to_datetime(df['DT_NASC_INSTITUIDOR'], errors='coerce')

# === PADRONIZAR CO_TIPO_FUNDO ===
df['CO_TIPO_FUNDO'] = df['CO_TIPO_FUNDO'].replace({"FUNPREV": 1, "FUNFIN": 2})

# === CALCULO_FUNDO ===
def calcular_fundo(data):
    if pd.isna(data):  # Se data for nula ou erro
        return "FUNPREV"
    return "FUNPREV" if data <= DATA_CORTE_NASC else None

df['CALCULO_FUNDO'] = df['DT_NASC_INSTITUIDOR'].apply(calcular_fundo)

# === EXCLUIR REGISTROS COM CALCULO_FUNDO = Null ===
df = df[df['CALCULO_FUNDO'].notna()]

# === COMPATIBILIDADE ===
df['COMPATIBILIDADE_FUNDO'] = df.apply(
    lambda x: 'compativel' if (x['CO_TIPO_FUNDO'] == 1 and x['CALCULO_FUNDO'] == 'FUNPREV') else 'incompativel',
    axis=1
)

# === DUPLICIDADE DE CPF ===
df['CPF_DUPLICADO'] = df['ID_INSTITUIDOR_CPF'].duplicated(keep=False)

# === FILTRAR INCOMPATÍVEIS ===
df_incomp = df[df['COMPATIBILIDADE_FUNDO'] == 'incompativel']

# === MAPEAR CO_TIPO_FUNDO PARA TEXTO NA SAÍDA ===
map_saida = {1: "FUNPREV", 2: "FUNFIN"}
df_incomp['CO_TIPO_FUNDO'] = df_incomp['CO_TIPO_FUNDO'].map(map_saida)

# === CAMPOS DE SAÍDA ===
colunas_saida = [
    'ID_INSTITUIDOR_MATRICULA', 'ID_INSTITUIDOR_CPF', 'NO_ORGAO', 'CO_TIPO_FUNDO',
    'DT_NASC_INSTITUIDOR', 'ID_PENSIONISTA_MATRICULA', 'ID_PENSIONISTA_CPF',
    'VL_CONTRIBUICAO', 'CPF_DUPLICADO', 'CALCULO_FUNDO', 'COMPATIBILIDADE_FUNDO'
]

df_incomp[colunas_saida].to_excel(ARQUIVO_SAIDA_EXCEL, index=False)

# === RESUMO FORMATADO ===
total = len(df)
incompat = len(df_incomp)
compat = total - incompat
cpf_duplicados = df['CPF_DUPLICADO'].sum()

resumo = [
    f"1. Total analisados (FUNPREV): {total}",
    f"2. Compatíveis: {compat} ({compat/total:.2%})",
    f"3. Incompatíveis: {incompat} ({incompat/total:.2%})",
    f"4. CPF duplicados: {cpf_duplicados}",
    "\n5. Top 5 órgãos com incompatíveis:"
]

for i, (orgao, count) in enumerate(df_incomp['NO_ORGAO'].value_counts().head(5).items(), start=1):
    resumo.append(f"5.{i} - {orgao}: {count}")

with open(ARQUIVO_SAIDA_TXT, "w", encoding="utf-8") as f:
    for linha in resumo:
        f.write(linha + "\n")

print("\n".join(resumo))
print(f"\nAnálise concluída. Arquivos salvos em:\n- {ARQUIVO_SAIDA_EXCEL}\n- {ARQUIVO_SAIDA_TXT}")