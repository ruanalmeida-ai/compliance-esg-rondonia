# 🌍 Sistema de Compliance ESG - Rondônia

Sistema integrado para análise de conformidade ambiental de imóveis rurais, combinando dados do Cadastro Ambiental Rural (CAR), embargos ambientais (IBAMA/ICMBio) e análise temporal de uso do solo (MapBiomas).

## 🎯 Funcionalidades

### 📊 Análise de Embargos
- Visualização de embargos IBAMA e ICMBio sobre imóveis CAR
- Status de conformidade em tempo real
- Mapa interativo com camadas controláveis

### 🛰️ Análise MapBiomas
- Série histórica de uso e cobertura do solo (1985-2024)
- Análise de transição entre dois períodos
- Exportação em Excel, GeoJSON e GeoTIFF

### 🆕 Inovações de Elite

#### 🔍 CPF/CNPJ "Sujo" (Risco Reputacional)
Identifica se o proprietário possui embargos em outras propriedades, calculando um score de risco (0-100).

#### 📅 Timeline de Satélite
Slider temporal para visualizar imagens de satélite de diferentes anos e comparar desmatamento.

#### 🔥 Alertas de Fogo em Tempo Real
Integração com BDQueimadas (INPE) mostrando focos de incêndio das últimas 24h.

#### 🌾 Cálculo de Área Útil
Desconta área embargada, Reserva Legal e APP para mostrar hectares realmente exploráveis.

#### ✅ Status de Validação CAR
Diferencia visualmente CARs validados pelo órgão estadual vs apenas declarados.

#### 📄 Gerador de Laudo PDF
Relatório automático de conformidade com mapas, dados e selo de aprovação/reprovação.

## 🚀 Como Usar

### 1. Instalação

```bash
git clone https://github.com/ruanalmeida-ai/compliance-esg-rondonia.git
cd compliance-esg-rondonia
pip install -r requirements.txt
```

### 2. Configuração Google Earth Engine

Crie um projeto no [Google Cloud](https://console.cloud.google.com/) e ative a API do Earth Engine.

Coloque o arquivo `service_account.json` na raiz do projeto ou configure via secrets:

```toml
# .streamlit/secrets.toml
[google_earth_engine]
service_account_b64 = "SEU_JSON_EM_BASE64"
```

### 3. Atualizar Base de Dados

#### Opção A: Usar dados reais do IBAMA/ICMBio

```bash
python scraper.py
```

Ou use o botão "🔄 Atualizar Base" dentro do app.

#### Opção B: Gerar dados de exemplo para testes

```bash
python gerar_dados_exemplo.py
```

Isso criará um arquivo `car_embargos.gpkg` com dados fictícios para demonstração.

### 4. Executar

```bash
streamlit run app.py
```

## 📁 Estrutura de Dados

O arquivo `car_embargos.gpkg` (GeoPackage) deve conter as camadas:

- `area_imovel`: Polígonos dos imóveis CAR
- `embargos_ibama`: Áreas embargadas pelo IBAMA
- `embargos_icmbio`: Áreas embargadas pelo ICMBio
- `reserva_legal` (opcional): Áreas de Reserva Legal
- `app` (opcional): Áreas de Preservação Permanente

### Colunas Obrigatórias

**area_imovel:**
- `cod_imovel` (str): Código único do imóvel
- `cpf_cnpj` (str): CPF/CNPJ do proprietário
- `status_validacao` (str): Pendente/Analisado/Validado/Cancelado
- `geometry` (Polygon): Geometria do imóvel

**embargos_ibama/embargos_icmbio:**
- `cod_imovel` (str): Referência ao imóvel
- `cpf_cnpj` (str): CPF/CNPJ do autuado
- `data_embargo` (date): Data da autuação
- `area_ha` (float): Área embargada em hectares
- `geometry` (Polygon): Geometria do embargo

## 🛠️ Tecnologias

- **Streamlit**: Interface web
- **GeoPandas**: Manipulação de dados geoespaciais
- **Folium**: Mapas interativos
- **Google Earth Engine**: Análise de imagens de satélite
- **Plotly**: Gráficos interativos
- **ReportLab**: Geração de PDFs

## 👨‍💻 Desenvolvido por

**Ruan Almeida**

- [LinkedIn](https://www.linkedin.com/in/ruan-almeida-8b8136295/)
- [Instagram](https://www.instagram.com/ruan_almeida_martins/)

## 📜 Licença

MIT License - Uso livre com atribuição.
