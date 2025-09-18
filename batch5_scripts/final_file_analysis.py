#!/usr/bin/env python3
"""
詳細分析 n8n_json_schema 目錄下的所有檔案
統計各個來源的檔案數量，檢查重複，並驗證檔案有效性
"""

import os
import json
from pathlib import Path
from collections import defaultdict

def analyze_directory_structure():
    """分析目錄結構和檔案分布"""
    
    base_dir = Path(".")
    
    print("🔍 分析 n8n_json_schema 目錄結構...")
    print("=" * 80)
    
    # 統計各個目錄的檔案
    directories = {}
    
    for item in base_dir.iterdir():
        if item.is_dir():
            json_files = list(item.glob("**/*.json"))
            py_files = list(item.glob("**/*.py"))
            other_files = list(item.glob("**/*")) 
            other_files = [f for f in other_files if f.suffix not in ['.json', '.py'] and f.is_file()]
            
            directories[item.name] = {
                'json_files': len(json_files),
                'py_files': len(py_files),
                'other_files': len(other_files),
                'total_files': len(json_files) + len(py_files) + len(other_files)
            }
    
    # 根目錄的檔案
    root_json = list(base_dir.glob("*.json"))
    root_py = list(base_dir.glob("*.py"))
    root_other = list(base_dir.glob("*"))
    root_other = [f for f in root_other if f.suffix not in ['.json', '.py'] and f.is_file()]
    
    directories['根目錄'] = {
        'json_files': len(root_json),
        'py_files': len(root_py),
        'other_files': len(root_other),
        'total_files': len(root_json) + len(root_py) + len(root_other)
    }
    
    return directories

def check_json_file_validity():
    """檢查 JSON 檔案的有效性"""
    
    print("\n🔍 檢查 JSON 檔案有效性...")
    
    base_dir = Path(".")
    json_files = list(base_dir.glob("**/*.json"))
    
    valid_files = 0
    invalid_files = 0
    invalid_details = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json.load(f)
            valid_files += 1
        except Exception as e:
            invalid_files += 1
            invalid_details.append({
                'file': str(json_file),
                'error': str(e)[:100]
            })
    
    print(f"✅ 有效 JSON 檔案: {valid_files}")
    print(f"❌ 無效 JSON 檔案: {invalid_files}")
    
    if invalid_files > 0:
        print(f"\n⚠️ 無效檔案詳情 (前10個):")
        for detail in invalid_details[:10]:
            print(f"  {detail['file']}: {detail['error']}")
    
    return valid_files, invalid_files, invalid_details

def find_duplicate_files():
    """尋找重複的檔案（基於檔案名稱）"""
    
    print("\n🔍 檢查重複檔案...")
    
    base_dir = Path(".")
    all_files = list(base_dir.glob("**/*"))
    all_files = [f for f in all_files if f.is_file()]
    
    # 按檔案名分組
    name_groups = defaultdict(list)
    for file_path in all_files:
        name_groups[file_path.name].append(file_path)
    
    # 找出重複的檔案名
    duplicates = {name: paths for name, paths in name_groups.items() if len(paths) > 1}
    
    print(f"📊 重複檔案名統計:")
    print(f"  總檔案數: {len(all_files)}")
    print(f"  重複檔案名: {len(duplicates)}")
    
    if duplicates:
        print(f"\n🔍 重複檔案詳情 (前10個):")
        for i, (name, paths) in enumerate(list(duplicates.items())[:10]):
            print(f"  {i+1}. {name} ({len(paths)} 個)")
            for path in paths:
                print(f"     - {path}")
    
    return duplicates

def analyze_fetch_history():
    """分析 fetch 歷史"""
    
    print("\n📋 Fetch 歷史分析...")
    print("=" * 80)
    
    fetch_history = [
        {
            'batch': 1,
            'method': 'n8n 伺服器 API',
            'target': '所有已安裝節點',
            'result': 792,
            'location': 'node_schemas/',
            'description': '從你的 n8n 伺服器透過 API 獲取所有已安裝節點的 schema'
        },
        {
            'batch': 2, 
            'method': 'npm 社群套件 (第一批)',
            'target': '15個精選社群套件',
            'result': 27,
            'location': 'community_packages/ + extracted_node_schemas/',
            'description': '下載社群套件並從中提取節點 schema'
        },
        {
            'batch': 3,
            'method': 'npm 官方套件',
            'target': 'n8n-nodes-base + n8n-nodes-langchain',
            'result': 458,
            'location': 'official_packages/',
            'description': '下載官方核心節點套件'
        },
        {
            'batch': 4,
            'method': 'npm 社群套件 (第二批)',
            'target': '14個高價值社群套件',
            'result': 16,
            'location': 'additional_community_packages/ + additional_node_schemas/',
            'description': '下載更多專業化社群套件'
        },
        {
            'batch': 5,
            'method': '全面分析 nodes-base',
            'target': '官方核心節點完整提取',
            'result': 443,
            'location': 'nodes_base_schemas/',
            'description': '從官方 nodes-base 套件中提取所有節點的詳細 schema'
        }
    ]
    
    total_fetched = 0
    for i, fetch in enumerate(fetch_history):
        print(f"🔄 第 {fetch['batch']} 次 Fetch:")
        print(f"   方法: {fetch['method']}")
        print(f"   目標: {fetch['target']}")
        print(f"   結果: {fetch['result']} 個檔案")
        print(f"   位置: {fetch['location']}")
        print(f"   說明: {fetch['description']}")
        print()
        total_fetched += fetch['result']
    
    print(f"📊 總計:")
    print(f"   Fetch 次數: {len(fetch_history)}")
    print(f"   總獲取檔案: {total_fetched}")
    
    return fetch_history, total_fetched

