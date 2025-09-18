#!/usr/bin/env python3
"""
全面搜尋 n8n 節點的工具
探索各種可能的節點來源，包括官方和社群節點
"""

import requests
import json
import time
from pathlib import Path

def search_npm_packages_comprehensive():
    """全面搜尋 npm 上的 n8n 相關套件"""
    
    print("🔍 全面搜尋 npm 上的 n8n 相關套件...")
    
    # 多個搜尋關鍵字組合
    search_terms = [
        "n8n-nodes",
        "n8n-workflow", 
        "n8n-automation",
        "n8n-integration",
        "n8n node",
        "n8n trigger",
        "n8n-community",
        "@n8n",
        "n8n-custom",
        "workflow automation",
        "n8n connector"
    ]
    
    all_packages = set()
    
    for term in search_terms:
        try:
            print(f"  搜尋: {term}")
            url = f"https://registry.npmjs.org/-/v1/search?text={term}&size=50"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                packages = data.get('objects', [])
                
                for pkg in packages:
                    package_info = pkg.get('package', {})
                    name = package_info.get('name', '')
                    description = package_info.get('description', '')
                    
                    # 篩選真正的 n8n 節點套件
                    if (('n8n' in name.lower() or 'n8n' in description.lower()) and
                        ('node' in name.lower() or 'node' in description.lower() or
                         'workflow' in description.lower() or 'automation' in description.lower())):
                        all_packages.add(name)
                        
                print(f"    找到 {len(packages)} 個結果")
                
        except Exception as e:
            print(f"  ❌ 搜尋 {term} 失敗: {e}")
        
        time.sleep(0.5)  # 避免 API 限制
    
    print(f"\n📦 總共找到 {len(all_packages)} 個獨特的 n8n 相關套件")
    
    return sorted(list(all_packages))

def search_official_n8n_packages():
    """搜尋官方 n8n 組織的套件"""
    
    print("\n🔍 搜尋官方 n8n 組織的套件...")
    
    # 搜尋 @n8n scope 下的所有套件
    official_packages = []
    
    try:
        # 搜尋 @n8n/ 開頭的套件
        url = "https://registry.npmjs.org/-/v1/search?text=scope:n8n&size=50"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            packages = data.get('objects', [])
            
            for pkg in packages:
                package_info = pkg.get('package', {})
                name = package_info.get('name', '')
                description = package_info.get('description', '')
                
                official_packages.append({
                    'name': name,
                    'description': description,
                    'version': package_info.get('version', ''),
                    'keywords': package_info.get('keywords', [])
                })
        
        print(f"  找到 {len(official_packages)} 個官方套件")
        
    except Exception as e:
        print(f"  ❌ 搜尋官方套件失敗: {e}")
    
    return official_packages

