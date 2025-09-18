import requests
import json

def test_n8n_community_support():
    """
    測試 n8n 伺服器是否支援社群節點功能
    """
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzZTRkMzU5ZC02ZmU4LTRjOWMtYjlhMy02Yzk3ZTQ2YTE0NGIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU2ODI0OTcyfQ.FCIaEzrMY4cKDwCrX1EP0B4CMS7Y_gc3Uf-WfeP30rs"
    base_url = "http://140.115.54.44:5678"
    
    headers = {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Accept": "application/json"
    }
    
    # 測試不同的 API 端點
    endpoints_to_test = [
        "/rest/community-node-types",     # 官方社群節點 API
        "/community-node-types",          # 簡化路徑
        "/api/community-node-types",      # 可能的替代路徑
        "/rest/settings",                 # 設定 API，可能包含社群節點配置
        "/rest/node-types",              # 節點類型 API
        "/webhook-test",                  # 基本連線測試
    ]
    
    print("🔍 測試 n8n 伺服器社群節點支援狀況...")
    print(f"📍 伺服器: {base_url}")
    print(f"🔑 API 金鑰: {N8N_API_KEY[:20]}...")
    print("-" * 50)
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        print(f"\n🌐 測試端點: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   ✅ 成功！返回列表，項目數量: {len(data)}")
                        if len(data) > 0:
                            print(f"   📋 第一個項目: {list(data[0].keys()) if isinstance(data[0], dict) else str(data[0])[:100]}")
                    elif isinstance(data, dict):
                        print(f"   ✅ 成功！返回物件，鍵值: {list(data.keys())}")
                        # 檢查是否包含社群節點相關資訊
                        if any(key for key in data.keys() if 'community' in key.lower() or 'package' in key.lower()):
                            print(f"   🎯 發現社群相關設定: {[k for k in data.keys() if 'community' in k.lower() or 'package' in k.lower()]}")
                    else:
                        print(f"   ✅ 成功！返回: {str(data)[:100]}")
                except json.JSONDecodeError:
                    print(f"   ⚠️  返回非 JSON 格式: {response.text[:100]}")
            elif response.status_code == 401:
                print(f"   🔐 需要認證 (可能端點存在但需要不同權限)")
            elif response.status_code == 404:
                print(f"   ❌ 端點不存在")
            elif response.status_code == 403:
                print(f"   🚫 禁止存取 (端點存在但權限不足)")
            else:
                print(f"   ⚠️  其他錯誤: {response.text[:100]}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ 請求超時")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 連線錯誤")
        except Exception as e:
            print(f"   💥 未知錯誤: {e}")
    
    # 額外測試：檢查版本資訊
    print(f"\n" + "=" * 50)
    print("🔍 檢查 n8n 版本和功能支援...")
    
    # 嘗試獲取 n8n 版本資訊
    version_endpoints = [
        "/rest/active-workflows",
        "/healthz",
        "/metrics", 
        "/rest/workflows",
    ]
    
    for endpoint in version_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🌐 測試: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            print(f"   狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                # 檢查回應標頭是否包含版本資訊
                if 'x-n8n-version' in response.headers:
                    print(f"   📦 n8n 版本: {response.headers['x-n8n-version']}")
                
                # 對於特定端點，顯示更多資訊
                if endpoint == "/healthz":
                    print(f"   💚 健康檢查: {response.text}")
                elif endpoint == "/rest/workflows":
                    try:
                        data = response.json()
                        if isinstance(data, dict) and 'data' in data:
                            print(f"   📊 工作流數量: {len(data['data'])}")
                    except:
                        pass
                        
        except Exception as e:
            print(f"   ❌ 錯誤: {e}")

if __name__ == "__main__":
    test_n8n_community_support()