#!/usr/bin/env python3
"""
批量下載優選的 n8n 社群節點套件
基於之前的搜尋結果，下載最有價值的套件
"""

import requests
import tarfile
import json
import time
from pathlib import Path

def download_priority_packages():
    """下載優先選擇的社群套件"""
    
    # 根據搜尋結果選擇的高價值套件
    priority_packages = [
        "@apify/n8n-nodes-apify",  # Apify 網頁爬蟲
        "@elevenlabs/n8n-nodes-elevenlabs",  # ElevenLabs AI 語音
        "@bitovi/n8n-nodes-excel",  # Excel 檔案處理
        "@bitovi/n8n-nodes-google-search",  # Google 搜尋
        "@cloudconvert/n8n-nodes-cloudconvert",  # 檔案轉換
        "@devlikeapro/n8n-nodes-chatwoot",  # Chatwoot 客服
        "@devlikeapro/n8n-nodes-waha",  # WhatsApp API
        "@formbricks/n8n-nodes-formbricks",  # 表單建構
        "@firefliesai/n8n-nodes-fireflies",  # 會議 AI 記錄
        "@digital-boss/n8n-nodes-pdf-merge",  # PDF 處理
        "@brave/n8n-nodes-brave-search",  # Brave 搜尋引擎
        "n8n-nodes-puppeteer",  # Puppeteer 自動化
        "n8n-nodes-azure-cosmos-db",  # Azure Cosmos DB
        "n8n-nodes-mongodb",  # MongoDB
        "n8n-nodes-jsonata",  # JSONata 資料轉換
    ]
    
    print(f"📦 開始下載 {len(priority_packages)} 個優選套件...")
    
    output_dir = Path("additional_community_packages")
    output_dir.mkdir(exist_ok=True)
    
    successful_downloads = []
    failed_downloads = []
    
    for i, package_name in enumerate(priority_packages):
        try:
            print(f"\n下載 {i+1}/{len(priority_packages)}: {package_name}")
            
            # 獲取套件資訊
            url = f"https://registry.npmjs.org/{package_name}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"  ❌ 套件不存在或無法訪問")
                failed_downloads.append(package_name)
                continue
            
            data = response.json()
            latest_version = data.get('dist-tags', {}).get('latest', '')
            
            if not latest_version:
                print(f"  ❌ 無法獲取版本資訊")
                failed_downloads.append(package_name)
                continue
            
            # 獲取 tarball URL
            version_data = data['versions'][latest_version]
            tarball_url = version_data['dist']['tarball']
            
            print(f"  版本: {latest_version}")
            print(f"  下載: {tarball_url}")
            
            # 下載 tarball
            response = requests.get(tarball_url, timeout=30)
            
            if response.status_code == 200:
                # 儲存檔案
                safe_name = package_name.replace('/', '_').replace('@', '')
                tarball_path = output_dir / f"{safe_name}-{latest_version}.tgz"
                
                with open(tarball_path, 'wb') as f:
                    f.write(response.content)
                
                # 解壓縮
                extract_dir = output_dir / safe_name
                extract_dir.mkdir(exist_ok=True)
                
                with tarfile.open(tarball_path, 'r:gz') as tar:
                    tar.extractall(extract_dir)
                
                successful_downloads.append({
                    'name': package_name,
                    'version': latest_version,
                    'description': version_data.get('description', ''),
                    'path': str(extract_dir)
                })
                
                print(f"  ✅ 下載成功")
            else:
                print(f"  ❌ 下載失敗: HTTP {response.status_code}")
                failed_downloads.append(package_name)
                
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
            failed_downloads.append(package_name)
        
        time.sleep(1)  # 避免過於頻繁的請求
    
    return successful_downloads, failed_downloads

def analyze_new_packages(downloaded_packages):
    """分析新下載的套件"""
    
    print(f"\n🔍 分析 {len(downloaded_packages)} 個新下載的套件...")
    
    total_nodes = 0
    total_js_files = 0
    package_analysis = []
    
    for pkg in downloaded_packages:
        try:
            pkg_path = Path(pkg['path'])
            
            # 搜尋 .node.js 檔案
            node_files = list(pkg_path.glob("**/*.node.js"))
            js_files = list(pkg_path.glob("**/*.js"))
            
            analysis = {
                'name': pkg['name'],
                'version': pkg['version'],
                'description': pkg['description'],
                'node_files': len(node_files),
                'total_js_files': len(js_files),
                'node_list': [f.name for f in node_files]
            }
            
            package_analysis.append(analysis)
            total_nodes += len(node_files)
            total_js_files += len(js_files)
            
            print(f"  📦 {pkg['name']}")
            print(f"     節點: {len(node_files)} 個")
            print(f"     JS檔案: {len(js_files)} 個")
            
            if node_files:
                print(f"     節點列表: {', '.join([f.name for f in node_files[:3]])}{'...' if len(node_files) > 3 else ''}")
            
        except Exception as e:
            print(f"  ❌ 分析 {pkg['name']} 失敗: {e}")
    
    print(f"\n📊 統計結果:")
    print(f"  成功下載的套件: {len(downloaded_packages)}")
    print(f"  總節點檔案: {total_nodes}")
    print(f"  總 JS 檔案: {total_js_files}")
    
    return package_analysis