def count_unique_schemas():
    """統計唯一的 schema 檔案"""
    
    print("\n🎯 統計唯一 Schema 檔案...")
    
    # 主要 schema 來源目錄
    schema_dirs = {
        'node_schemas': '原始 API Schema',
        'extracted_node_schemas': '第一批社群 Schema', 
        'additional_node_schemas': '第二批社群 Schema',
        'nodes_base_schemas': '官方 nodes-base Schema',
        'community_node_schemas': '社群 JSON Schema'
    }
    
    total_schemas = 0
    schema_counts = {}
    
    for dir_name, description in schema_dirs.items():
        dir_path = Path(dir_name)
        if dir_path.exists():
            json_files = list(dir_path.glob("*.json"))
            schema_counts[description] = len(json_files)
            total_schemas += len(json_files)
            print(f"📁 {description}: {len(json_files)} 個")
        else:
            schema_counts[description] = 0
            print(f"📁 {description}: 0 個 (目錄不存在)")
    
    print(f"\n🎯 唯一 Schema 總數: {total_schemas}")
    
    return schema_counts, total_schemas

def main():
    """主函數"""
    
    print("=" * 80)
    print("📊 n8n_json_schema 目錄完整分析報告")
    print("=" * 80)
    
    # 1. 目錄結構分析
    directories = analyze_directory_structure()
    
    print("\n📁 目錄結構:")
    total_json = 0
    total_py = 0
    total_other = 0
    
    for dir_name, stats in directories.items():
        print(f"  {dir_name}:")
        print(f"    JSON: {stats['json_files']}")
        print(f"    Python: {stats['py_files']}")
        print(f"    其他: {stats['other_files']}")
        print(f"    小計: {stats['total_files']}")
        
        total_json += stats['json_files']
        total_py += stats['py_files']
        total_other += stats['other_files']
    
    print(f"\n📊 總計:")
    print(f"  JSON 檔案: {total_json}")
    print(f"  Python 檔案: {total_py}")
    print(f"  其他檔案: {total_other}")
    print(f"  總檔案數: {total_json + total_py + total_other}")
    
    # 2. JSON 檔案有效性檢查
    valid_json, invalid_json, invalid_details = check_json_file_validity()
    
    # 3. 重複檔案檢查
    duplicates = find_duplicate_files()
    
    # 4. Fetch 歷史分析
    fetch_history, total_fetched = analyze_fetch_history()
    
    # 5. 唯一 schema 統計
    schema_counts, total_schemas = count_unique_schemas()
    
    # 6. 最終總結
    print("\n" + "=" * 80)
    print("🎉 最終總結")
    print("=" * 80)
    
    print(f"📋 工作回顧:")
    print(f"  執行了 {len(fetch_history)} 次資料獲取")
    print(f"  總共獲取了 {total_fetched} 個節點檔案")
    print(f"  最終產生了 {total_json} 個 JSON 檔案")
    print(f"  其中有效 JSON 檔案: {valid_json} 個")
    print(f"  唯一的 Schema 檔案: {total_schemas} 個")
    
    print(f"\n📊 檔案品質:")
    print(f"  JSON 檔案有效率: {(valid_json/total_json*100):.1f}%")
    print(f"  重複檔案名數量: {len(duplicates)}")
    
    print(f"\n🎯 達成情況:")
    print(f"  目標 Schema 數: 1157")
    print(f"  實際 Schema 數: {total_schemas}")
    print(f"  達成率: {(total_schemas/1157*100):.1f}%")
    
    # 7. 儲存報告
    report = {
        'directories': directories,
        'json_validation': {
            'valid': valid_json,
            'invalid': invalid_json,
            'invalid_details': invalid_details[:10]
        },
        'duplicates': {name: [str(p) for p in paths] for name, paths in list(duplicates.items())[:10]},
        'fetch_history': fetch_history,
        'schema_counts': schema_counts,
        'summary': {
            'total_json_files': total_json,
            'valid_json_files': valid_json,
            'total_schemas': total_schemas,
            'total_fetches': len(fetch_history),
            'total_fetched_files': total_fetched,
            'completion_rate': total_schemas/1157*100
        }
    }
    
    with open('final_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 詳細報告已儲存至: final_analysis_report.json")

if __name__ == "__main__":
    main()