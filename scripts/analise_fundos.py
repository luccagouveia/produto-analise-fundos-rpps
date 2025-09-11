import pandas as pd
from datetime import datetime
import os

# === CONFIGURAÇÕES ===
ARQUIVO_ENTRADA = "dados/SERVIDOR.xlsx"
ARQUIVO_SAIDA_EXCEL = "resultados/SERVIDOR_resultado.xlsx"
ARQUIVO_SAIDA_TXT = "resultados/SERVIDOR_resumo_analise.txt"
NOME_ABA = "SERVIDOR"

# === GARANTIR PASTA DE RESULTADOS ===
os.makedirs("resultados", exist_ok=True)

# === DATAS DE CORTE ===
DATA_CORTE_ENTE = datetime(2018, 12, 27)
DATA_CORTE_NASC = datetime(1957, 2, 28)

# === CARREGAR DADOS ===
df = pd.read_excel(ARQUIVO_ENTRADA, sheet_name=NOME_ABA, engine="openpyxl")

# === CLASSIFICAÇÃO DO FUNDO ===
def classificar_fundo(row):
    dt_ing_ente = pd.to_datetime(row['DT_ING_ENTE'], errors='coerce')
    dt_nasc = pd.to_datetime(row['DT_NASC_SERVIDOR'], errors='coerce')
    prev_comp = row['IN_PREV_COMP']
    if pd.isna(dt_ing_ente) or pd.isna(dt_nasc) or pd.isna(prev_comp):
        return None
    if dt_ing_ente <= DATA_CORTE_ENTE and dt_nasc > DATA_CORTE_NASC and prev_comp == 2:
        return 2  # FUNFIN
    if dt_ing_ente > DATA_CORTE_ENTE or dt_nasc <= DATA_CORTE_NASC or prev_comp == 1:
        return 1  # FUNPREV
    return None

df['CALCULO_FUNDO'] = df.apply(classificar_fundo, axis=1)

# === COMPATIBILIDADE ===
df['COMPATIBILIDADE_FUNDO'] = df.apply(
    lambda row: 'compativel' if row['CO_TIPO_FUNDO'] == row['CALCULO_FUNDO'] else 'incompativel',
    axis=1
)

# === DUPLICIDADE DE CPF ===
cpf_counts = df['ID_SERVIDOR_CPF'].value_counts()
df['CPF_DUPLICADO'] = df['ID_SERVIDOR_CPF'].map(lambda x: cpf_counts[x] > 1)

# === CENÁRIOS ===
def classificar_cenario(row):
    if row['COMPATIBILIDADE_FUNDO'] == 'incompativel':
        if not row['CPF_DUPLICADO']:
            return "Cenario 1"
        elif row['CPF_DUPLICADO'] and row['CO_SITUACAO_FUNCIONAL'] == 1:
            return "Cenario 2"
        elif row['CPF_DUPLICADO'] and row['CO_SITUACAO_FUNCIONAL'] != 1:
            return "Cenario 3"
    return None

df['CENARIO_FUNDO'] = df.apply(classificar_cenario, axis=1)

# === COLUNAS DE SAÍDA ===
colunas_saida = [
    'ID_SERVIDOR_MATRICULA', 'ID_SERVIDOR_CPF', 'CO_TIPO_FUNDO', 'NO_ORGAO',
    'CO_SITUACAO_FUNCIONAL', 'VL_CONTRIBUICAO', 'DT_ING_ENTE', 'DT_NASC_SERVIDOR',
    'IN_PREV_COMP', 'CPF_DUPLICADO', 'CALCULO_FUNDO', 'COMPATIBILIDADE_FUNDO', 'CENARIO_FUNDO'
]

# === SALVAR RESULTADO EM EXCEL ===
df[colunas_saida].to_excel(ARQUIVO_SAIDA_EXCEL, index=False)

# === RESUMO DA ANÁLISE ===
resumo = []

resumo.append(f"1. Total de linhas: {len(df)}")
resumo.append(f"2. Compatíveis: {(df['COMPATIBILIDADE_FUNDO'] == 'compativel').sum()}")
resumo.append(f"3. Incompatíveis: {(df['COMPATIBILIDADE_FUNDO'] == 'incompativel').sum()}")

# 3.1 Incompatíveis por tipo de fundo
incomp_df = df[df['COMPATIBILIDADE_FUNDO'] == 'incompativel']
for tipo in [1, 2, 9]:
    count = incomp_df[incomp_df['CO_TIPO_FUNDO'] == tipo].shape[0]
    resumo.append(f"3.1.{tipo} - Incompatíveis CO_TIPO_FUNDO {tipo}: {count}")

# 3.1 Incompatíveis por órgão
orgaos = incomp_df['NO_ORGAO'].value_counts()
resumo.append("3.1 - Incompatíveis por NO_ORGAO:")
resumo.extend([f"  {orgao}: {count}" for orgao, count in orgaos.items()])

# 3.2 Incompatíveis por cenário
cenarios = incomp_df['CENARIO_FUNDO'].value_counts()
for cenario in ['Cenario 1', 'Cenario 2', 'Cenario 3']:
    resumo.append(f"3.2 - {cenario}: {cenarios.get(cenario, 0)}")

# 3.3 Valor total de contribuição incompatível
vl_total_incomp = incomp_df['VL_CONTRIBUICAO'].sum()
resumo.append(f"3.3 - Valor total VL_CONTRIBUICAO incompatível: {vl_total_incomp:.2f}")

# 3.3 Valor total por tipo de fundo
for tipo in [1, 2, 9]:
    soma = incomp_df[incomp_df['CO_TIPO_FUNDO'] == tipo]['VL_CONTRIBUICAO'].sum()
    resumo.append(f"3.3.{tipo} - Valor total VL_CONTRIBUICAO incompatível para CO_TIPO_FUNDO {tipo}: {soma:.2f}")

# 3.4 Contribuições nulas
nulos_contrib = df['VL_CONTRIBUICAO'].isna().sum()
resumo.append(f"3.4 - VL_CONTRIBUICAO nulo ou vazio: {nulos_contrib}")

# 4. CPFs duplicados
cpf_duplicados = df['CPF_DUPLICADO'].sum()
resumo.append(f"4. CPF_DUPLICADO verdadeiro: {cpf_duplicados}")

# === SALVAR RESUMO EM TXT ===
with open(ARQUIVO_SAIDA_TXT, "w", encoding="utf-8") as f:
    for linha in resumo:
        f.write(linha + "\n")

# === EXIBIR NO TERMINAL ===
for linha in resumo:
    print(linha)

print(f"\nAnálise concluída. Arquivos salvos em:\n- {ARQUIVO_SAIDA_EXCEL}\n- {ARQUIVO_SAIDA_TXT}")