def extract_schemas_from_new_packages():
    """從新套件中提取 schema"""
    
    print(f"\n🔧 從新套件中提取節點 schema...")
    
    base_dir = Path("additional_community_packages")
    output_dir = Path("additional_node_schemas")
    output_dir.mkdir(exist_ok=True)
    
    # 搜尋所有 .node.js 檔案
    node_files = list(base_dir.glob("**/*.node.js"))
    
    print(f"  找到 {len(node_files)} 個節點檔案")
    
    extracted_schemas = []
    
    for node_file in node_files:
        try:
            with open(node_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 簡單提取節點資訊
            node_info = {}
            
            # 提取 displayName
            if "displayName:" in content:
                lines = content.split('\n')
                for line in lines:
                    if 'displayName:' in line and ("'" in line or '"' in line):
                        quote_char = "'" if "'" in line else '"'
                        start = line.find(quote_char) + 1
                        end = line.find(quote_char, start)
                        if end > start:
                            node_info['displayName'] = line[start:end]
                            break
            
            # 提取 name
            if "name:" in content:
                lines = content.split('\n')
                for line in lines:
                    if 'name:' in line and ("'" in line or '"' in line):
                        quote_char = "'" if "'" in line else '"'
                        start = line.find(quote_char) + 1
                        end = line.find(quote_char, start)
                        if end > start:
                            node_info['name'] = line[start:end]
                            break
            
            # 提取 description
            if "description:" in content:
                lines = content.split('\n')
                for line in lines:
                    if 'description:' in line and ("'" in line or '"' in line):
                        quote_char = "'" if "'" in line else '"'
                        start = line.find(quote_char) + 1
                        end = line.find(quote_char, start)
                        if end > start:
                            node_info['description'] = line[start:end]
                            break
            
            if node_info:
                # 儲存提取的資訊
                safe_name = node_file.stem.replace('.node', '')
                output_file = output_dir / f"{safe_name}_schema.json"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(node_info, f, indent=2, ensure_ascii=False)
                
                extracted_schemas.append(node_info)
                print(f"    ✅ {node_info.get('displayName', safe_name)}")
            
        except Exception as e:
            print(f"    ❌ 提取 {node_file.name} 失敗: {e}")
    
    print(f"\n📊 提取結果: {len(extracted_schemas)} 個新 schema")
    
    return extracted_schemas

def main():
    """主函數"""
    
    print("=" * 80)
    print("🚀 n8n 社群節點大規模下載器")
    print("=" * 80)
    
    # 1. 下載優選套件
    downloaded, failed = download_priority_packages()
    
    print(f"\n📊 下載結果:")
    print(f"  成功: {len(downloaded)} 個")
    print(f"  失敗: {len(failed)} 個")
    
    if failed:
        print(f"\n❌ 失敗的套件:")
        for pkg in failed:
            print(f"    - {pkg}")
    
    # 2. 分析套件
    if downloaded:
        analysis = analyze_new_packages(downloaded)
        
        # 3. 提取 schema
        extracted_schemas = extract_schemas_from_new_packages()
        
        # 4. 計算總數
        print(f"\n" + "=" * 80)
        print("🎯 最終統計")
        print("=" * 80)
        
        # 之前的數據
        original_schemas = 792  # 原始 API
        community_schemas = 30   # 之前的社群套件
        official_nodes = 458     # 官方 nodes-base
        new_schemas = len(extracted_schemas)  # 新的社群套件
        
        total_schemas = original_schemas + community_schemas + new_schemas
        
        print(f"📊 Schema 數量統計:")
        print(f"  原始 API Schema: {original_schemas}")
        print(f"  之前社群 Schema: {community_schemas}")
        print(f"  新增社群 Schema: {new_schemas}")
        print(f"  官方 nodes-base: {official_nodes} (可能重複)")
        print(f"  總計: {total_schemas}")
        
        print(f"\n🎉 進度:")
        print(f"  目前 Schema 數: {total_schemas}")
        print(f"  官方目標數: 1157")
        print(f"  達成率: {(total_schemas/1157*100):.1f}%")
        print(f"  還需要: {max(0, 1157-total_schemas)} 個")
        
        # 5. 儲存結果
        results = {
            'downloaded_packages': downloaded,
            'failed_packages': failed,
            'package_analysis': analysis,
            'extracted_schemas': extracted_schemas,
            'statistics': {
                'original_schemas': original_schemas,
                'previous_community': community_schemas,
                'new_community': new_schemas,
                'official_nodes': official_nodes,
                'total': total_schemas,
                'target': 1157,
                'completion_rate': total_schemas/1157*100
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('batch_download_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 詳細結果已儲存至: batch_download_results.json")

if __name__ == "__main__":
    main()