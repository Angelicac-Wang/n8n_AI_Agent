#!/usr/bin/env python3
"""
搜尋官方 n8n 核心套件和 LangChain 節點
"""

import requests
import json
import time
from pathlib import Path

def search_official_n8n_packages():
    """搜尋官方 n8n 套件"""
    
    print("🔍 搜尋官方 n8n 套件...")
    
    # 已知的官方套件列表
    official_packages = [
        "n8n",
        "n8n-core", 
        "n8n-editor-ui",
        "n8n-nodes-base",
        "n8n-workflow",
        "n8n-nodes-langchain",
        "@n8n/nodes-langchain",
        "n8n-design-system",
        "n8n-client-oauth2"
    ]
    
    package_details = []
    
    for package in official_packages:
        try:
            print(f"  檢查: {package}")
            url = f"https://registry.npmjs.org/{package}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get('dist-tags', {}).get('latest', '')
                
                if latest_version:
                    version_data = data['versions'][latest_version]
                    
                    package_info = {
                        'name': package,
                        'version': latest_version,
                        'description': version_data.get('description', ''),
                        'main': version_data.get('main', ''),
                        'files': version_data.get('files', []),
                        'dependencies': list(version_data.get('dependencies', {}).keys()),
                        'keywords': version_data.get('keywords', [])
                    }
                    
                    package_details.append(package_info)
                    print(f"    ✅ 版本: {latest_version}")
                else:
                    print(f"    ❌ 無法獲取版本資訊")
            else:
                print(f"    ❌ 套件不存在或無法訪問")
                
        except Exception as e:
            print(f"    ❌ 錯誤: {e}")
        
        time.sleep(0.3)
    
    return package_details

def download_official_packages(packages_to_download):
    """下載指定的官方套件"""
    
    print(f"\n📦 下載 {len(packages_to_download)} 個官方套件...")
    
    output_dir = Path("official_packages")
    output_dir.mkdir(exist_ok=True)
    
    downloaded = []
    
    for package_info in packages_to_download:
        package_name = package_info['name']
        version = package_info['version']
        
        try:
            print(f"  下載: {package_name}@{version}")
            
            # 獲取 tarball URL
            tarball_url = f"https://registry.npmjs.org/{package_name}/-/{package_name.split('/')[-1]}-{version}.tgz"
            
            # 如果是 scoped package，需要調整 URL
            if package_name.startswith('@'):
                scope, name = package_name.split('/')
                tarball_url = f"https://registry.npmjs.org/{package_name}/-/{name}-{version}.tgz"
            
            response = requests.get(tarball_url, timeout=30)
            
            if response.status_code == 200:
                # 儲存 tarball
                safe_name = package_name.replace('/', '_').replace('@', '')
                tarball_path = output_dir / f"{safe_name}-{version}.tgz"
                
                with open(tarball_path, 'wb') as f:
                    f.write(response.content)
                
                # 解壓縮
                import tarfile
                extract_dir = output_dir / safe_name
                extract_dir.mkdir(exist_ok=True)
                
                with tarfile.open(tarball_path, 'r:gz') as tar:
                    tar.extractall(extract_dir)
                
                downloaded.append({
                    'name': package_name,
                    'version': version,
                    'path': extract_dir,
                    'tarball': tarball_path
                })
                
                print(f"    ✅ 下載完成")
            else:
                print(f"    ❌ 下載失敗: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ 下載錯誤: {e}")
        
        time.sleep(0.5)
    
    return downloaded

def analyze_nodes_base_package():
    """特別分析 n8n-nodes-base 套件中的節點"""
    
    print(f"\n🔍 分析 n8n-nodes-base 套件中的節點...")
    
    nodes_base_dir = Path("official_packages/n8n-nodes-base/package/dist/nodes")
    
    if not nodes_base_dir.exists():
        print(f"  ❌ 找不到 nodes-base 目錄")
        return []
    
    # 搜尋所有 .node.js 檔案
    node_files = list(nodes_base_dir.glob("**/*.node.js"))
    
    print(f"  找到 {len(node_files)} 個節點檔案")
    
    nodes_info = []
    
    for node_file in node_files[:50]:  # 限制分析數量
        try:
            with open(node_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 簡單提取節點名稱
            if 'displayName:' in content:
                lines = content.split('\n')
                for line in lines:
                    if 'displayName:' in line:
                        # 提取 displayName
                        start = line.find("'") or line.find('"')
                        if start > 0:
                            quote_char = line[start]
                            end = line.find(quote_char, start + 1)
                            if end > 0:
                                display_name = line[start+1:end]
                                nodes_info.append({
                                    'file': node_file.name,
                                    'path': str(node_file.relative_to(nodes_base_dir)),
                                    'display_name': display_name
                                })
                                break
        except Exception as e:
            continue
    
    return nodes_info

def main():
    """主函數"""
    
    print("=" * 80)
    print("🏢 n8n 官方套件探索器")
    print("=" * 80)
    
    # 1. 搜尋官方套件
    official_packages = search_official_n8n_packages()
    
    print(f"\n📊 找到 {len(official_packages)} 個官方套件")
    
    # 2. 選擇需要下載的套件（特別是 nodes-base 和 langchain）
    priority_packages = []
    for pkg in official_packages:
        if any(keyword in pkg['name'] for keyword in ['nodes-base', 'langchain']):
            priority_packages.append(pkg)
    
    print(f"\n🎯 優先下載的套件: {len(priority_packages)} 個")
    
    # 3. 下載套件
    if priority_packages:
        downloaded = download_official_packages(priority_packages)
        
        # 4. 特別分析 nodes-base
        nodes_base_nodes = analyze_nodes_base_package()
        
        print(f"\n📋 n8n-nodes-base 分析結果:")
        print(f"  節點數量: {len(nodes_base_nodes)}")
        
        # 顯示部分節點
        for i, node in enumerate(nodes_base_nodes[:20]):
            print(f"    {i+1}. {node['display_name']} ({node['file']})")
        
        if len(nodes_base_nodes) > 20:
            print(f"    ... 還有 {len(nodes_base_nodes) - 20} 個節點")
        
        # 5. 儲存結果
        results = {
            'official_packages': official_packages,
            'downloaded_packages': downloaded,
            'nodes_base_analysis': nodes_base_nodes,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('official_packages_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 結果已儲存至: official_packages_analysis.json")
        
        # 6. 總結發現
        print(f"\n🎉 總結:")
        print(f"  官方套件: {len(official_packages)} 個")
        print(f"  下載的套件: {len(downloaded)} 個")
        print(f"  nodes-base 中的節點: {len(nodes_base_nodes)} 個")
        
        if len(nodes_base_nodes) > 0:
            print(f"  🎯 這些可能是你伺服器上現有 792 個節點的原始定義！")
            print(f"  📈 如果能提取完整的 schema，可能會獲得更詳細的節點定義")

if __name__ == "__main__":
    main()