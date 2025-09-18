#!/usr/bin/env python3
"""
n8n 社群節點批量安裝腳本
透過 n8n API 嘗試安裝熱門社群節點
"""

import requests
import json
import time
import os

# n8n 伺服器配置
N8N_BASE_URL = "http://140.115.54.44:5678"
JWT_TOKEN = os.getenv('N8N_JWT_TOKEN')
if not JWT_TOKEN:
    print("❌ Error: N8N_JWT_TOKEN environment variable not set")
    exit(1)

headers = {
    'Authorization': f'Bearer {JWT_TOKEN}',
    'Content-Type': 'application/json'
}

# 熱門社群節點清單（基於之前的搜尋結果）
POPULAR_COMMUNITY_NODES = [
    # 資料處理和 API 相關
    "@apify/n8n-nodes-apify",
    "@brave/n8n-nodes-brave-search", 
    "@cloudconvert/n8n-nodes-cloudconvert",
    "@bitovi/n8n-nodes-excel",
    "@bitovi/n8n-nodes-google-search",
    "@bitovi/n8n-nodes-confluence",
    
    # AI 和機器學習相關
    "@bitovi/n8n-nodes-watsonx",
    "@bitovi/n8n-nodes-langfuse",
    "@bitovi/n8n-nodes-semantic-text-splitter",
    "@bitovi/n8n-nodes-markitdown",
    
    # 通訊和社交媒體
    "@devlikeapro/n8n-nodes-waha",
    "@devlikeapro/n8n-nodes-chatwoot",
    "@aldinokemal2104/n8n-nodes-gowa",
    "@donney521/n8n-nodes-xiaohongshu",
    
    # 商業和行銷工具
    "@deviobr/n8n-nodes-rdstation",
    "@bitovi/n8n-nodes-freshbooks",
    "@blotato/n8n-nodes-blotato",
    "@amonlibanio/n8n-nodes-cogfy",
    
    # 資料庫和基礎設施
    "@digital-boss/n8n-nodes-oracle",
    
    # 其他實用工具
    "n8n-nodes-browserless",
    "n8n-nodes-puppeteer", 
    "n8n-nodes-qrcode",
    "n8n-nodes-pdf",
    "n8n-nodes-jsonata",
    "n8n-nodes-crypto",
    "n8n-nodes-base64",
    "n8n-nodes-xml",
    "n8n-nodes-yaml",
    "n8n-nodes-uuid"
]

