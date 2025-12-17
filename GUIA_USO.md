# 📖 Guia de Uso - Sistema de Compliance ESG Rondônia

## 🚀 Início Rápido

### 1. Instalação

```bash
# Clone o repositório
git clone https://github.com/ruanalmeida-ai/compliance-esg-rondonia.git
cd compliance-esg-rondonia

# Instale as dependências
pip install -r requirements.txt
```

### 2. Preparar Dados

#### Opção A: Dados de Exemplo (Recomendado para Testes)

```bash
python gerar_dados_exemplo.py
```

Isso criará:
- 5 imóveis CAR fictícios
- 3 embargos IBAMA
- 2 embargos ICMBio  
- Áreas de Reserva Legal e APP

#### Opção B: Dados Reais

```bash
python scraper.py
```

Baixa dados reais do IBAMA/ICMBio (requer conexão com APIs públicas).

### 3. Executar Aplicação

```bash
streamlit run app.py
```

A aplicação abrirá em `http://localhost:8501`

---

## 🎯 Funcionalidades Principais

### 📍 Seleção de Imóvel

1. Na barra lateral, escolha um imóvel CAR no dropdown
2. O mapa será atualizado automaticamente
3. Verifique o status de conformidade na sidebar

### 🗺️ Visualização do Mapa

O mapa interativo exibe:
- **Verde/Amarelo/Vermelho/Cinza**: Imóvel CAR (cor indica status de validação)
- **Vermelho**: Embargos IBAMA
- **Laranja**: Embargos ICMBio
- **Verde claro**: Reserva Legal
- **Azul**: Áreas de Preservação Permanente (APP)
- **🔥 Focos de Fogo**: Ative esta camada para ver focos das últimas 24h

**Dica**: Use o controle de camadas no canto superior direito do mapa.

### 📊 Dashboard de Conformidade

À direita do mapa você verá:
- Status do CAR
- Número de embargos
- Score de risco reputacional (0-100)
- Análise de áreas (total, embargada, útil)

### 🔍 Análise de Risco Reputacional

O sistema verifica se o CPF/CNPJ possui embargos em **outras propriedades**:
- ✅ **Baixo Risco** (0-10): Sem embargos
- ⚠️ **Médio Risco** (50): 1-2 embargos
- ❌ **Alto Risco** (90+): 3+ embargos

**Caso de Uso**: Bancos podem usar isso para análise de crédito rural.

### 🛰️ Análise MapBiomas

1. Configure suas credenciais do Google Earth Engine (veja seção abaixo)
2. Selecione o ano de análise (1985-2023)
3. Clique em "▶️ Executar Análise MapBiomas"
4. Visualize gráficos de uso do solo
5. Exporte dados em Excel

**Classes Monitoradas**:
- Formação Florestal
- Pastagem
- Agricultura
- Infraestrutura Urbana
- E muitas outras...

### 📅 Timeline de Satélite

1. Escolha ano inicial e final (2018-2024)
2. Clique em "🛰️ Carregar Imagens Sentinel-2"
3. Compare imagens lado a lado para identificar desmatamento

**Nota**: Esta funcionalidade usa Sentinel-2 (resolução 10m).

### 🔥 Monitoramento de Incêndios

- Consulta automática ao BDQueimadas (INPE)
- Exibe focos detectados nas últimas 24h
- Alerta visual quando há focos ativos

### 📄 Geração de Laudo PDF

1. Após analisar o imóvel, clique em "📄 Gerar Laudo PDF"
2. O sistema cria um relatório profissional com:
   - Status de embargos
   - Análise de risco
   - Cálculo de áreas
   - Selo de aprovação/reprovação
3. Baixe o PDF clicando no botão de download

**Caso de Uso**: Enviar para análise de crédito ou auditoria ESG.

---

## ⚙️ Configuração Avançada

### Google Earth Engine (Necessário para MapBiomas)

#### Método 1: Service Account (Recomendado para Produção)

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto e ative a API Earth Engine
3. Crie uma Service Account e baixe o JSON
4. Converta para base64:
   ```bash
   base64 -i service_account.json | tr -d '\n'
   ```
5. Cole o resultado em `.streamlit/secrets.toml`:
   ```toml
   [google_earth_engine]
   service_account_b64 = "SEU_BASE64_AQUI"
   ```

#### Método 2: Arquivo Local

Coloque `service_account.json` na raiz do projeto.

#### Método 3: Autenticação Padrão (Desenvolvimento)

```bash
earthengine authenticate
```

### Personalização de Cores

Edite `proc.py`, função `cor_por_status()`:

```python
def cor_por_status(status):
    cores = {
        'Validado': 'green',      # Mude para 'darkgreen'
        'Em Análise': 'yellow',   # Mude para 'orange'
        'Cancelado': 'red',       # Mude para 'crimson'
        'Declarado': 'gray'       # Mude para 'lightgray'
    }
    return cores.get(status, 'white')
```

---

## 🐛 Solução de Problemas

### Erro: "Nenhum imóvel encontrado"

**Solução**: Execute `python gerar_dados_exemplo.py` para criar dados de teste.

### Erro: "Earth Engine não disponível"

**Solução**: Configure as credenciais conforme seção "Google Earth Engine" acima.

### Erro: "Módulo não encontrado"

**Solução**:
```bash
pip install -r requirements.txt
```

### Mapa não carrega

**Solução**: Verifique sua conexão com internet. Folium usa tiles do OpenStreetMap.

### Scraper falha

