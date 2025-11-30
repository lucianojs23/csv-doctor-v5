# CSV Doctor
## Diagnóstico, Reparo Automático e Relatórios Estruturados para Arquivos CSV

O CSV Doctor v5 é uma ferramenta desenvolvida para inspeção, saneamento e padronização de arquivos CSV com problemas estruturais ou de conteúdo.  
Foi projetado com foco em cenários reais enfrentados por profissionais que lidam diariamente com dados heterogêneos: inconsistências de encoding, delimitadores mistos, colunas desalinhadas, datas inválidas, valores numéricos em múltiplos formatos e diversas formas comuns de corrupção de dados tabulares.
A ferramenta opera inteiramente via linha de comando (CLI) e produz diagnósticos detalhados, reparos automatizados e relatórios visuais em HTML baseados em React e TailwindCSS.

---

## Sumário

1. [Principais Funcionalidades](#principais-funcionalidades)  
2. [Instalação](#instalação)  
3. [Uso da Ferramenta](#uso-da-ferramenta)  
4. [Pipeline Completo](#pipeline-completo)  
5. [Estrutura de Saída](#estrutura-de-saída)  
6. [Tecnologias Utilizadas](#tecnologias-utilizadas)  
7. [Exemplo de Execução](#exemplo-de-execução)  
8. [Contribuição](#contribuição)  
9. [Licença](#licença)

---

# Principais Funcionalidades

## 1. Diagnóstico Estrutural Completo

O CSV Doctor analisa profundamente arquivos CSV, identificando:

- Encoding predominante (UTF-8, Latin-1, CP1252, UTF-16 etc.)
- Delimitador dominante e inconsistências
- Linhas com número incorreto de colunas
- Linhas quebradas (multiline)
- Erros estruturais
- Inferência de tipos por coluna
- Distribuição de nulos e cardinalidade
- Valores suspeitos
- Preview seguro das primeiras linhas
- Score geral de integridade

A execução gera:

```
outputs/diagnostic.json
outputs/report.html
```

---

## 2. Reparo Automático (CSV Repair)

O reparo automático aplica correções estruturais e de conteúdo:

### Colunas desalinhadas
- Preenchimento automático de colunas ausentes  
- Consolidação de colunas excedentes  
- Reconstrução de linhas quebradas  

### Padronização de encoding
- Remoção de caracteres inválidos  
- Normalização para UTF-8  

### Padronização de delimitador
Converte automaticamente variações entre:  
`,`, `;`, `|`, TAB e espaço.

### Normalização de datas
Todas as datas são convertidas para o formato ISO:

```
YYYY-MM-DD
```

### Normalização de números
Inclusão de suporte a diferentes convenções regionais:

- `4.300,50` → `4300.5`  
- `5.500.00` → `5500`  
- `3 500,00` → `3500`  

Saída principal do reparo:

```
outputs/<arquivo>_repaired.csv
```

---

## 3. Relatório HTML

O relatório final inclui:

- Visão geral e score de qualidade  
- Resumo de colunas  
- Taxas de nulos  
- Cardinalidade  
- Visualização das primeiras linhas  
- Descrição das correções realizadas  
- Informações de encoding e delimitador  

O relatório funciona inteiramente offline.

---

## 4. Conversão de Formatos

Após o reparo, é possível converter o arquivo para:

- Parquet  
- Feather  
- CSV limpo  

---

# Instalação

### Via Makefile (recomendado)

```bash
make install
```

### Instalação Manual

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --no-build-isolation -r requirements.txt
pip install --no-build-isolation -e .
```

---

# Uso da Ferramenta

### Diagnóstico

```bash
csvdoctor inspect arquivo.csv --html
```

### Reparo automático

```bash
csvdoctor repair arquivo.csv
```

### Conversão

```bash
csvdoctor convert arquivo.csv --to parquet
```

---

# Pipeline Completo

```bash
csvdoctor full arquivo.csv --to parquet
```

Executa:

1. Reparo  
2. Diagnóstico  
3. Relatório HTML  
4. Conversão  

---

# Estrutura de Saída

```
outputs/
 ├─ logs/
 ├─ diagnostic.json
 ├─ report.html
 ├─ arquivo_repaired.csv
 ├─ arquivo.parquet
 ├─ arquivo.feather
```

---

# Tecnologias Utilizadas

- Python 3.10+
- pandas
- numpy
- chardet
- csv (biblioteca padrão)
- pyarrow
- React 18
- TailwindCSS
- Makefile

---

# Exemplo de Execução

```bash
make example
```

Abra o relatório em:

```
outputs/report.html
```

---

# Contribuição

Contribuições são bem-vindas. Melhorias futuras podem incluir:

- Suporte a schemas YAML  
- Perfil de dataset mais completo  
- Interface Web/API  
- Suporte ampliado para arquivos muito grandes  
- Regras de reparo baseadas em modelos estatísticos ou ML  

---



---

Criado por Luciano de Jesus Santos.