def test_community_api_endpoints():
    """測試各種社群節點相關的 API 端點"""
    print("=== 測試 n8n 社群節點 API 端點 ===")
    
    endpoints_to_test = [
        "/rest/community-packages",
        "/rest/community-packages/install", 
        "/rest/community-packages/uninstall",
        "/rest/community-packages/update",
        "/rest/community-packages/search",
        "/rest/nodes/packages",
        "/rest/nodes/community"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            # 測試 GET 請求
            response = requests.get(f"{N8N_BASE_URL}{endpoint}", headers=headers)
            print(f"GET {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  回應: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print(f"  回應: {response.text[:200]}...")
            elif response.status_code != 404:
                print(f"  錯誤: {response.text[:100]}")
                
        except Exception as e:
            print(f"  異常: {e}")
    
    print()

def attempt_package_installation(package_name):
    """嘗試安裝單個社群套件"""
    print(f"嘗試安裝: {package_name}")
    
    # 方法 1: 透過 REST API POST 安裝
    install_data = {
        "name": package_name,
        "version": "latest"
    }
    
    try:
        response = requests.post(
            f"{N8N_BASE_URL}/rest/community-packages", 
            headers=headers,
            json=install_data
        )
        
        print(f"  POST /rest/community-packages: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"  ✅ {package_name} 安裝成功")
            return True
        else:
            print(f"  ❌ 安裝失敗: {response.text[:100]}")
            
    except Exception as e:
        print(f"  ❌ 安裝異常: {e}")
    
    # 方法 2: 嘗試其他可能的安裝端點
    try:
        alt_response = requests.post(
            f"{N8N_BASE_URL}/rest/community-packages/install",
            headers=headers,
            json={"packageName": package_name}
        )
        
        print(f"  POST /rest/community-packages/install: {alt_response.status_code}")
        
        if alt_response.status_code in [200, 201]:
            print(f"  ✅ {package_name} 透過替代端點安裝成功")
            return True
        else:
            print(f"  ❌ 替代端點失敗: {alt_response.text[:100]}")
            
    except Exception as e:
        print(f"  ❌ 替代端點異常: {e}")
    
    return False

def check_installed_packages():
    """檢查目前已安裝的社群套件"""
    print("=== 檢查已安裝的社群套件 ===")
    
    try:
        response = requests.get(f"{N8N_BASE_URL}/rest/community-packages", headers=headers)
        
        if response.status_code == 200:
            packages = response.json()
            if isinstance(packages, dict) and 'data' in packages:
                installed = packages['data']
                print(f"已安裝 {len(installed)} 個社群套件:")
                for pkg in installed:
                    name = pkg.get('packageName', 'Unknown')
                    version = pkg.get('installedVersion', 'Unknown')
                    print(f"  - {name} (v{version})")
            else:
                print("無已安裝的社群套件")
        else:
            print(f"無法取得已安裝套件清單: {response.status_code}")
            print(f"回應: {response.text}")
            
    except Exception as e:
        print(f"錯誤: {e}")
    
    print()

def get_node_count():
    """取得目前節點數量"""
    try:
        response = requests.get(f"{N8N_BASE_URL}/types/nodes.json", headers=headers)
        if response.status_code == 200:
            nodes = response.json()
            return len(nodes)
    except:
        pass
    return 0

def main():
    print(f"=== n8n 社群節點批量安裝 ===")
    print(f"伺服器: {N8N_BASE_URL}")
    print(f"目標安裝: {len(POPULAR_COMMUNITY_NODES)} 個社群節點")
    print()
    
    # 記錄安裝前的節點數量
    initial_node_count = get_node_count()
    print(f"安裝前節點數量: {initial_node_count}")
    print()
    
    # 測試 API 端點
    test_community_api_endpoints()
    
    # 檢查已安裝的套件
    check_installed_packages()
    
    # 嘗試安裝社群節點
    print("=== 開始批量安裝社群節點 ===")
    
    successful_installs = []
    failed_installs = []
    
    for i, package in enumerate(POPULAR_COMMUNITY_NODES, 1):
        print(f"\n進度: {i}/{len(POPULAR_COMMUNITY_NODES)}")
        
        if attempt_package_installation(package):
            successful_installs.append(package)
            # 安裝成功後稍等一下
            time.sleep(2)
        else:
            failed_installs.append(package)
        
        # 每 5 個套件檢查一次狀態
        if i % 5 == 0:
            print(f"\n--- 中間檢查 ({i}/{len(POPULAR_COMMUNITY_NODES)}) ---")
            check_installed_packages()
            current_node_count = get_node_count()
            print(f"目前節點數量: {current_node_count} (增加了 {current_node_count - initial_node_count} 個)")
    
    # 最終結果
    print(f"\n=== 安裝結果總結 ===")
    print(f"成功安裝: {len(successful_installs)} 個")
    for pkg in successful_installs:
        print(f"  ✅ {pkg}")
    
    print(f"\n安裝失敗: {len(failed_installs)} 個") 
    for pkg in failed_installs:
        print(f"  ❌ {pkg}")
    
    # 最終檢查
    print(f"\n=== 最終狀態 ===")
    check_installed_packages()
    
    final_node_count = get_node_count()
    print(f"最終節點數量: {final_node_count}")
    print(f"新增節點數量: {final_node_count - initial_node_count}")
    
    if successful_installs:
        print(f"\n🎉 成功安裝了 {len(successful_installs)} 個社群節點!")
        print("請重新執行 fetchAllNodesSchema.py 來取得新的 schema")
    else:
        print("\n⚠️ 無法透過 API 自動安裝社群節點")
        print("可能需要透過 n8n UI 手動安裝: http://140.115.54.44:5678/settings/community-nodes")

if __name__ == "__main__":
    main()