def check_github_n8n_repo():
    """檢查 n8n 官方 GitHub repository"""
    
    print("\n🔍 檢查 n8n 官方 GitHub repository...")
    
    try:
        # GitHub API 獲取 n8n/n8n repository 資訊
        url = "https://api.github.com/repos/n8n-io/n8n/contents/packages/nodes-base/nodes"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            node_folders = []
            for item in data:
                if item.get('type') == 'dir':
                    node_folders.append(item.get('name'))
            
            print(f"  GitHub 上找到 {len(node_folders)} 個節點資料夾")
            return node_folders
        else:
            print(f"  ❌ GitHub API 回應: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"  ❌ 檢查 GitHub 失敗: {e}")
        return []

def analyze_package_details(package_name):
    """分析單個套件的詳細資訊"""
    
    try:
        url = f"https://registry.npmjs.org/{package_name}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # 獲取最新版本資訊
            latest_version = data.get('dist-tags', {}).get('latest', '')
            versions = data.get('versions', {})
            
            if latest_version and latest_version in versions:
                version_data = versions[latest_version]
                
                return {
                    'name': package_name,
                    'version': latest_version,
                    'description': version_data.get('description', ''),
                    'keywords': version_data.get('keywords', []),
                    'dependencies': list(version_data.get('dependencies', {}).keys()),
                    'has_n8n_dependency': any('n8n' in dep for dep in version_data.get('dependencies', {}).keys()),
                    'main': version_data.get('main', ''),
                    'files': version_data.get('files', [])
                }
        
        return None
        
    except Exception as e:
        print(f"    ❌ 分析 {package_name} 失敗: {e}")
        return None

def comprehensive_node_search():
    """執行全面的節點搜尋"""
    
    print("=" * 80)
    print("🚀 全面 n8n 節點搜尋器")
    print("=" * 80)
    
    # 1. 搜尋社群套件
    community_packages = search_npm_packages_comprehensive()
    
    # 2. 搜尋官方套件
    official_packages = search_official_n8n_packages()
    
    # 3. 檢查 GitHub
    github_nodes = check_github_n8n_repo()
    
    # 4. 分析套件詳情
    print(f"\n🔍 分析 {len(community_packages)} 個社群套件詳情...")
    
    detailed_packages = []
    for i, pkg_name in enumerate(community_packages[:50]):  # 限制分析數量避免過長
        print(f"  分析 {i+1}/{min(50, len(community_packages))}: {pkg_name}")
        details = analyze_package_details(pkg_name)
        if details:
            detailed_packages.append(details)
        time.sleep(0.2)  # 避免 API 限制
    
    # 5. 統計和分析
    print("\n" + "=" * 80)
    print("📊 搜尋結果統計")
    print("=" * 80)
    
    print(f"🔍 社群套件: {len(community_packages)} 個")
    print(f"🏢 官方套件: {len(official_packages)} 個") 
    print(f"🐙 GitHub 節點資料夾: {len(github_nodes)} 個")
    print(f"📦 分析的詳細套件: {len(detailed_packages)} 個")
    
    # 6. 篩選真正的節點套件
    actual_node_packages = []
    for pkg in detailed_packages:
        if (pkg['has_n8n_dependency'] or 
            any('node' in kw.lower() for kw in pkg['keywords']) or
            'n8n-nodes' in pkg['name']):
            actual_node_packages.append(pkg)
    
    print(f"✅ 真正的節點套件: {len(actual_node_packages)} 個")
    
    # 7. 儲存結果
    results = {
        'community_packages': community_packages,
        'official_packages': official_packages,
        'github_nodes': github_nodes,
        'detailed_analysis': detailed_packages,
        'actual_node_packages': actual_node_packages,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open('comprehensive_node_search.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 結果已儲存至: comprehensive_node_search.json")
    
    # 8. 推薦下載的套件
    print(f"\n💡 推薦下載的新套件:")
    downloaded_packages = {
        'n8n-nodes-chatwork', 'n8n-nodes-scrapeless', 'n8n-nodes-openpix',
        'n8n-nodes-taz', 'n8n-nodes-launix', 'n8n-nodes-binance',
        'n8n-nodes-lexware', 'n8n-nodes-cometapi', 'woztell-sanuker',
        'n8n-nodes-zalo-user-v3'
    }
    
    new_packages = []
    for pkg in actual_node_packages:
        if pkg['name'] not in downloaded_packages:
            new_packages.append(pkg)
    
    for i, pkg in enumerate(new_packages[:10]):  # 顯示前10個
        print(f"  {i+1}. {pkg['name']}")
        print(f"     描述: {pkg['description'][:60]}...")
        print(f"     版本: {pkg['version']}")
    
    print(f"\n🎯 總結:")
    print(f"  已下載套件: {len(downloaded_packages)} 個")
    print(f"  可下載的新套件: {len(new_packages)} 個")
    print(f"  潛在新節點數量: 估計 {len(new_packages) * 2} - {len(new_packages) * 5} 個")
    
    return results

if __name__ == "__main__":
    results = comprehensive_node_search()