#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpa imagens antigas de treino mantendo apenas as mais recentes
"""

import os
from pathlib import Path
import shutil

def limpar_pasta(pasta: str, manter: int = 50):
    """
    Limpa pasta mantendo apenas as N imagens mais recentes
    
    Args:
        pasta: Nome da pasta
        manter: Quantas imagens manter (0 = deletar tudo)
    """
    pasta_path = Path(pasta)
    
    if not pasta_path.exists():
        print(f"❌ Pasta não existe: {pasta}")
        return
    
    # Lista todos os arquivos
    arquivos = list(pasta_path.glob("*.png")) + list(pasta_path.glob("*.jpg"))
    
    if not arquivos:
        print(f"✅ {pasta}/ já está vazia")
        return
    
    # Ordena por data de modificação (mais antigas primeiro)
    arquivos.sort(key=lambda x: x.stat().st_mtime)
    
    total = len(arquivos)
    
    if manter == 0:
        # Deleta tudo
        for arquivo in arquivos:
            arquivo.unlink()
        print(f"🗑️  {pasta}/ - {total} imagens deletadas")
    
    elif total > manter:
        # Deleta apenas as antigas
        deletar = arquivos[:-manter]
        
        for arquivo in deletar:
            arquivo.unlink()
        
        print(f"🗑️  {pasta}/ - {len(deletar)} imagens antigas deletadas, {manter} mantidas")
    
    else:
        print(f"✅ {pasta}/ - {total} imagens (abaixo do limite)")


def obter_tamanho_pasta(pasta: str) -> float:
    """Retorna tamanho da pasta em MB"""
    pasta_path = Path(pasta)
    
    if not pasta_path.exists():
        return 0
    
    total = sum(f.stat().st_size for f in pasta_path.rglob('*') if f.is_file())
    return total / (1024 * 1024)  # MB


def menu():
    """Menu interativo de limpeza"""
    
    pastas = [
        "exp_ganho_treino",
        "treino_ml", 
        "minimap_captures",
        "debug_deteccao",
        "analytics_data"
    ]
    
    print("\n" + "="*70)
    print("🗑️  LIMPEZA DE IMAGENS DE TREINO")
    print("="*70)
    
    # Mostra tamanhos
    print("\n📊 Uso de espaço:")
    total_mb = 0
    
    for pasta in pastas:
        tamanho = obter_tamanho_pasta(pasta)
        total_mb += tamanho
        
        if tamanho > 0:
            print(f"  📁 {pasta:25s}: {tamanho:7.2f} MB")
    
    print(f"  {'─'*40}")
    print(f"  📊 TOTAL: {total_mb:.2f} MB")
    
    print("\n" + "="*70)
    print("OPÇÕES:")
    print("="*70)
    print("1. 🗑️  Deletar TUDO de exp_ganho_treino (libera mais espaço)")
    print("2. 📦 Manter apenas 50 mais recentes (cada pasta)")
    print("3. 📦 Manter apenas 100 mais recentes (cada pasta)")
    print("4. 🗑️  Deletar TUDO de minimap_captures")
    print("5. 🗑️  Deletar TUDO de debug_deteccao")
    print("6. 🔥 DELETAR TUDO (CUIDADO!)")
    print("7. ⚙️  Personalizado")
    print("0. ❌ Cancelar")
    
    escolha = input("\n➡️  Escolha: ").strip()
    
    if escolha == '0':
        print("❌ Cancelado")
        return
    
    elif escolha == '1':
        limpar_pasta("exp_ganho_treino", manter=0)
    
    elif escolha == '2':
        for pasta in pastas:
            limpar_pasta(pasta, manter=50)
    
    elif escolha == '3':
        for pasta in pastas:
            limpar_pasta(pasta, manter=100)
    
    elif escolha == '4':
        limpar_pasta("minimap_captures", manter=0)
    
    elif escolha == '5':
        limpar_pasta("debug_deteccao", manter=0)
    
    elif escolha == '6':
        confirma = input("⚠️  DELETAR TUDO? (digite SIM): ")
        if confirma.upper() == "SIM":
            for pasta in pastas:
                limpar_pasta(pasta, manter=0)
            print("🔥 Tudo deletado!")
        else:
            print("❌ Cancelado")
    
    elif escolha == '7':
        print("\n📁 Pastas disponíveis:")
        for i, pasta in enumerate(pastas, 1):
            print(f"  {i}. {pasta}")
        
        pasta_idx = int(input("\nPasta (número): ")) - 1
        manter = int(input("Manter quantas imagens? (0 = deletar tudo): "))
        
        if 0 <= pasta_idx < len(pastas):
            limpar_pasta(pastas[pasta_idx], manter)
    
    else:
        print("❌ Opção inválida")
    
    # Mostra espaço liberado
    print("\n" + "="*70)
    print("📊 Espaço após limpeza:")
    novo_total = 0
    
    for pasta in pastas:
        tamanho = obter_tamanho_pasta(pasta)
        novo_total += tamanho
        
        if tamanho > 0:
            print(f"  📁 {pasta:25s}: {tamanho:7.2f} MB")
    
    print(f"  {'─'*40}")
    print(f"  📊 TOTAL: {novo_total:.2f} MB")
    
    if novo_total < total_mb:
        liberado = total_mb - novo_total
        print(f"\n✅ Liberados: {liberado:.2f} MB")
    
    print("="*70)


if __name__ == "__main__":
    menu()
