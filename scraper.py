#!/usr/bin/env python3
"""
Scraper de Embargos IBAMA/ICMBio - Rondônia
Atualiza a base de dados local com informações recentes
"""

import requests
import geopandas as gpd
import pandas as pd
from shapely import wkb
from datetime import datetime
import os
import sys

# URLs oficiais (APIs públicas)
URL_IBAMA_EMBARGOS = "https://servicos.ibama.gov.br/ctf/publico/areasembargadas/downloadshape.php"
URL_ICMBIO_EMBARGOS = "https://geoserver.icmbio.gov.br/geoserver/ows"

GPKG_OUTPUT = "car_embargos.gpkg"
UF_FILTRO = "RO"  # Rondônia


def limpar_geometrias(gdf):
    """
    Remove geometrias inválidas e converte para 2D
    
    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame a limpar
        
    Returns:
        gpd.GeoDataFrame: GeoDataFrame limpo
    """
    def remove_z(geom):
        if geom and geom.has_z:
            return wkb.loads(wkb.dumps(geom, output_dimension=2))
        return geom
    
    print("  → Limpando geometrias...")
    gdf['geometry'] = gdf.geometry.apply(remove_z).buffer(0)
    gdf = gdf[~gdf.geometry.is_empty].dropna(subset=['geometry'])
    gdf = gdf[gdf.geometry.is_valid]
    
    return gdf


def baixar_embargos_ibama():
    """
    Baixa embargos do IBAMA e filtra por Rondônia
    
    Returns:
        gpd.GeoDataFrame: GeoDataFrame com embargos IBAMA
    """
    print("📥 Baixando embargos IBAMA...")
    
    try:
        # IBAMA disponibiliza via WFS
        params = {
            'service': 'WFS',
            'version': '2.0.0',
            'request': 'GetFeature',
            'typeName': 'embargos',
            'outputFormat': 'json',
            'cql_filter': f"uf='{UF_FILTRO}'"
        }
        
        response = requests.get(URL_IBAMA_EMBARGOS, params=params, timeout=60)
        
        if response.status_code == 200:
            gdf = gpd.read_file(response.text)
            gdf = limpar_geometrias(gdf)
            print(f"  ✅ {len(gdf)} embargos IBAMA baixados")
            return gdf
        else:
            print(f"  ❌ Erro HTTP {response.status_code}")
            return gpd.GeoDataFrame()
            
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return gpd.GeoDataFrame()


def baixar_embargos_icmbio():
    """
    Baixa embargos do ICMBio e filtra por Rondônia
    
    Returns:
        gpd.GeoDataFrame: GeoDataFrame com embargos ICMBio
    """
    print("📥 Baixando embargos ICMBio...")
    
    try:
        params = {
            'service': 'WFS',
            'version': '1.0.0',
            'request': 'GetFeature',
            'typeName': 'embargos_icmbio',
            'outputFormat': 'json',
            'cql_filter': f"uf='{UF_FILTRO}'"
        }
        
        response = requests.get(URL_ICMBIO_EMBARGOS, params=params, timeout=60)
        
        if response.status_code == 200:
            gdf = gpd.read_file(response.text)
            gdf = limpar_geometrias(gdf)
            print(f"  ✅ {len(gdf)} embargos ICMBio baixados")
            return gdf
        else:
            print(f"  ❌ Erro HTTP {response.status_code}")
            return gpd.GeoDataFrame()
            
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return gpd.GeoDataFrame()


def atualizar_geopackage():
    """
    Atualiza o GeoPackage com dados recentes
    
    Returns:
        bool: True se atualização foi bem-sucedida
    """
    print("🔄 Iniciando atualização da base de dados...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Baixar dados
    gdf_ibama = baixar_embargos_ibama()
    gdf_icmbio = baixar_embargos_icmbio()
    
    # Salvar no GeoPackage
    sucesso = False
    
    if not gdf_ibama.empty:
        try:
            gdf_ibama.to_file(GPKG_OUTPUT, layer='embargos_ibama', driver='GPKG')
            print(f"💾 Camada 'embargos_ibama' atualizada")
            sucesso = True
        except Exception as e:
            print(f"❌ Erro ao salvar embargos IBAMA: {e}")
    
    if not gdf_icmbio.empty:
        try:
            gdf_icmbio.to_file(GPKG_OUTPUT, layer='embargos_icmbio', driver='GPKG')
            print(f"💾 Camada 'embargos_icmbio' atualizada")
            sucesso = True
        except Exception as e:
            print(f"❌ Erro ao salvar embargos ICMBio: {e}")
    
    if sucesso:
        print("\n✅ Atualização concluída!")
        print(f"📊 Total: {len(gdf_ibama) + len(gdf_icmbio)} embargos em Rondônia")
    else:
        print("\n❌ Nenhum dado foi atualizado")
    
    return sucesso


if __name__ == "__main__":
    try:
        atualizar_geopackage()
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        sys.exit(1)
