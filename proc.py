"""
Funções auxiliares para processamento de dados CAR e embargos
Sistema de Compliance ESG - Rondônia
"""

import geopandas as gpd
import fiona
from shapely import wkb
import folium


def ler_geodataframe(gpkg_path, layer_name):
    """
    Lê camada de GeoPackage
    
    Args:
        gpkg_path (str): Caminho para o arquivo .gpkg
        layer_name (str): Nome da camada a ser lida
        
    Returns:
        gpd.GeoDataFrame: GeoDataFrame com a camada lida
    """
    return gpd.read_file(gpkg_path, layer=layer_name)


def selecionar_imovel_car(gdf, codigo, coluna_cod):
    """
    Seleciona imóvel e calcula bounds
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame com imóveis
        codigo (str): Código do imóvel a selecionar
        coluna_cod (str): Nome da coluna com códigos
        
    Returns:
        tuple: (gdf_sel, lat, lon, min_lat, max_lat, min_lon, max_lon)
    """
    gdf_sel = gdf[gdf[coluna_cod] == codigo].copy()
    bounds = gdf_sel.total_bounds  # minx, miny, maxx, maxy
    centroid = gdf_sel.geometry.centroid.iloc[0]
    return gdf_sel, centroid.y, centroid.x, bounds[1], bounds[3], bounds[0], bounds[2]


def inserir_geojson_folium(gdf, col_popup, label, layer_name, color, mapa):
    """
    Adiciona GeoJSON ao mapa Folium
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame a ser adicionado
        col_popup (str): Coluna para mostrar no popup
        label (str): Label para o popup
        layer_name (str): Nome da camada
        color (str): Cor da camada
        mapa (folium.Map): Mapa Folium
        
    Returns:
        folium.Map: Mapa atualizado
    """
    geojson = folium.GeoJson(
        gdf,
        name=layer_name,
        style_function=lambda x: {
            'fillColor': color,
            'color': color,
            'weight': 2,
            'fillOpacity': 0.4
        },
        tooltip=folium.GeoJsonTooltip(fields=[col_popup], aliases=[label])
    )
    geojson.add_to(mapa)
    return mapa


def mostrar_status(nome, quantidade):
    """
    Exibe status com emoji
    
    Args:
        nome (str): Nome do status
        quantidade (int): Quantidade de itens
        
    Returns:
        str: String formatada com emoji
    """
    emoji = "✅" if quantidade == 0 else "❌"
    return f"{emoji} {nome}: {quantidade}"


def validar_geometria(gdf):
    """
    Remove geometrias inválidas e converte Z para 2D
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame a validar
        
    Returns:
        gpd.GeoDataFrame: GeoDataFrame validado
    """
    def remove_z(geom):
        if geom and geom.has_z:
            return wkb.loads(wkb.dumps(geom, output_dimension=2))
        return geom
    
    gdf['geometry'] = gdf.geometry.apply(remove_z).buffer(0)
    return gdf[~gdf.geometry.is_empty].dropna(subset=['geometry'])


def contar_embargos_por_cpf(cpf_cnpj, gdf_embargos_ibama, gdf_embargos_icmbio):
    """
    Conta total de embargos de um CPF/CNPJ em todas as propriedades
    
    Args:
        cpf_cnpj (str): CPF/CNPJ do proprietário
        gdf_embargos_ibama (gpd.GeoDataFrame): Embargos IBAMA
        gdf_embargos_icmbio (gpd.GeoDataFrame): Embargos ICMBio
        
    Returns:
        int: Total de embargos
    """
    total_ibama = 0
    total_icmbio = 0
    
    if not gdf_embargos_ibama.empty and 'cpf_cnpj' in gdf_embargos_ibama.columns:
        total_ibama = gdf_embargos_ibama[
            gdf_embargos_ibama['cpf_cnpj'] == cpf_cnpj
        ].shape[0]
    
    if not gdf_embargos_icmbio.empty and 'cpf_cnpj' in gdf_embargos_icmbio.columns:
        total_icmbio = gdf_embargos_icmbio[
            gdf_embargos_icmbio['cpf_cnpj'] == cpf_cnpj
        ].shape[0]
    
    return total_ibama + total_icmbio


def calcular_risco_reputacional(cpf_cnpj, gdf_embargos_ibama, gdf_embargos_icmbio):
    """
    Calcula score de risco reputacional baseado em embargos
    
    Args:
        cpf_cnpj (str): CPF/CNPJ do proprietário
        gdf_embargos_ibama (gpd.GeoDataFrame): Embargos IBAMA
        gdf_embargos_icmbio (gpd.GeoDataFrame): Embargos ICMBio
        
    Returns:
        tuple: (mensagem, score)
    """
    total_embargos = contar_embargos_por_cpf(cpf_cnpj, gdf_embargos_ibama, gdf_embargos_icmbio)
    
    if total_embargos == 0:
        return "✅ Baixo Risco", 10
    elif total_embargos <= 2:
        return "⚠️ Médio Risco", 50
    else:
        return "❌ Alto Risco", 90


def calcular_area_util(gdf_imovel, gdf_embargos, gdf_rl, gdf_app):
    """
    Calcula área realmente explorável
    
    Args:
        gdf_imovel (gpd.GeoDataFrame): GeoDataFrame do imóvel
        gdf_embargos (gpd.GeoDataFrame): GeoDataFrame de embargos
        gdf_rl (gpd.GeoDataFrame): GeoDataFrame de Reserva Legal
        gdf_app (gpd.GeoDataFrame): GeoDataFrame de APP
        
    Returns:
        dict: Dicionário com áreas calculadas
    """
    area_total = gdf_imovel.geometry.area.sum() / 10000  # m² -> ha
    area_embargada = gdf_embargos.geometry.area.sum() / 10000 if not gdf_embargos.empty else 0
    area_rl = gdf_rl.geometry.area.sum() / 10000 if not gdf_rl.empty else 0
    area_app = gdf_app.geometry.area.sum() / 10000 if not gdf_app.empty else 0
    
    area_util = area_total - area_embargada - area_rl - area_app
    percentual = (area_util / area_total) * 100 if area_total > 0 else 0
    
    return {
        'total': area_total,
        'embargada': area_embargada,
        'reserva_legal': area_rl,
        'app': area_app,
        'util': area_util,
        'percentual_util': percentual
    }


def cor_por_status(status):
    """
    Retorna cor baseada no status de validação CAR
    
    Args:
        status (str): Status de validação
        
    Returns:
        str: Nome da cor
    """
    cores = {
        'Validado': 'green',
        'Em Análise': 'yellow',
        'Cancelado': 'red',
        'Declarado': 'gray'
    }
    return cores.get(status, 'white')