**Causas possíveis**:
1. APIs do IBAMA/ICMBio estão offline
2. URLs mudaram (verifique `scraper.py`)
3. Sem conexão com internet

**Solução temporária**: Use dados de exemplo.

---

## 📊 Estrutura de Dados

### Arquivo: `car_embargos.gpkg`

#### Camada: `area_imovel`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| cod_imovel | String | Código único do imóvel CAR |
| cpf_cnpj | String | CPF/CNPJ do proprietário |
| status_validacao | String | Pendente/Analisado/Validado/Cancelado |
| geometry | Polygon | Polígono do imóvel |

#### Camada: `embargos_ibama`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| cod_imovel | String | Referência ao imóvel |
| cpf_cnpj | String | CPF/CNPJ do autuado |
| data_embargo | Date | Data da autuação |
| area_ha | Float | Área embargada em hectares |
| motivo | String | Motivo do embargo |
| geometry | Polygon | Polígono do embargo |

#### Camada: `embargos_icmbio` (mesmo formato)

#### Camada: `reserva_legal`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| cod_imovel | String | Referência ao imóvel |
| tipo | String | "Reserva Legal" |
| area_ha | Float | Área em hectares |
| geometry | Polygon | Polígono da RL |

#### Camada: `app` (mesmo formato que reserva_legal)

---

## 🎓 Casos de Uso

### 1. Análise de Crédito Rural (Bancos)

**Problema**: Verificar se um produtor é elegível para crédito.

**Solução**:
1. Selecione o imóvel do produtor
2. Verifique embargos IBAMA/ICMBio
3. Analise o score de risco reputacional
4. Calcule a área útil disponível para produção
5. Gere laudo PDF para anexar ao processo

**Decisão**:
- ✅ Aprovado: Sem embargos, baixo risco, área útil > 70%
- ❌ Reprovado: Com embargos ativos ou alto risco

### 2. Due Diligence ESG (Empresas)

**Problema**: Avaliar fornecedores antes de compra de commodities.

**Solução**:
1. Verifique embargos ambientais
2. Analise histórico de desmatamento (MapBiomas)
3. Monitore focos de incêndio em tempo real
4. Verifique status de validação CAR

### 3. Monitoramento Ambiental (ONGs)

**Problema**: Identificar áreas de desmatamento recente.

**Solução**:
1. Use Timeline de Satélite para comparar anos
2. Sobreponha com embargos existentes
3. Exporte dados para análise estatística
4. Denuncie irregularidades aos órgãos competentes

### 4. Compliance Interno (Produtores)

**Problema**: Garantir conformidade antes de auditoria.

**Solução**:
1. Verifique status do próprio CAR
2. Confirme ausência de embargos
3. Valide áreas de RL e APP
4. Mantenha laudo PDF atualizado

---

## 🔒 Segurança e Privacidade

### Dados Sensíveis

⚠️ **NUNCA COMMITE**:
- `service_account.json`
- `.streamlit/secrets.toml`
- Arquivos `.gpkg` com dados reais
- CPF/CNPJ de pessoas reais

### LGPD (Lei Geral de Proteção de Dados)

Se usar dados reais de CPF/CNPJ:
1. Anonimize antes de compartilhar
2. Use hash: `hashlib.sha256(cpf.encode()).hexdigest()`
3. Obtenha consentimento dos titulares
4. Implemente controle de acesso

### Recomendações de Segurança

1. Use HTTPS em produção
2. Adicione autenticação ao Streamlit
3. Limite acesso ao servidor
4. Faça backup regular dos dados
5. Audite logs de acesso

---

## 📈 Performance

### Otimizações

1. **Earth Engine**: Use `tileScale=4` em reduções grandes
2. **Cache**: Streamlit cacheia automaticamente funções com `@st.cache_data`
3. **Geometrias**: Simplifique polígonos complexos antes de visualizar

### Limites

- **MapBiomas**: Máximo ~100.000 hectares por análise
- **Sentinel-2**: Imagens disponíveis desde 2015
- **BDQueimadas**: Últimas 24h, 48h, 7 dias

---

## 🤝 Contribuindo

Contribuições são bem-vindas! 

### Como Contribuir

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

### Ideias para Contribuir

- [ ] Integração com TerraBrasilis (desmatamento DETER)
- [ ] Análise de CAR duplicado/sobreposto
- [ ] Dashboard com múltiplos imóveis
- [ ] API REST para integração
- [ ] Modo offline (cache de imagens)
- [ ] Exportação para KML/Shapefile
- [ ] Alertas por email/Telegram
- [ ] Gráficos de série temporal melhorados

---

## 📞 Suporte

### Contato

**Desenvolvedor**: Ruan Almeida
- LinkedIn: [ruan-almeida-8b8136295](https://www.linkedin.com/in/ruan-almeida-8b8136295/)
- Instagram: [@ruan_almeida_martins](https://www.instagram.com/ruan_almeida_martins/)

### Issues

Reporte bugs em: https://github.com/ruanalmeida-ai/compliance-esg-rondonia/issues

---

## 📚 Referências

- [MapBiomas Collection 8](https://mapbiomas.org/)
- [Google Earth Engine](https://earthengine.google.com/)
- [IBAMA Embargos](https://www.ibama.gov.br/)
- [ICMBio](https://www.icmbio.gov.br/)
- [BDQueimadas INPE](https://queimadas.dgi.inpe.br/)
- [SICAR - Sistema CAR](https://www.car.gov.br/)

---

## 📄 Licença

MIT License - Uso livre com atribuição.

Copyright (c) 2024 Ruan Almeida
