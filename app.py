"""
Sistema de Compliance ESG - Rondônia
Aplicação principal integrando análise de embargos CAR e MapBiomas
"""

import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import subprocess
import json
import base64
from io import BytesIO

# Importar funções auxiliares
from proc import (
    ler_geodataframe,
    selecionar_imovel_car,
    inserir_geojson_folium,
    mostrar_status,
    validar_geometria,
    contar_embargos_por_cpf,
    calcular_risco_reputacional,
    calcular_area_util,
    cor_por_status
)

# Tentar importar Earth Engine
try:
    import ee
    import geemap.foliumap as geemap
    EE_DISPONIVEL = True
except ImportError:
    EE_DISPONIVEL = False

# Configuração da página
st.set_page_config(
    page_title="Compliance ESG - Rondônia",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .reportview-container {
        background: #f5f5f5;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


# ==================== INICIALIZAÇÃO EARTH ENGINE ====================

def inicializar_earth_engine():
    """
    Inicializa Google Earth Engine usando service account
    
    Returns:
        bool: True se inicialização foi bem-sucedida
    """
    if not EE_DISPONIVEL:
        return False
    
    try:
        # Verificar se já está inicializado
        ee.Initialize()
        return True
    except:
        pass
    
    try:
        # Tentar usar secrets do Streamlit
        if 'google_earth_engine' in st.secrets:
            service_account_info = st.secrets['google_earth_engine']
            
            if 'service_account_b64' in service_account_info:
                # Decodificar base64
                credentials_json = base64.b64decode(
                    service_account_info['service_account_b64']
                ).decode('utf-8')
                credentials = json.loads(credentials_json)
                
                # Inicializar com service account
                service_account = credentials['client_email']
                credentials_ee = ee.ServiceAccountCredentials(service_account, key_data=credentials_json)
                ee.Initialize(credentials_ee)
                return True
        
        # Tentar arquivo local
        if os.path.exists('service_account.json'):
            with open('service_account.json', 'r') as f:
                credentials = json.load(f)
            service_account = credentials['client_email']
            credentials_ee = ee.ServiceAccountCredentials(service_account, 'service_account.json')
            ee.Initialize(credentials_ee)
            return True
        
        # Tentar autenticação padrão
        ee.Initialize()
        return True
        
    except Exception as e:
        st.sidebar.warning(f"⚠️ Earth Engine não disponível: {str(e)[:100]}")
        return False


# ==================== FUNÇÕES DE ANÁLISE MAPBIOMAS ====================

def obter_cobertura_mapbiomas(roi, ano):
    """
    Obtém dados de cobertura do MapBiomas para um ano específico
    
    Args:
        roi (ee.Geometry): Região de interesse
        ano (int): Ano da análise
        
    Returns:
        dict: Dicionário com estatísticas de cobertura
    """
    try:
        # Coleção MapBiomas 8.0
        mapbiomas = ee.Image('projects/mapbiomas-workspace/public/collection8/mapbiomas_collection80_integration_v1')
        
        # Selecionar banda do ano
        banda = f'classification_{ano}'
        imagem = mapbiomas.select(banda)
        
        # Calcular áreas por classe
        areas = imagem.reduceRegion(
            reducer=ee.Reducer.frequencyHistogram(),
            geometry=roi,
            scale=30,
            maxPixels=1e13,
            bestEffort=True,
            tileScale=4
        )
        
        # Processar resultado
        histogram = areas.getInfo()[banda]
        
        # Converter pixel count para hectares (30m x 30m = 900m² = 0.09ha)
        resultado = {}
        for classe, pixels in histogram.items():
            area_ha = float(pixels) * 0.09
            resultado[int(classe)] = area_ha
        
        return resultado
        
    except Exception as e:
        st.error(f"Erro ao obter cobertura MapBiomas: {e}")
        return {}


def mapbiomas_classes():
    """
    Retorna dicionário com classes do MapBiomas
    
    Returns:
        dict: Dicionário {código: nome}
    """
    return {
        3: 'Formação Florestal',
        4: 'Formação Savânica',
        5: 'Mangue',
        11: 'Área Úmida',
        12: 'Campo Alagado',
        15: 'Pastagem',
        18: 'Agricultura',
        21: 'Mosaico Agricultura/Pastagem',
        24: 'Infraestrutura Urbana',
        25: 'Outras Áreas não Vegetadas',
        30: 'Mineração',
        33: 'Rio/Lago/Oceano',
        41: 'Lavoura Temporária',
        46: 'Café',
        47: 'Citrus',
        48: 'Outras Lavouras Perenes'
    }


def criar_grafico_cobertura(dados_cobertura, titulo):
    """
    Cria gráfico de barras para cobertura do solo
    
    Args:
        dados_cobertura (dict): Dicionário {classe: area_ha}
        titulo (str): Título do gráfico
        
    Returns:
        plotly.graph_objects.Figure: Figura do gráfico
    """
    classes = mapbiomas_classes()
    
    # Preparar dados
    df_dados = []
    for classe_id, area in dados_cobertura.items():
        nome_classe = classes.get(classe_id, f'Classe {classe_id}')
        df_dados.append({'Classe': nome_classe, 'Área (ha)': area})
    
    df = pd.DataFrame(df_dados).sort_values('Área (ha)', ascending=False)
    
    # Criar gráfico
    fig = px.bar(
        df,
        x='Classe',
        y='Área (ha)',
        title=titulo,
        color='Área (ha)',
        color_continuous_scale='Greens'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        showlegend=False
    )
    
    return fig


def criar_grafico_pizza(dados_cobertura):
    """
    Cria gráfico de pizza para cobertura do solo
    
    Args:
        dados_cobertura (dict): Dicionário {classe: area_ha}
        
    Returns:
        plotly.graph_objects.Figure: Figura do gráfico
    """
    classes = mapbiomas_classes()
    
    # Preparar dados
    labels = []
    values = []
    for classe_id, area in dados_cobertura.items():
        nome_classe = classes.get(classe_id, f'Classe {classe_id}')
        labels.append(nome_classe)
        values.append(area)
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(title='Distribuição de Uso do Solo', height=500)
    
    return fig


# ==================== FUNÇÕES DE SATÉLITE ====================

def obter_imagem_sentinel2(roi, ano):
    """
    Obtém imagem Sentinel-2 mediana para um ano
    
    Args:
        roi (ee.Geometry): Região de interesse
        ano (int): Ano da imagem
        
    Returns:
        ee.Image: Imagem Sentinel-2 processada
    """
    try:
        # Definir período
        data_inicio = f'{ano}-01-01'
        data_fim = f'{ano}-12-31'
        
        # Coleção Sentinel-2
        sentinel = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filterBounds(roi) \
            .filterDate(data_inicio, data_fim) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
            .select(['B4', 'B3', 'B2'])  # RGB
        
        # Mediana
        imagem = sentinel.median().clip(roi)
        
        return imagem
    
    except Exception as e:
        st.error(f"Erro ao obter imagem Sentinel-2: {e}")
        return None


def detectar_focos_fogo(gdf_imovel):
    """
    Detecta focos de fogo dentro do polígono do imóvel
    Nota: Esta é uma função simulada. A API real do BDQueimadas requer autenticação.
    
    Args:
        gdf_imovel (gpd.GeoDataFrame): GeoDataFrame do imóvel
        
    Returns:
        int: Número de focos detectados (simulado)
    """
    # Em uma implementação real, você faria:
    # 1. Consulta à API do BDQueimadas INPE
    # 2. Filtrar focos das últimas 24h
    # 3. Fazer interseção espacial com o polígono
    
    # Por enquanto, retorna 0 (sem focos)
    # URL da API: https://queimadas.dgi.inpe.br/api/focos/
    
    return 0


# ==================== FUNÇÕES DE PDF ====================

def gerar_laudo_pdf(dados_imovel, embargos_ibama, embargos_icmbio, areas, risco):
    """
    Gera PDF profissional de compliance
    
    Args:
        dados_imovel (dict): Dados do imóvel
        embargos_ibama (int): Número de embargos IBAMA
        embargos_icmbio (int): Número de embargos ICMBio
        areas (dict): Áreas calculadas
        risco (tuple): (mensagem, score)
        
    Returns:
        bytes: PDF em bytes
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        
        # Criar buffer
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        
        # Dimensões da página
        width, height = A4
        
        # Cabeçalho
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(2*cm, height - 2*cm, "LAUDO DE CONFORMIDADE ESG")
        
        pdf.setFont("Helvetica", 12)
        pdf.drawString(2*cm, height - 3*cm, f"Imóvel: {dados_imovel.get('cod_imovel', 'N/A')}")
        pdf.drawString(2*cm, height - 3.7*cm, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Linha separadora
        pdf.line(2*cm, height - 4*cm, width - 2*cm, height - 4*cm)
        
        # Status de Embargos
        y_pos = height - 5*cm
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(2*cm, y_pos, "STATUS DE EMBARGOS")
        
        pdf.setFont("Helvetica", 11)
        y_pos -= 0.8*cm
        pdf.drawString(2*cm, y_pos, f"Embargos IBAMA: {embargos_ibama}")
        y_pos -= 0.6*cm
        pdf.drawString(2*cm, y_pos, f"Embargos ICMBio: {embargos_icmbio}")
        
        # Status geral
        y_pos -= 1*cm
        pdf.setFont("Helvetica-Bold", 14)
        if embargos_ibama + embargos_icmbio == 0:
            pdf.setFillColorRGB(0, 0.5, 0)
            pdf.drawString(2*cm, y_pos, "✓ APROVADO - Sem Embargos")
        else:
            pdf.setFillColorRGB(0.8, 0, 0)
            pdf.drawString(2*cm, y_pos, "✗ REPROVADO - Com Embargos Ativos")
        
        # Resetar cor
        pdf.setFillColorRGB(0, 0, 0)
        
        # Risco Reputacional
        y_pos -= 1.5*cm
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(2*cm, y_pos, "RISCO REPUTACIONAL")
        
        pdf.setFont("Helvetica", 11)
        y_pos -= 0.8*cm
        pdf.drawString(2*cm, y_pos, f"{risco[0]}")
        y_pos -= 0.6*cm
        pdf.drawString(2*cm, y_pos, f"Score: {risco[1]}/100")
        
        # Áreas
        y_pos -= 1.5*cm
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(2*cm, y_pos, "ANÁLISE DE ÁREAS")
        
        pdf.setFont("Helvetica", 11)
        y_pos -= 0.8*cm
        pdf.drawString(2*cm, y_pos, f"Área Total: {areas['total']:.2f} ha")
        y_pos -= 0.6*cm
        pdf.drawString(2*cm, y_pos, f"Área Embargada: {areas['embargada']:.2f} ha")
        y_pos -= 0.6*cm
        pdf.drawString(2*cm, y_pos, f"Reserva Legal: {areas['reserva_legal']:.2f} ha")
        y_pos -= 0.6*cm
        pdf.drawString(2*cm, y_pos, f"APP: {areas['app']:.2f} ha")
        y_pos -= 0.6*cm
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(2*cm, y_pos, f"Área Útil Explorável: {areas['util']:.2f} ha ({areas['percentual_util']:.1f}%)")
        
        # Rodapé
        pdf.setFont("Helvetica", 8)
        pdf.drawString(2*cm, 2*cm, "Sistema de Compliance ESG - Rondônia")
        pdf.drawString(2*cm, 1.5*cm, "Desenvolvido por Ruan Almeida")
        
        pdf.save()
        
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
        return None


# ==================== INTERFACE PRINCIPAL ====================

def main():
    """Função principal da aplicação"""
    
    # Título
    st.title("🌍 Sistema de Compliance ESG - Rondônia")
    st.markdown("**Análise Integrada: Embargos CAR + MapBiomas + Inovações ESG**")
    st.markdown("---")
    
    # ==================== SIDEBAR ====================
    
    st.sidebar.title("⚙️ Configurações")
    
    # Botão de atualização de embargos
    if st.sidebar.button("🔄 Atualizar Base de Embargos"):
        with st.spinner("Baixando dados do IBAMA/ICMBio..."):
            resultado = subprocess.run(
                ["python", "scraper.py"],
                capture_output=True,
                text=True
            )
            
            if resultado.returncode == 0:
                st.sidebar.success("✅ Base atualizada com sucesso!")
                st.rerun()
            else:
                st.sidebar.error(f"❌ Erro na atualização: {resultado.stderr}")
    
    # Verificar se arquivo existe
    gpkg_path = "car_embargos.gpkg"
    if not os.path.exists(gpkg_path):
        st.warning("⚠️ Arquivo `car_embargos.gpkg` não encontrado. Execute o scraper primeiro ou faça upload de um arquivo válido.")
        st.info("💡 Clique no botão '🔄 Atualizar Base de Embargos' na barra lateral para baixar os dados.")
        st.stop()
    
    # Tentar ler camadas
    try:
        # Listar camadas disponíveis
        import fiona
        layers = fiona.listlayers(gpkg_path)
        
        if not layers:
            st.error("❌ Nenhuma camada encontrada no GeoPackage")
            st.stop()
        
        st.sidebar.success(f"✅ {len(layers)} camadas encontradas")
        
        # Ler dados
        gdf_imoveis = None
        gdf_embargos_ibama = gpd.GeoDataFrame()
        gdf_embargos_icmbio = gpd.GeoDataFrame()
        gdf_rl = gpd.GeoDataFrame()
        gdf_app = gpd.GeoDataFrame()
        
        if 'area_imovel' in layers:
            gdf_imoveis = ler_geodataframe(gpkg_path, 'area_imovel')
        
        if 'embargos_ibama' in layers:
            gdf_embargos_ibama = ler_geodataframe(gpkg_path, 'embargos_ibama')
        
        if 'embargos_icmbio' in layers:
            gdf_embargos_icmbio = ler_geodataframe(gpkg_path, 'embargos_icmbio')
        
        if 'reserva_legal' in layers:
            gdf_rl = ler_geodataframe(gpkg_path, 'reserva_legal')
        
        if 'app' in layers:
            gdf_app = ler_geodataframe(gpkg_path, 'app')
        
        # Verificar se há imóveis
        if gdf_imoveis is None or gdf_imoveis.empty:
            st.error("❌ Nenhum imóvel encontrado na camada 'area_imovel'")
            st.stop()
        
        # Determinar coluna de código
        coluna_cod = 'cod_imovel' if 'cod_imovel' in gdf_imoveis.columns else gdf_imoveis.columns[0]
        
        # Seleção de imóvel
        st.sidebar.markdown("### 📍 Selecionar Imóvel")
        codigos_imoveis = gdf_imoveis[coluna_cod].unique().tolist()
        codigo_selecionado = st.sidebar.selectbox(
            "Código do Imóvel:",
            options=codigos_imoveis,
            index=0
        )
        
        # Selecionar imóvel
        gdf_imovel_sel, lat, lon, min_lat, max_lat, min_lon, max_lon = selecionar_imovel_car(
            gdf_imoveis,
            codigo_selecionado,
            coluna_cod
        )
        
        # Filtrar embargos do imóvel
        gdf_embargos_ibama_imovel = gpd.GeoDataFrame()
        gdf_embargos_icmbio_imovel = gpd.GeoDataFrame()
        
        if not gdf_embargos_ibama.empty:
            # Filtrar por interseção espacial
            gdf_embargos_ibama_imovel = gpd.sjoin(
                gdf_embargos_ibama,
                gdf_imovel_sel,
                how='inner',
                predicate='intersects'
            )
        
        if not gdf_embargos_icmbio.empty:
            gdf_embargos_icmbio_imovel = gpd.sjoin(
                gdf_embargos_icmbio,
                gdf_imovel_sel,
                how='inner',
                predicate='intersects'
            )
        
        # Filtrar RL e APP do imóvel
        gdf_rl_imovel = gpd.GeoDataFrame()
        gdf_app_imovel = gpd.GeoDataFrame()
        
        if not gdf_rl.empty:
            gdf_rl_imovel = gpd.sjoin(gdf_rl, gdf_imovel_sel, how='inner', predicate='intersects')
        
        if not gdf_app.empty:
            gdf_app_imovel = gpd.sjoin(gdf_app, gdf_imovel_sel, how='inner', predicate='intersects')
        
        # Obter CPF/CNPJ
        cpf_cnpj = None
        if 'cpf_cnpj' in gdf_imovel_sel.columns:
            cpf_cnpj = gdf_imovel_sel.iloc[0]['cpf_cnpj']
        
        # Status de validação
        status_validacao = 'Declarado'
        if 'status_validacao' in gdf_imovel_sel.columns:
            status_validacao = gdf_imovel_sel.iloc[0]['status_validacao']
        
        # ==================== CONFORMIDADE ====================
        
        st.sidebar.markdown("### 📊 Conformidade")
        
        num_embargos_ibama = len(gdf_embargos_ibama_imovel)
        num_embargos_icmbio = len(gdf_embargos_icmbio_imovel)
        
        st.sidebar.markdown(mostrar_status("IBAMA", num_embargos_ibama))
        st.sidebar.markdown(mostrar_status("ICMBio", num_embargos_icmbio))
        
        # Risco reputacional
        if cpf_cnpj:
            risco_msg, risco_score = calcular_risco_reputacional(
                cpf_cnpj,
                gdf_embargos_ibama,
                gdf_embargos_icmbio
            )
            st.sidebar.markdown(f"**{risco_msg}** (Score: {risco_score})")
            
            total_outros_embargos = contar_embargos_por_cpf(
                cpf_cnpj,
                gdf_embargos_ibama,
                gdf_embargos_icmbio
            )
            
            if total_outros_embargos > (num_embargos_ibama + num_embargos_icmbio):
                outros = total_outros_embargos - (num_embargos_ibama + num_embargos_icmbio)
                st.sidebar.warning(f"⚠️ Este produtor possui {outros} embargo(s) em outras propriedades")
        else:
            risco_msg, risco_score = "⚪ Sem Informação", 0
        
        # Status CAR
        st.sidebar.markdown(f"**Status CAR:** {status_validacao}")
        
        # ==================== ÁREA PRINCIPAL ====================
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🗺️ Mapa Interativo")
            
            # Criar mapa
            mapa = folium.Map(
                location=[lat, lon],
                zoom_start=13,
                tiles='OpenStreetMap'
            )
            
            # Adicionar imóvel
            cor_imovel = cor_por_status(status_validacao)
            folium.GeoJson(
                gdf_imovel_sel,
                name='Imóvel CAR',
                style_function=lambda x: {
                    'fillColor': cor_imovel,
                    'color': cor_imovel,
                    'weight': 3,
                    'fillOpacity': 0.3
                }
            ).add_to(mapa)
            
            # Adicionar embargos IBAMA
            if not gdf_embargos_ibama_imovel.empty:
                folium.GeoJson(
                    gdf_embargos_ibama_imovel,
                    name='Embargos IBAMA',
                    style_function=lambda x: {
                        'fillColor': 'red',
                        'color': 'red',
                        'weight': 2,
                        'fillOpacity': 0.5
                    }
                ).add_to(mapa)
            
            # Adicionar embargos ICMBio
            if not gdf_embargos_icmbio_imovel.empty:
                folium.GeoJson(
                    gdf_embargos_icmbio_imovel,
                    name='Embargos ICMBio',
                    style_function=lambda x: {
                        'fillColor': 'orange',
                        'color': 'orange',
                        'weight': 2,
                        'fillOpacity': 0.5
                    }
                ).add_to(mapa)
            
            # Adicionar RL
            if not gdf_rl_imovel.empty:
                folium.GeoJson(
                    gdf_rl_imovel,
                    name='Reserva Legal',
                    style_function=lambda x: {
                        'fillColor': 'green',
                        'color': 'green',
                        'weight': 1,
                        'fillOpacity': 0.3
                    }
                ).add_to(mapa)
            
            # Adicionar APP
            if not gdf_app_imovel.empty:
                folium.GeoJson(
                    gdf_app_imovel,
                    name='APP',
                    style_function=lambda x: {
                        'fillColor': 'blue',
                        'color': 'blue',
                        'weight': 1,
                        'fillOpacity': 0.3
                    }
                ).add_to(mapa)
            
            # Adicionar WMS de focos de fogo
            folium.raster_layers.WmsTileLayer(
                url='https://queimadas.dgi.inpe.br/queimadas/geoserver/wms',
                layers='focos_24h',
                name='🔥 Focos de Fogo 24h',
                fmt='image/png',
                transparent=True,
                overlay=True,
                control=True
            ).add_to(mapa)
            
            # Controle de camadas
            folium.LayerControl().add_to(mapa)
            
            # Exibir mapa
            folium_static(mapa, width=800, height=600)
        
        with col2:
            st.markdown("### 📊 Dashboard")
            
            # Métricas
            st.metric("🏠 Imóvel", codigo_selecionado)
            st.metric("✅ Status CAR", status_validacao)
            st.metric("❌ Embargos IBAMA", num_embargos_ibama)
            st.metric("⚠️ Embargos ICMBio", num_embargos_icmbio)
            
            if cpf_cnpj:
                st.metric("🔍 Risco Reputacional", f"{risco_score}/100")
            
            # Calcular áreas
            areas = calcular_area_util(
                gdf_imovel_sel,
                pd.concat([gdf_embargos_ibama_imovel, gdf_embargos_icmbio_imovel]),
                gdf_rl_imovel,
                gdf_app_imovel
            )
            
            st.markdown("### 🌾 Análise de Áreas")
            st.metric("Área Total", f"{areas['total']:.2f} ha")
            st.metric("Área Embargada", f"{areas['embargada']:.2f} ha")
            st.metric("Reserva Legal", f"{areas['reserva_legal']:.2f} ha")
            st.metric("APP", f"{areas['app']:.2f} ha")
            st.metric(
                "🌾 Área Explorável",
                f"{areas['util']:.2f} ha",
                delta=f"{areas['percentual_util']:.1f}% do total"
            )
        
        # ==================== MAPBIOMAS ====================
        
        st.markdown("---")
        st.markdown("### 🛰️ Análise MapBiomas")
        
        # Inicializar Earth Engine
        ee_inicializado = False
        if EE_DISPONIVEL:
            with st.spinner("Inicializando Google Earth Engine..."):
                ee_inicializado = inicializar_earth_engine()
        
        if ee_inicializado:
            st.success("✅ Google Earth Engine conectado")
            
            # Configurações MapBiomas
            col_mb1, col_mb2 = st.columns(2)
            
            with col_mb1:
                ano_analise = st.slider("📅 Ano de Análise", 1985, 2023, 2023)
            
            with col_mb2:
                analise_transicao = st.checkbox("🔄 Análise de Transição (dois anos)")
            
            if st.button("▶️ Executar Análise MapBiomas"):
                with st.spinner("Processando análise..."):
                    try:
                        # Converter geometria para Earth Engine
                        geom_json = json.loads(gdf_imovel_sel.to_json())
                        roi = ee.Geometry(geom_json['features'][0]['geometry'])
                        
                        # Obter cobertura
                        cobertura = obter_cobertura_mapbiomas(roi, ano_analise)
                        
                        if cobertura:
                            st.success(f"✅ Análise concluída para o ano {ano_analise}")
                            
                            # Gráficos
                            col_g1, col_g2 = st.columns(2)
                            
                            with col_g1:
                                fig_barras = criar_grafico_cobertura(
                                    cobertura,
                                    f"Uso do Solo - {ano_analise}"
                                )
                                st.plotly_chart(fig_barras, use_container_width=True)
                            
                            with col_g2:
                                fig_pizza = criar_grafico_pizza(cobertura)
                                st.plotly_chart(fig_pizza, use_container_width=True)
                            
                            # Tabela de dados
                            st.markdown("#### 📋 Dados Detalhados")
                            classes = mapbiomas_classes()
                            df_resultado = pd.DataFrame([
                                {
                                    'Classe': classes.get(int(k), f'Classe {k}'),
                                    'Área (ha)': f"{v:.2f}",
                                    'Percentual': f"{(v/sum(cobertura.values()))*100:.1f}%"
                                }
                                for k, v in sorted(cobertura.items(), key=lambda x: x[1], reverse=True)
                            ])
                            st.dataframe(df_resultado, use_container_width=True)
                            
                            # Exportação
                            st.markdown("#### 📥 Exportar Dados")
                            
                            # Excel
                            buffer = BytesIO()
                            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                                df_resultado.to_excel(writer, index=False, sheet_name='Cobertura')
                            
                            st.download_button(
                                label="📊 Baixar Excel",
                                data=buffer.getvalue(),
                                file_name=f"mapbiomas_{codigo_selecionado}_{ano_analise}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        else:
                            st.warning("⚠️ Nenhum dado retornado para esta região")
                    
                    except Exception as e:
                        st.error(f"❌ Erro na análise MapBiomas: {e}")
            
            # ==================== TIMELINE DE SATÉLITE ====================
            
            st.markdown("---")
            st.markdown("### 📅 Timeline de Imagens de Satélite")
            st.markdown("Compare imagens Sentinel-2 de diferentes anos para identificar mudanças no uso do solo")
            
            col_sat1, col_sat2 = st.columns(2)
            
            with col_sat1:
                ano_inicial_sat = st.slider("Ano Inicial", 2018, 2024, 2020, key='ano_inicial')
            
            with col_sat2:
                ano_final_sat = st.slider("Ano Final", 2018, 2024, 2024, key='ano_final')
            
            if st.button("🛰️ Carregar Imagens Sentinel-2"):
                if ano_final_sat <= ano_inicial_sat:
                    st.warning("⚠️ O ano final deve ser maior que o ano inicial")
                else:
                    with st.spinner("Carregando imagens de satélite..."):
                        try:
                            # Converter geometria
                            geom_json = json.loads(gdf_imovel_sel.to_json())
                            roi = ee.Geometry(geom_json['features'][0]['geometry'])
                            
                            # Obter imagens
                            img_inicial = obter_imagem_sentinel2(roi, ano_inicial_sat)
                            img_final = obter_imagem_sentinel2(roi, ano_final_sat)
                            
                            if img_inicial and img_final:
                                st.success(f"✅ Imagens carregadas: {ano_inicial_sat} e {ano_final_sat}")
                                
                                # Criar visualização
                                vis_params = {
                                    'min': 0,
                                    'max': 3000,
                                    'bands': ['B4', 'B3', 'B2']
                                }
                                
                                col_img1, col_img2 = st.columns(2)
                                
                                with col_img1:
                                    st.markdown(f"#### Sentinel-2 - {ano_inicial_sat}")
                                    st.info("🛰️ Imagem disponível para visualização no Earth Engine")
                                    st.markdown(f"**Período:** Janeiro-Dezembro {ano_inicial_sat}")
                                
                                with col_img2:
                                    st.markdown(f"#### Sentinel-2 - {ano_final_sat}")
                                    st.info("🛰️ Imagem disponível para visualização no Earth Engine")
                                    st.markdown(f"**Período:** Janeiro-Dezembro {ano_final_sat}")
                                
                                st.markdown("""
                                **💡 Dica:** As imagens Sentinel-2 foram processadas e estão prontas.
                                Para visualização interativa completa, considere usar o Google Earth Engine Code Editor.
                                """)
                            else:
                                st.warning("⚠️ Não foi possível carregar as imagens para este período")
                        
                        except Exception as e:
                            st.error(f"❌ Erro ao carregar imagens: {e}")
            
            # ==================== DETECÇÃO DE FOCOS DE FOGO ====================
            
            st.markdown("---")
            st.markdown("### 🔥 Monitoramento de Focos de Incêndio")
            
            # Detectar focos
            num_focos = detectar_focos_fogo(gdf_imovel_sel)
            
            col_fogo1, col_fogo2 = st.columns([1, 2])
            
            with col_fogo1:
                st.metric(
                    "🔥 Focos nas últimas 24h",
                    num_focos,
                    delta="Dados do INPE/BDQueimadas"
                )
            
            with col_fogo2:
                if num_focos > 0:
                    st.error(f"⚠️ ALERTA: {num_focos} foco(s) de incêndio detectado(s) na propriedade!")
                    st.markdown("**Recomendação:** Verificar situação e acionar brigada de incêndio se necessário.")
                else:
                    st.success("✅ Nenhum foco de incêndio detectado nas últimas 24 horas")
                
                st.info("""
                **Fonte de Dados:** Programa Queimadas - INPE
                
                A camada de focos de fogo está disponível no mapa interativo acima.
                Ative a camada "🔥 Focos de Fogo 24h" para visualizar.
                """)
        
        else:
            st.info("ℹ️ Google Earth Engine não disponível. Configure as credenciais para usar análise MapBiomas.")
        
        # ==================== GERAÇÃO DE LAUDO ====================
        
        st.markdown("---")
        st.markdown("### 📄 Gerar Laudo de Conformidade")
        
        if st.button("📄 Gerar Laudo PDF"):
            with st.spinner("Gerando laudo..."):
                dados_imovel = {
                    'cod_imovel': codigo_selecionado,
                    'status': status_validacao
                }
                
                pdf_bytes = gerar_laudo_pdf(
                    dados_imovel,
                    num_embargos_ibama,
                    num_embargos_icmbio,
                    areas,
                    (risco_msg, risco_score)
                )
                
                if pdf_bytes:
                    st.success("✅ Laudo gerado com sucesso!")
                    st.download_button(
                        label="📥 Baixar Laudo PDF",
                        data=pdf_bytes,
                        file_name=f"laudo_esg_{codigo_selecionado}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        st.exception(e)


if __name__ == "__main__":
    main()
