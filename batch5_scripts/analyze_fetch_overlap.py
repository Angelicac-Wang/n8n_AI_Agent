#!/usr/bin/env python3
import os
import json
import re

def extract_node_name_from_filename(filename):
    """從檔案名提取節點名稱"""
    # 移除副檔名
    name = filename.replace('.json', '')
    # 移除可能的前綴
    if name.startswith('n8n-nodes-base.'):
        name = name[15:]  # 移除 'n8n-nodes-base.' 前綴
    return name.lower()

def extract_node_name_from_content(file_path):
    """從檔案內容提取節點名稱"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 嘗試不同的欄位
        for field in ['name', 'displayName']:
            if field in data:
                name = data[field]
                # 清理名稱
                if name.startswith('n8n-nodes-base.'):
                    name = name[15:]
                return name.lower()
        
        return None
    except:
        return None

def analyze_duplicates():
    """分析第一次和第三次 fetch 的重複情況"""
    
    base_path = "/Users/angelicawang/Documents/n8n/n8n_json_schema"
    first_fetch_path = os.path.join(base_path, "node_schemas")
    third_fetch_path = os.path.join(base_path, "nodes_base_schemas")
    
    # 收集第一次 fetch 的節點
    first_fetch_nodes = {}
    if os.path.exists(first_fetch_path):
        for filename in os.listdir(first_fetch_path):
            if filename.endswith('.json') and not filename.startswith('.'):
                file_path = os.path.join(first_fetch_path, filename)
                node_name = extract_node_name_from_content(file_path)
                if node_name:
                    first_fetch_nodes[node_name] = {
                        'filename': filename,
                        'source': 'API',
                        'path': file_path
                    }
    
    # 收集第三次 fetch 的節點
    third_fetch_nodes = {}
    if os.path.exists(third_fetch_path):
        for filename in os.listdir(third_fetch_path):
            if filename.endswith('.json') and not filename.startswith('.'):
                file_path = os.path.join(third_fetch_path, filename)
                node_name = extract_node_name_from_content(file_path)
                if node_name:
                    third_fetch_nodes[node_name] = {
                        'filename': filename,
                        'source': 'nodes-base package',
                        'path': file_path
                    }
    
    # 分析重複和新增
    duplicates = []
    unique_to_first = []
    unique_to_third = []
    
    all_nodes = set(first_fetch_nodes.keys()) | set(third_fetch_nodes.keys())
    
    for node_name in all_nodes:
        in_first = node_name in first_fetch_nodes
        in_third = node_name in third_fetch_nodes
        
        if in_first and in_third:
            duplicates.append({
                'node': node_name,
                'first_file': first_fetch_nodes[node_name]['filename'],
                'third_file': third_fetch_nodes[node_name]['filename']
            })
        elif in_first and not in_third:
            unique_to_first.append({
                'node': node_name,
                'filename': first_fetch_nodes[node_name]['filename']
            })
        elif not in_first and in_third:
            unique_to_third.append({
                'node': node_name,
                'filename': third_fetch_nodes[node_name]['filename']
            })
    
    # 報告結果
    print(f"📊 重複分析結果:")
    print(f"第一次 fetch (API): {len(first_fetch_nodes)} 個節點")
    print(f"第三次 fetch (nodes-base): {len(third_fetch_nodes)} 個節點")
    print(f"重複的節點: {len(duplicates)} 個")
    print(f"僅在第一次 fetch: {len(unique_to_first)} 個")
    print(f"僅在第三次 fetch: {len(unique_to_third)} 個")
    
    print(f"\\n🔄 重複節點範例 (前10個):")
    for dup in duplicates[:10]:
        print(f"  {dup['node']}: {dup['first_file']} <-> {dup['third_file']}")
    
    print(f"\\n🆕 僅在第三次 fetch 的新節點 (前20個):")
    for unique in unique_to_third[:20]:
        print(f"  {unique['node']}: {unique['filename']}")
    
    print(f"\\n📋 僅在第一次 fetch 的節點 (前20個):")
    for unique in unique_to_first[:20]:
        print(f"  {unique['node']}: {unique['filename']}")
    
    # 詳細分析第三次 fetch 的新內容
    print(f"\\n🔍 第三次 fetch 新增內容分析:")
    
    # 按類別分析新節點
    categories = {}
    for unique in unique_to_third:
        node_name = unique['node']
        # 簡單的分類邏輯
        if 'trigger' in node_name:
            category = 'Triggers'
        elif any(word in node_name for word in ['google', 'microsoft', 'aws', 'azure']):
            category = 'Cloud Services'
        elif any(word in node_name for word in ['database', 'mysql', 'postgres', 'mongo']):
            category = 'Databases'
        elif any(word in node_name for word in ['email', 'mail', 'smtp']):
            category = 'Email'
        else:
            category = 'Others'
        
        if category not in categories:
            categories[category] = []
        categories[category].append(node_name)
    
    print(f"\\n📂 新節點分類:")
    for category, nodes in categories.items():
        print(f"  {category}: {len(nodes)} 個節點")
        for node in nodes[:5]:  # 顯示前5個
            print(f"    - {node}")
        if len(nodes) > 5:
            print(f"    ... 還有 {len(nodes) - 5} 個")
    
    # 重複率計算
    if len(third_fetch_nodes) > 0:
        overlap_rate = len(duplicates) / len(third_fetch_nodes) * 100
        new_content_rate = len(unique_to_third) / len(third_fetch_nodes) * 100
        print(f"\\n📈 統計:")
        print(f"重複率: {overlap_rate:.1f}%")
        print(f"新內容率: {new_content_rate:.1f}%")
    
    return {
        'duplicates': duplicates,
        'unique_to_first': unique_to_first,
        'unique_to_third': unique_to_third,
        'first_count': len(first_fetch_nodes),
        'third_count': len(third_fetch_nodes)
    }

if __name__ == "__main__":
    results = analyze_duplicates()