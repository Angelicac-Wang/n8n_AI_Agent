#!/usr/bin/env python3
"""
搜尋 npm 上的 n8n 社群節點套件
"""

import requests
import json

def search_n8n_community_nodes():
    """搜尋 npm registry 中的 n8n 社群節點"""
    try:
        # 使用更廣泛的搜尋條件
        search_terms = [
            'n8n-nodes-',
            'n8n-community-',
            '@n8n/',
            'n8n-node-'
        ]
        
        all_packages = []
        
        for term in search_terms:
            print(f"搜尋關鍵字: {term}")
            
            npm_url = "https://registry.npmjs.org/-/v1/search"
            params = {
                'text': term,
                'size': 100,
                'quality': 0.65,
                'popularity': 0.35,
                'maintenance': 0.35
            }
            
            response = requests.get(npm_url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                packages = result.get('objects', [])
                
                for pkg in packages:
                    package_info = pkg.get('package', {})
                    name = package_info.get('name', '')
                    
                    # 過濾真正的 n8n 相關套件
                    if any(keyword in name.lower() for keyword in ['n8n', 'node']):
                        keywords = package_info.get('keywords', [])
                        if any('n8n' in str(kw).lower() for kw in keywords):
                            all_packages.append(package_info)
                            
            print(f"  找到 {len(packages)} 個相關套件")
        
        # 去重複並排序
        unique_packages = {}
        for pkg in all_packages:
            name = pkg.get('name', '')
            if name not in unique_packages:
                unique_packages[name] = pkg
        
        sorted_packages = sorted(unique_packages.values(), 
                               key=lambda x: x.get('name', ''))
        
        print(f"\n=== 找到 {len(sorted_packages)} 個 n8n 相關套件 ===")
        
        community_nodes = []
        
        for pkg in sorted_packages:
            name = pkg.get('name', 'Unknown')
            description = pkg.get('description', 'No description')
            version = pkg.get('version', 'Unknown')
            keywords = pkg.get('keywords', [])
            
            # 檢查是否為社群節點
            is_community_node = (
                'n8n-nodes-' in name or
                'n8n-community-' in name or
                any('community' in str(kw).lower() for kw in keywords) or
                any('node' in str(kw).lower() for kw in keywords)
            )
            
            if is_community_node:
                community_nodes.append({
                    'name': name,
                    'version': version,
                    'description': description,
                    'keywords': keywords
                })
        
        print(f"\n=== 社群節點套件 ({len(community_nodes)} 個) ===")
        
        for i, node in enumerate(community_nodes[:20], 1):  # 只顯示前20個
            print(f"{i}. {node['name']} (v{node['version']})")
            print(f"   描述: {node['description']}")
            if node['keywords']:
                print(f"   關鍵字: {', '.join(str(kw) for kw in node['keywords'][:5])}")
            print()
            
        if len(community_nodes) > 20:
            print(f"... 還有 {len(community_nodes) - 20} 個套件")
            
        return community_nodes
        
    except Exception as e:
        print(f"錯誤: {e}")
        return []

def get_popular_n8n_integrations():
    """取得熱門的 n8n 整合"""
    print("\n=== 檢查官方 n8n 文檔中的整合 ===")
    
    try:
        # 嘗試從 n8n 官方 API 取得整合清單
        response = requests.get("https://api.n8n.io/api/nodes")
        
        if response.status_code == 200:
            nodes = response.json()
            print(f"官方 API 回應: {len(nodes)} 個項目")
            
            if isinstance(nodes, list) and len(nodes) > 0:
                print("前 10 個官方節點:")
                for i, node in enumerate(nodes[:10], 1):
                    if isinstance(node, dict):
                        name = node.get('name', node.get('displayName', 'Unknown'))
                        print(f"  {i}. {name}")
        else:
            print(f"無法取得官方節點清單 (狀態碼: {response.status_code})")
            
    except Exception as e:
        print(f"官方 API 錯誤: {e}")

if __name__ == "__main__":
    print("=== n8n 社群節點探索 ===")
    
    # 搜尋社群節點
    community_nodes = search_n8n_community_nodes()
    
    # 檢查官方整合
    get_popular_n8n_integrations()
    
    print(f"\n=== 總結 ===")
    print(f"找到 {len(community_nodes)} 個可安裝的社群節點套件")
    print("你的 n8n 伺服器支援安裝這些社群節點！")
    print("\n安裝方式:")
    print("1. 透過 n8n UI: http://140.115.54.44:5678/settings/community-nodes")
    print("2. 透過 Docker 命令: docker exec <container_id> npm install <package_name>")