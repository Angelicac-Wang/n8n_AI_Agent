import requests
import json
import os

def check_n8n_settings():
    """
    檢查 n8n 的設定
    """
    N8N_API_KEY = os.getenv('N8N_API_KEY')
    if not N8N_API_KEY:
        print("❌ Error: N8N_API_KEY environment variable not set")
        return None
    base_url = "http://140.115.54.44:5678"
    
    headers = {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Accept": "application/json"
    }
    
    print("🔍 檢查 n8n 伺服器設定...")
    print("-" * 50)
    
    try:
        response = requests.get(f"{base_url}/rest/settings", headers=headers, timeout=10)
        
        if response.status_code == 200:
            settings = response.json()
            print("✅ 成功獲取設定資訊！")
            
            if 'data' in settings:
                data = settings['data']
                
                print(f"\n📊 設定項目總數: {len(data)}")
                print("\n🔍 所有可用設定項目:")
                
                # 顯示所有設定鍵值
                for key in sorted(data.keys()):
                    value = data[key]
                    # 限制顯示長度，避免輸出太長
                    if isinstance(value, str) and len(value) > 100:
                        display_value = f"{value[:97]}..."
                    elif isinstance(value, (list, dict)):
                        display_value = f"{type(value).__name__} ({len(value)} items)"
                    else:
                        display_value = value
                    print(f"   📌 {key}: {display_value}")
                
                # 特別檢查社群相關設定
                print(f"\n" + "="*50)
                print("🔍 社群節點相關設定檢查:")
                
                community_related = {}
                package_related = {}
                node_related = {}
                
                for key, value in data.items():
                    key_lower = key.lower()
                    if 'community' in key_lower:
                        community_related[key] = value
                    elif 'package' in key_lower:
                        package_related[key] = value
                    elif 'node' in key_lower and 'external' in key_lower:
                        node_related[key] = value
                
                if community_related:
                    print("\n🎯 社群相關設定:")
                    for key, value in community_related.items():
                        print(f"   ✅ {key}: {value}")
                else:
                    print("\n❌ 未發現明確的社群節點設定")
                
                if package_related:
                    print("\n📦 套件相關設定:")
                    for key, value in package_related.items():
                        print(f"   📋 {key}: {value}")
                
                if node_related:
                    print("\n🔧 外部節點相關設定:")
                    for key, value in node_related.items():
                        print(f"   🔗 {key}: {value}")
                
                # 檢查版本資訊
                if 'versionCli' in data:
                    print(f"\n🏷️  n8n CLI 版本: {data['versionCli']}")
                
                # 檢查是否有 npm 或安裝相關設定
                install_related = [k for k in data.keys() if any(term in k.lower() for term in ['install', 'npm', 'registry'])]
                if install_related:
                    print("\n💾 安裝相關設定:")
                    for key in install_related:
                        print(f"   🔧 {key}: {data[key]}")
                
                # 檢查許可證相關
                license_related = [k for k in data.keys() if 'license' in k.lower() or 'enterprise' in k.lower()]
                if license_related:
                    print("\n📜 許可證相關設定:")
                    for key in license_related:
                        print(f"   📋 {key}: {data[key]}")
                
                # 保存完整設定到檔案供後續分析
                with open('n8n_settings_full.json', 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                print(f"\n💾 完整設定已儲存到: n8n_settings_full.json")
                
            else:
                print(f"⚠️  設定格式異常: {settings}")
                
        else:
            print(f"❌ 無法獲取設定: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"💥 錯誤: {e}")

if __name__ == "__main__":
    check_n8n_settings()