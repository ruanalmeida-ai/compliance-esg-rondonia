# 🤝 Contribuindo para o Sistema de Compliance ESG Rondônia

Obrigado por considerar contribuir com este projeto! Este documento fornece diretrizes para contribuição.

## 📋 Como Contribuir

### 1. Reportar Bugs

Se você encontrou um bug:

1. Verifique se já não existe uma issue aberta sobre o problema
2. Crie uma nova issue com:
   - Título descritivo
   - Passos para reproduzir
   - Comportamento esperado vs obtido
   - Screenshots se aplicável
   - Versão do Python e dependências

### 2. Sugerir Funcionalidades

Para sugerir novas funcionalidades:

1. Verifique se já não existe uma issue/PR relacionada
2. Crie uma issue descrevendo:
   - Problema que a funcionalidade resolve
   - Proposta de solução
   - Exemplos de uso
   - Alternativas consideradas

### 3. Contribuir com Código

#### Setup do Ambiente

```bash
# Fork e clone
git clone https://github.com/SEU_USUARIO/compliance-esg-rondonia.git
cd compliance-esg-rondonia

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Crie dados de teste
python gerar_dados_exemplo.py
```

#### Workflow

1. **Crie uma branch**:
   ```bash
   git checkout -b feature/minha-funcionalidade
   # ou
   git checkout -b fix/correcao-bug
   ```

2. **Faça suas mudanças**:
   - Siga o estilo de código existente
   - Adicione docstrings em funções novas
   - Comente código complexo
   - Mantenha mudanças focadas e atômicas

3. **Teste suas mudanças**:
   ```bash
   # Valide sintaxe
   python -m py_compile app.py proc.py scraper.py
   
   # Teste manualmente
   streamlit run app.py
   ```

4. **Commit**:
   ```bash
   git add .
   git commit -m "feat: adiciona funcionalidade X"
   ```
   
   Use prefixos:
   - `feat:` nova funcionalidade
   - `fix:` correção de bug
   - `docs:` documentação
   - `style:` formatação
   - `refactor:` refatoração
   - `test:` testes
   - `chore:` manutenção

5. **Push e Pull Request**:
   ```bash
   git push origin feature/minha-funcionalidade
   ```
   
   Abra PR no GitHub com:
   - Título descritivo
   - Descrição do problema/solução
   - Screenshots se aplicável
   - Link para issues relacionadas

## 🎨 Padrões de Código

### Python

- **PEP 8**: Siga o guia de estilo Python
- **Docstrings**: Use formato Google/NumPy
- **Type Hints**: Use quando possível

Exemplo:
```python
def calcular_area_util(gdf_imovel: gpd.GeoDataFrame, 
                       gdf_embargos: gpd.GeoDataFrame) -> dict:
    """
    Calcula área realmente explorável de um imóvel.
    
    Args:
        gdf_imovel: GeoDataFrame com geometria do imóvel
        gdf_embargos: GeoDataFrame com embargos
        
    Returns:
        Dicionário com áreas calculadas em hectares
        
    Raises:
        ValueError: Se geometrias forem inválidas
    """
    # implementação
```

### Streamlit

- Use `st.cache_data` para dados que não mudam
- Organize em seções com `st.markdown("### Título")`
- Prefira `st.columns()` para layouts lado a lado
- Use `with st.spinner()` para operações demoradas

### Git

- Commits pequenos e frequentes
- Mensagens descritivas em português
- Rebase antes de merge (evitar merge commits)

## 🧪 Testes

Atualmente não há testes automatizados, mas você deve:

1. **Testar manualmente** todas as funcionalidades afetadas
2. **Validar em diferentes navegadores**
3. **Testar com dados de exemplo**
4. **Verificar console para erros**

### Futuro: Testes Automatizados

Contribuições bem-vindas para adicionar:
- Pytest para funções de `proc.py`
- Testes de integração para GeoPackage
- Testes de UI com Selenium

## 📚 Documentação

Ao adicionar funcionalidades:

1. Atualize `README.md` se necessário
2. Adicione seção em `GUIA_USO.md` se for feature de usuário
3. Atualize docstrings
4. Adicione comentários em código complexo

## 🐛 Reportando Vulnerabilidades de Segurança

**NÃO** abra issues públicas para vulnerabilidades de segurança.

Entre em contato diretamente:
- LinkedIn: https://www.linkedin.com/in/ruan-almeida-8b8136295/

Inclua:
- Descrição da vulnerabilidade
- Passos para reproduzir
- Impacto potencial
- Sugestões de correção (opcional)

## 💡 Ideias para Contribuir

### Features Planejadas

- [ ] **API REST**: Expor funcionalidades via FastAPI
- [ ] **Autenticação**: Login com OAuth/LDAP
- [ ] **Multi-usuário**: Controle de acesso por perfil
- [ ] **Notificações**: Email/Telegram quando embargos novos
- [ ] **Dashboard Analítico**: Métricas agregadas de múltiplos imóveis
- [ ] **Exportação**: KML, Shapefile, GeoJSON melhorados
- [ ] **Mobile**: UI responsiva otimizada para celular
- [ ] **Offline Mode**: Cache de dados Earth Engine
- [ ] **Integração DETER**: Alertas de desmatamento TerraBrasilis
- [ ] **IA/ML**: Predição de risco de embargo

### Melhorias

- [ ] Performance: Lazy loading de mapas grandes
- [ ] UX: Wizard guiado para primeiro uso
- [ ] Acessibilidade: ARIA labels, contraste
- [ ] Internacionalização: Suporte a inglês
- [ ] Testes: Cobertura de 80%+
- [ ] CI/CD: GitHub Actions para deploy automático

## 📊 Estrutura do Projeto

```
compliance-esg-rondonia/
├── app.py                     # Aplicação Streamlit principal
├── proc.py                    # Funções auxiliares
├── scraper.py                 # Atualização de embargos
├── gerar_dados_exemplo.py     # Gerador de dados de teste
├── requirements.txt           # Dependências Python
├── README.md                  # Documentação principal
├── GUIA_USO.md               # Guia detalhado de uso
├── CONTRIBUTING.md           # Este arquivo
├── LICENSE                   # Licença MIT
├── .gitignore               # Arquivos ignorados
└── .streamlit/
    └── secrets.toml.example # Template de configuração
```

## 🔍 Review Process

PRs serão revisados considerando:

1. **Funcionalidade**: Resolve o problema proposto?
2. **Código**: Legível, mantível, segue padrões?
3. **Performance**: Não degrada performance existente?
4. **Segurança**: Não introduz vulnerabilidades?
5. **Documentação**: Funcionalidade está documentada?
6. **Compatibilidade**: Não quebra funcionalidades existentes?

## 🏆 Reconhecimento

Contribuidores serão mencionados em:
- README.md (seção de contribuidores)
- Release notes
- Commits (via co-authorship)

## 📞 Dúvidas?

- Abra uma issue com a label `question`
- Entre em contato via LinkedIn

---

Obrigado por contribuir! 🎉
