#!/usr/bin/env python3
"""
n8n 社群節點 JSON Schema 提取器
從下載的 npm 套件中提取實際的 JSON schema 檔案
"""

import os
import json
import shutil
from pathlib import Path

def extract_json_schemas_from_npm():
    """從 npm 套件中提取 JSON schema 檔案"""
    
    base_dir = Path("community_packages")
    output_dir = Path("community_node_schemas")
    
    # 創建輸出目錄
    output_dir.mkdir(exist_ok=True)
    
    # 統計
    total_schemas = 0
    extracted_schemas = 0
    
    print("🔍 搜尋 npm 套件中的 JSON schema 檔案...")
    
    # 搜尋所有 .node.json 檔案
    node_json_files = list(base_dir.glob("**/*.node.json"))
    
    print(f"📋 找到 {len(node_json_files)} 個 .node.json 檔案")
    
    for json_file in node_json_files:
        try:
            # 解析檔案內容
            with open(json_file, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
            
            # 獲取節點名稱
            node_name = json_file.stem.replace('.node', '')
            
            # 創建輸出檔案名
            output_file = output_dir / f"{node_name}.json"
            
            # 複製檔案
            shutil.copy2(json_file, output_file)
            
            print(f"  ✅ 提取: {node_name} -> {output_file}")
            extracted_schemas += 1
            
        except Exception as e:
            print(f"  ❌ 錯誤處理 {json_file}: {e}")
    
    # 同時也搜尋其他可能的 JSON schema 檔案
    print("\n🔍 搜尋其他 JSON 定義檔案...")
    
    # 搜尋包含節點定義的 JSON 檔案
    other_json_files = []
    for json_file in base_dir.glob("**/*.json"):
        if ".node.json" not in str(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 檢查是否包含節點定義的特徵
                if isinstance(data, dict):
                    if ('displayName' in data and 'properties' in data) or \
                       ('description' in data and 'inputs' in data) or \
                       ('codex' in data and 'properties' in data):
                        other_json_files.append(json_file)
                        
            except:
                continue
    
    print(f"📋 找到 {len(other_json_files)} 個其他可能的節點定義檔案")
    
    for json_file in other_json_files:
        try:
            # 獲取相對路徑作為檔案名
            relative_path = json_file.relative_to(base_dir)
            safe_name = str(relative_path).replace('/', '_').replace('\\', '_')
            
            output_file = output_dir / safe_name
            
            # 複製檔案
            shutil.copy2(json_file, output_file)
            
            print(f"  ✅ 提取: {safe_name}")
            extracted_schemas += 1
            
        except Exception as e:
            print(f"  ❌ 錯誤處理 {json_file}: {e}")
    
    # 從 JavaScript 檔案中提取嵌入的 schema
    print("\n🔍 從 JavaScript 檔案中提取嵌入的 schema...")
    
    js_files = list(base_dir.glob("**/*.node.js"))
    js_extracted = 0
    
    for js_file in js_files:
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尋找 description 物件定義
            if 'description' in content and 'displayName' in content:
                node_name = js_file.stem.replace('.node', '')
                
                # 嘗試提取 description 物件
                # 這是一個簡化的提取方法
                start_idx = content.find('description')
                if start_idx != -1:
                    # 創建一個標記檔案表示這個 JS 檔案包含節點定義
                    marker_file = output_dir / f"{node_name}_from_js.txt"
                    
                    with open(marker_file, 'w', encoding='utf-8') as f:
                        f.write(f"JavaScript 節點檔案: {js_file}\n")
                        f.write(f"包含節點定義，但需要進一步解析\n")
                        f.write(f"檔案大小: {len(content)} 字符\n")
                    
                    print(f"  📝 記錄 JS 節點: {node_name}")
                    js_extracted += 1
            
        except Exception as e:
            print(f"  ❌ 錯誤處理 {js_file}: {e}")
    
    print(f"\n📊 提取結果:")
    print(f"  JSON Schema 檔案: {extracted_schemas}")
    print(f"  JavaScript 節點記錄: {js_extracted}")
    print(f"  總計: {extracted_schemas + js_extracted}")
    print(f"  輸出目錄: {output_dir}")
    
    return extracted_schemas, js_extracted

def analyze_existing_schemas():
    """分析現有的 schema 檔案"""
    
    print("\n📈 分析現有 schema 檔案分布:")
    
    # 原有的 node_schemas 目錄
    node_schemas_dir = Path("node_schemas")
    if node_schemas_dir.exists():
        node_schemas_count = len(list(node_schemas_dir.glob("*.json")))
        print(f"  原有 node_schemas: {node_schemas_count} 個")
    else:
        node_schemas_count = 0
        print(f"  原有 node_schemas: 0 個 (目錄不存在)")
    
    # 新提取的 community schemas
    community_schemas_dir = Path("community_node_schemas")
    if community_schemas_dir.exists():
        community_count = len(list(community_schemas_dir.glob("*.json")))
        community_txt_count = len(list(community_schemas_dir.glob("*.txt")))
        print(f"  新提取的社群 schemas: {community_count} 個 JSON")
        print(f"  JavaScript 節點記錄: {community_txt_count} 個")
    else:
        community_count = 0
        community_txt_count = 0
    
    total = node_schemas_count + community_count
    print(f"\n🎯 總計 JSON Schema: {total} 個")
    
    return {
        'original_schemas': node_schemas_count,
        'community_json_schemas': community_count,
        'community_js_nodes': community_txt_count,
        'total_json_schemas': total
    }

if __name__ == "__main__":
    print("=" * 60)
    print("📦 n8n 社群節點 JSON Schema 提取器")
    print("=" * 60)
    
    # 提取 JSON schemas
    extracted_json, extracted_js = extract_json_schemas_from_npm()
    
    # 分析總體情況
    analysis = analyze_existing_schemas()
    
    print("\n" + "=" * 60)
    print("🎉 提取完成總結")
    print("=" * 60)
    print(f"✅ 從 npm 套件提取的 JSON schemas: {extracted_json}")
    print(f"📝 記錄的 JavaScript 節點: {extracted_js}")
    print(f"📊 原有 schemas: {analysis['original_schemas']}")
    print(f"🎯 總計 JSON schemas: {analysis['total_json_schemas']}")
    print(f"💡 實際獲得的新 schema 數量: {extracted_json}")