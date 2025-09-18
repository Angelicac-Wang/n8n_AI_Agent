#!/usr/bin/env python3
"""
檢查 n8n 社群節點和可安裝套件
"""

import requests
import json
import os

# 配置
BASE_URL = "http://140.115.54.44:5678"
JWT_TOKEN = os.getenv('N8N_JWT_TOKEN')
if not JWT_TOKEN:
    print("❌ Error: N8N_JWT_TOKEN environment variable not set")
    exit(1)

headers = {
    'Authorization': f'Bearer {JWT_TOKEN}',
    'Content-Type': 'application/json'
}

def check_installed_packages():
    """檢查已安裝的社群套件"""
    try:
        # 嘗試取得已安裝的社群套件
        response = requests.get(f"{BASE_URL}/rest/community-packages", headers=headers)
        print(f"已安裝社群套件 - 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            packages = response.json()
            print(f"已安裝社群套件數量: {len(packages.get('data', []))}")
            
            for package in packages.get('data', []):
                print(f"  - {package.get('packageName', 'Unknown')}: {package.get('installedVersion', 'Unknown version')}")
        else:
            print(f"回應內容: {response.text}")
            
    except Exception as e:
        print(f"錯誤: {e}")

def check_available_packages():
    """檢查可用的社群套件"""
    try:
        # 嘗試搜尋可用的社群套件
        response = requests.get(f"{BASE_URL}/rest/community-packages/search", 
                              headers=headers, params={'keyword': ''})
        print(f"\n可用社群套件搜尋 - 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"搜尋結果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"回應內容: {response.text}")
            
    except Exception as e:
        print(f"錯誤: {e}")

def check_npm_packages():
    """檢查 npm 上的 n8n 社群套件"""
    try:
        # 搜尋 npm registry 中的 n8n 社群套件
        npm_url = "https://registry.npmjs.org/-/v1/search"
        params = {
            'text': 'keywords:n8n-community-node-*',
            'size': 50
        }
        
        response = requests.get(npm_url, params=params)
        print(f"\nNPM 社群套件搜尋 - 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            packages = result.get('objects', [])
            print(f"找到 {len(packages)} 個 n8n 社群套件:")
            
            for pkg in packages[:10]:  # 只顯示前10個
                package_info = pkg.get('package', {})
                name = package_info.get('name', 'Unknown')
                description = package_info.get('description', 'No description')
                version = package_info.get('version', 'Unknown')
                
                print(f"  - {name} (v{version})")
                print(f"    {description}")
                print()
                
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    print("=== n8n 社群節點檢查 ===")
    print(f"伺服器: {BASE_URL}")
    print(f"版本: 1.110.1 (Docker)")
    print(f"社群節點功能: 已啟用")
    print()
    
    # 檢查已安裝的套件
    check_installed_packages()
    
    # 檢查可用的套件
    check_available_packages()
    
    # 檢查 npm 上的套件
    check_npm_packages()