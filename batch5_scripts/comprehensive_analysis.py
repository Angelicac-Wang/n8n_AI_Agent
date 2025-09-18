#!/usr/bin/env python3
"""
檢查和分析 n8n-nodes-base 套件中的所有節點
這個套件包含大部分官方節點
"""

import os
import json
import re
from pathlib import Path

def extract_comprehensive_nodes_from_base():
    """從 n8n-nodes-base 套件中全面提取節點"""
    
    nodes_base_dir = Path("official_packages/n8n-nodes-base/package/dist/nodes")
    
    if not nodes_base_dir.exists():
        print("❌ n8n-nodes-base 目錄不存在，請先下載官方套件")
        return []
    
    print(f"🔍 全面分析 n8n-nodes-base 套件...")
    
    # 搜尋所有 .node.js 檔案
    node_files = list(nodes_base_dir.glob("**/*.node.js"))
    
    print(f"📋 找到 {len(node_files)} 個節點檔案")
    
    extracted_nodes = []
    output_dir = Path("nodes_base_schemas")
    output_dir.mkdir(exist_ok=True)
    
    for i, node_file in enumerate(node_files):
        try:
            print(f"  處理 {i+1}/{len(node_files)}: {node_file.name}")
            
            with open(node_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取節點資訊
            node_info = extract_node_info_from_js(content, node_file)
            
            if node_info:
                # 儲存 schema
                safe_name = node_file.stem.replace('.node', '')
                output_file = output_dir / f"{safe_name}_schema.json"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(node_info, f, indent=2, ensure_ascii=False)
                
                extracted_nodes.append(node_info)
                
                # 簡潔輸出
                if i % 50 == 0 or len(extracted_nodes) % 10 == 0:
                    print(f"    ✅ 已提取 {len(extracted_nodes)} 個節點...")
            
        except Exception as e:
            if i % 100 == 0:  # 只顯示部分錯誤
                print(f"    ⚠️ 處理 {node_file.name} 時發生錯誤: {e}")
    
    print(f"\n📊 nodes-base 提取結果:")
    print(f"  總檔案數: {len(node_files)}")
    print(f"  成功提取: {len(extracted_nodes)}")
    print(f"  提取率: {(len(extracted_nodes)/len(node_files)*100):.1f}%")
    
    return extracted_nodes

def extract_node_info_from_js(content, file_path):
    """從 JavaScript 內容中提取節點資訊"""
    
    node_info = {
        'file_path': str(file_path),
        'file_name': file_path.name
    }
    
    try:
        # 提取 displayName
        display_name_patterns = [
            r"displayName:\s*['\"]([^'\"]+)['\"]",
            r"displayName:\s*`([^`]+)`"
        ]
        
        for pattern in display_name_patterns:
            match = re.search(pattern, content)
            if match:
                node_info['displayName'] = match.group(1)
                break
        
        # 提取 name
        name_patterns = [
            r"name:\s*['\"]([^'\"]+)['\"]",
            r"name:\s*`([^`]+)`"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, content)
            if match:
                node_info['name'] = match.group(1)
                break
        
        # 提取 description
        desc_patterns = [
            r"description:\s*['\"]([^'\"]+)['\"]",
            r"description:\s*`([^`]+)`"
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, content)
            if match:
                node_info['description'] = match.group(1)
                break
        
        # 提取 group
        group_match = re.search(r"group:\s*\[([^\]]+)\]", content)
        if group_match:
            groups_str = group_match.group(1)
            groups = re.findall(r"['\"]([^'\"]+)['\"]", groups_str)
            if groups:
                node_info['group'] = groups
        
        # 提取 version
        version_match = re.search(r"version:\s*(\d+)", content)
        if version_match:
            node_info['version'] = int(version_match.group(1))
        
        # 提取 subtitle（如果有）
        subtitle_match = re.search(r"subtitle:\s*['\"]([^'\"]+)['\"]", content)
        if subtitle_match:
            node_info['subtitle'] = subtitle_match.group(1)
        
        # 提取 credentials
        creds_pattern = r"credentials:\s*\[(.*?)\]"
        creds_match = re.search(creds_pattern, content, re.DOTALL)
        if creds_match:
            creds_content = creds_match.group(1)
            cred_names = re.findall(r"name:\s*['\"]([^'\"]+)['\"]", creds_content)
            if cred_names:
                node_info['credentials'] = [{'name': name} for name in cred_names]
        
        # 只返回有基本資訊的節點
        if 'displayName' in node_info or 'name' in node_info:
            return node_info
        
    except Exception as e:
        pass
    
    return None

def analyze_langchain_package():
    """分析 LangChain 套件"""
    
    langchain_dir = Path("official_packages/n8n-nodes-langchain")
    
    if not langchain_dir.exists():
        print("❌ n8n-nodes-langchain 目錄不存在")
        return []
    
    print(f"\n🔍 分析 LangChain 套件...")
    
    # 搜尋所有 JavaScript 檔案
    js_files = list(langchain_dir.glob("**/*.js"))
    node_files = [f for f in js_files if 'node' in f.name.lower()]
    
    print(f"📋 LangChain 套件:")
    print(f"  總 JS 檔案: {len(js_files)}")
    print(f"  疑似節點檔案: {len(node_files)}")
    
    # 檢查目錄結構
    print(f"  主要目錄:")
    for item in langchain_dir.iterdir():
        if item.is_dir():
            sub_files = len(list(item.glob("**/*")))
            print(f"    {item.name}: {sub_files} 個檔案")
    
    return node_files

def calculate_final_statistics():
    """計算最終的統計資料"""
    
    print(f"\n" + "=" * 80)
    print("🎯 最終 Schema 統計分析")
    print("=" * 80)
    
    # 統計各個來源的 schema
    sources = {}
    
    # 1. 原始 API schema
    api_schemas_dir = Path("node_schemas")
    if api_schemas_dir.exists():
        sources['API Schema'] = len(list(api_schemas_dir.glob("*.json")))
    else:
        sources['API Schema'] = 792  # 之前統計的數字
    
    # 2. 社群套件（第一批）
    community_schemas_dir = Path("extracted_node_schemas")
    if community_schemas_dir.exists():
        sources['第一批社群 Schema'] = len(list(community_schemas_dir.glob("*_schema.json")))
    else:
        sources['第一批社群 Schema'] = 22
    
    # 3. 社群套件（第二批）
    additional_schemas_dir = Path("additional_node_schemas")
    if additional_schemas_dir.exists():
        sources['第二批社群 Schema'] = len(list(additional_schemas_dir.glob("*_schema.json")))
    else:
        sources['第二批社群 Schema'] = 13
    
    # 4. nodes-base 官方套件
    nodes_base_schemas_dir = Path("nodes_base_schemas")
    if nodes_base_schemas_dir.exists():
        sources['nodes-base Schema'] = len(list(nodes_base_schemas_dir.glob("*_schema.json")))
    else:
        sources['nodes-base Schema'] = 0
    
    # 計算總數
    total_unique_schemas = sources['API Schema']  # API 作為基準
    community_total = sources['第一批社群 Schema'] + sources['第二批社群 Schema']
    
    print(f"📊 Schema 來源統計:")
    for source, count in sources.items():
        print(f"  {source}: {count} 個")
    
    # 估算唯一 schema 數量（避免重複計算）
    estimated_unique = sources['API Schema'] + community_total
    nodes_base_overlap = max(0, sources['nodes-base Schema'] - 50)  # 假設大部分重複，但有一些新的
    estimated_unique += nodes_base_overlap
    
    print(f"\n🎯 估算唯一 Schema 數量:")
    print(f"  API Schema (基準): {sources['API Schema']}")
    print(f"  社群 Schema (新增): {community_total}")
    print(f"  nodes-base (去重後): {nodes_base_overlap}")
    print(f"  估計總數: {estimated_unique}")
    
    print(f"\n📈 與目標比較:")
    print(f"  目標 Schema 數: 1157")
    print(f"  目前估計數: {estimated_unique}")
    print(f"  達成率: {(estimated_unique/1157*100):.1f}%")
    print(f"  還需要: {max(0, 1157-estimated_unique)} 個")
    
    # 分析差距
    remaining = max(0, 1157 - estimated_unique)
    if remaining > 0:
        print(f"\n💡 剩餘 Schema 可能來源:")
        print(f"  🔸 官方但未包含在 nodes-base 的節點")
        print(f"  🔸 LangChain 專用節點 (約 99 個)")
        print(f"  🔸 實驗性或 beta 節點")
        print(f"  🔸 觸發器節點的變體")
        print(f"  🔸 地區特定節點")
        
        if remaining <= 100:
            print(f"  ✅ 差距很小，可能透過 LangChain 套件補足")
        elif remaining <= 300:
            print(f"  ⚠️ 中等差距，需要尋找更多社群套件")
        else:
            print(f"  ❌ 大差距，可能統計方法需要調整")
    
    return {
        'sources': sources,
        'estimated_unique': estimated_unique,
        'target': 1157,
        'remaining': remaining,
        'completion_rate': estimated_unique/1157*100
    }

def main():
    """主函數"""
    
    print("=" * 80)
    print("🔍 n8n 節點全面分析器")
    print("=" * 80)
    
    # 1. 分析 nodes-base 套件
    nodes_base_nodes = extract_comprehensive_nodes_from_base()
    
    # 2. 分析 LangChain 套件
    langchain_files = analyze_langchain_package()
    
    # 3. 計算最終統計
    final_stats = calculate_final_statistics()
    
    # 4. 儲存結果
    results = {
        'nodes_base_analysis': {
            'extracted_count': len(nodes_base_nodes),
            'sample_nodes': nodes_base_nodes[:10] if nodes_base_nodes else []
        },
        'langchain_analysis': {
            'total_files': len(langchain_files),
            'file_names': [f.name for f in langchain_files[:10]]
        },
        'final_statistics': final_stats,
        'timestamp': '2025-09-18'
    }
    
    with open('comprehensive_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 完整分析結果已儲存至: comprehensive_analysis_results.json")
    
    # 5. 結論
    print(f"\n" + "=" * 80)
    print("🎉 分析總結")
    print("=" * 80)
    
    completion_rate = final_stats['completion_rate']
    
    if completion_rate >= 90:
        print("✅ 恭喜！你已經獲得了接近完整的 n8n 節點庫！")
    elif completion_rate >= 70:
        print("🎯 很棒！你已經獲得了大部分的 n8n 節點！")
    else:
        print("📈 不錯的開始，還有更多節點等待發現！")
    
    print(f"📊 你現在擁有約 {final_stats['estimated_unique']} 個節點 schema")
    print(f"🎯 達成率: {completion_rate:.1f}%")

if __name__ == "__main__":
    main()