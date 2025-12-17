#!/usr/bin/env python3
"""
Gerador de dados de exemplo para testes
Cria um GeoPackage com dados fictícios para demonstração
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, Point
from datetime import datetime
import random

def gerar_dados_exemplo():
    """
    Gera GeoPackage de exemplo com imóveis CAR e embargos fictícios
    Região: Rondônia (exemplo genérico)
    """
    
    print("🔧 Gerando dados de exemplo para testes...")
    
    # Coordenadas aproximadas de Rondônia (região central)
    lon_base = -63.0
    lat_base = -10.5
    
    # ==================== IMÓVEIS CAR ====================
    
    print("📍 Criando imóveis CAR...")
    
    imoveis_data = []
    
    for i in range(5):
        lon_offset = random.uniform(-0.5, 0.5)
        lat_offset = random.uniform(-0.5, 0.5)
        
        # Criar polígono simples (quadrado de ~10km x 10km)
        size = 0.09  # ~10km em graus
        coords = [
            (lon_base + lon_offset, lat_base + lat_offset),
            (lon_base + lon_offset + size, lat_base + lat_offset),
            (lon_base + lon_offset + size, lat_base + lat_offset + size),
            (lon_base + lon_offset, lat_base + lat_offset + size),
            (lon_base + lon_offset, lat_base + lat_offset)
        ]
        
        polygon = Polygon(coords)
        
        status_opcoes = ['Validado', 'Em Análise', 'Declarado', 'Cancelado']
        
        imoveis_data.append({
            'cod_imovel': f'RO-{1000 + i}',
            'cpf_cnpj': f'000.000.00{i}-00',
            'status_validacao': random.choice(status_opcoes),
            'area_ha': round(polygon.area * 111 * 111 / 10000, 2),  # Aproximação
            'geometry': polygon
        })
    
    gdf_imoveis = gpd.GeoDataFrame(imoveis_data, crs='EPSG:4326')
    
    # ==================== EMBARGOS IBAMA ====================
    
    print("⚠️ Criando embargos IBAMA...")
    
    embargos_ibama_data = []
    
    # Adicionar alguns embargos
    for i in range(3):
        # Pegar um imóvel aleatório
        imovel = imoveis_data[random.randint(0, len(imoveis_data) - 1)]
        
        # Criar embargo dentro do imóvel
        bounds = imovel['geometry'].bounds
        embargo_size = 0.02  # Menor que o imóvel
        
        embargo_coords = [
            (bounds[0] + 0.01, bounds[1] + 0.01),
            (bounds[0] + 0.01 + embargo_size, bounds[1] + 0.01),
            (bounds[0] + 0.01 + embargo_size, bounds[1] + 0.01 + embargo_size),
            (bounds[0] + 0.01, bounds[1] + 0.01 + embargo_size),
            (bounds[0] + 0.01, bounds[1] + 0.01)
        ]
        
        embargo_polygon = Polygon(embargo_coords)
        
        embargos_ibama_data.append({
            'cod_imovel': imovel['cod_imovel'],
            'cpf_cnpj': imovel['cpf_cnpj'],
            'data_embargo': datetime.now().date(),
            'area_ha': round(embargo_polygon.area * 111 * 111 / 10000, 2),
            'motivo': 'Desmatamento irregular',
            'geometry': embargo_polygon
        })
    
    gdf_embargos_ibama = gpd.GeoDataFrame(embargos_ibama_data, crs='EPSG:4326')
    
    # ==================== EMBARGOS ICMBio ====================
    
    print("🌳 Criando embargos ICMBio...")
    
    embargos_icmbio_data = []
    
    # Adicionar alguns embargos ICMBio
    for i in range(2):
        imovel = imoveis_data[random.randint(0, len(imoveis_data) - 1)]
        bounds = imovel['geometry'].bounds
        embargo_size = 0.015
        
        embargo_coords = [
            (bounds[2] - 0.03, bounds[3] - 0.03),
            (bounds[2] - 0.03 + embargo_size, bounds[3] - 0.03),
            (bounds[2] - 0.03 + embargo_size, bounds[3] - 0.03 + embargo_size),
            (bounds[2] - 0.03, bounds[3] - 0.03 + embargo_size),
            (bounds[2] - 0.03, bounds[3] - 0.03)
        ]
        
        embargo_polygon = Polygon(embargo_coords)
        
        embargos_icmbio_data.append({
            'cod_imovel': imovel['cod_imovel'],
            'cpf_cnpj': imovel['cpf_cnpj'],
            'data_embargo': datetime.now().date(),
            'area_ha': round(embargo_polygon.area * 111 * 111 / 10000, 2),
            'motivo': 'Dano à UC',
            'geometry': embargo_polygon
        })
    
    gdf_embargos_icmbio = gpd.GeoDataFrame(embargos_icmbio_data, crs='EPSG:4326')
    
    # ==================== RESERVA LEGAL ====================
    
    print("🌲 Criando áreas de Reserva Legal...")
    
    rl_data = []
    
    for imovel in imoveis_data:
        bounds = imovel['geometry'].bounds
        rl_size_x = 0.04
        rl_size_y = 0.04
        
        rl_coords = [
            (bounds[0], bounds[1]),
            (bounds[0] + rl_size_x, bounds[1]),
            (bounds[0] + rl_size_x, bounds[1] + rl_size_y),
            (bounds[0], bounds[1] + rl_size_y),
            (bounds[0], bounds[1])
        ]
        
        rl_polygon = Polygon(rl_coords)
        
        rl_data.append({
            'cod_imovel': imovel['cod_imovel'],
            'tipo': 'Reserva Legal',
            'area_ha': round(rl_polygon.area * 111 * 111 / 10000, 2),
            'geometry': rl_polygon
        })
    
    gdf_rl = gpd.GeoDataFrame(rl_data, crs='EPSG:4326')
    
    # ==================== APP ====================
    
    print("💧 Criando áreas de APP...")
    
    app_data = []
    
    for i, imovel in enumerate(imoveis_data[:3]):  # Apenas alguns com APP
        bounds = imovel['geometry'].bounds
        app_size_x = 0.02
        app_size_y = 0.02
        
        app_coords = [
            (bounds[2] - app_size_x, bounds[1]),
            (bounds[2], bounds[1]),
            (bounds[2], bounds[1] + app_size_y),
            (bounds[2] - app_size_x, bounds[1] + app_size_y),
            (bounds[2] - app_size_x, bounds[1])
        ]
        
        app_polygon = Polygon(app_coords)
        
        app_data.append({
            'cod_imovel': imovel['cod_imovel'],
            'tipo': 'APP',
            'area_ha': round(app_polygon.area * 111 * 111 / 10000, 2),
            'geometry': app_polygon
        })
    
    gdf_app = gpd.GeoDataFrame(app_data, crs='EPSG:4326')
    
    # ==================== SALVAR GEOPACKAGE ====================
    
    print("💾 Salvando GeoPackage...")
    
    gpkg_path = 'car_embargos.gpkg'
    
    gdf_imoveis.to_file(gpkg_path, layer='area_imovel', driver='GPKG')
    gdf_embargos_ibama.to_file(gpkg_path, layer='embargos_ibama', driver='GPKG')
    gdf_embargos_icmbio.to_file(gpkg_path, layer='embargos_icmbio', driver='GPKG')
    gdf_rl.to_file(gpkg_path, layer='reserva_legal', driver='GPKG')
    gdf_app.to_file(gpkg_path, layer='app', driver='GPKG')
    
    print(f"\n✅ Dados de exemplo criados com sucesso!")
    print(f"📁 Arquivo: {gpkg_path}")
    print(f"📊 Estatísticas:")
    print(f"   - {len(gdf_imoveis)} imóveis CAR")
    print(f"   - {len(gdf_embargos_ibama)} embargos IBAMA")
    print(f"   - {len(gdf_embargos_icmbio)} embargos ICMBio")
    print(f"   - {len(gdf_rl)} áreas de Reserva Legal")
    print(f"   - {len(gdf_app)} áreas de APP")
    print(f"\n🚀 Execute 'streamlit run app.py' para testar!")

if __name__ == "__main__":
    try:
        gerar_dados_exemplo()
    except Exception as e:
        print(f"\n❌ Erro ao gerar dados: {e}")
        import traceback
        traceback.print_exc()
