import requests
import json
import os

def get_all_nodes_data():
    """
    從 n8n API 獲取所有節點的原始資料
    """
    N8N_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzZTRkMzU5ZC02ZmU4LTRjOWMtYjlhMy02Yzk3ZTQ2YTE0NGIiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzU2ODI0OTcyfQ.FCIaEzrMY4cKDwCrX1EP0B4CMS7Y_gc3Uf-WfeP30rs"

    base_url = "http://140.115.54.44:5678"  # 實驗室的 n8n 伺服器位置
    endpoint = "/types/nodes.json"  # 已確認可用的端點
    url = f"{base_url}{endpoint}"
    
    headers = {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Accept": "application/json"
    }
    
    try:
        print(f"Fetching node data from: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # 檢查 HTTP 請求是否成功
        
        nodes_data = response.json()
        print(f"✅ Successfully retrieved {len(nodes_data)} nodes")
        return nodes_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching nodes from n8n API: {e}")
        return None

def save_nodes_to_json_files(nodes_data, output_dir="node_schemas"):
    """
    將每個節點的參數資訊儲存為單獨的 JSON 文件，作為知識庫。
    """
    if not nodes_data:
        print("❌ No nodes data to save")
        return

    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving node schemas to '{output_dir}'...")

    saved_count = 0
    for node in nodes_data:
        node_name = node.get("name")
        display_name = node.get("displayName", "unknown_node")

        if not node_name or not node.get("properties"):
            print(f"⚠️ Skipping malformed node data: {node_name}")
            continue

        # 整理出對模型有用的資訊
        node_schema = {
            "name": node_name,
            "displayName": display_name,
            "description": node.get("description", ""),
            "properties": node.get("properties")
        }

        # 創建一個易於閱讀的文件名，處理特殊字符和路徑
        safe_filename = node_name.replace('n8n-nodes-base.', '').replace('@n8n/n8n-nodes-langchain.', '').replace('/', '_').replace('\\', '_')
        filename = f"{safe_filename}.json"
        filepath = os.path.join(output_dir, filename)

        # 檢查檔案是否已存在
        if os.path.exists(filepath):
            print(f"  ↻ Updating {display_name} schema")
        else:
            print(f"  + Creating {display_name} schema")

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(node_schema, f, ensure_ascii=False, indent=2)
            saved_count += 1
        except Exception as e:
            print(f"❌ Error saving {filepath}: {e}")
    
    print(f"✅ Saved {saved_count} node schemas successfully.")

def main():
    """
    主程式：抓取 n8n 節點資料並儲存為 JSON 檔案
    """
    print("🚀 Starting n8n node schema extraction...")
    
    # 檢查是否已有現有的節點檔案
    if os.path.exists("node_schemas") and os.listdir("node_schemas"):
        existing_files = len([f for f in os.listdir("node_schemas") if f.endswith('.json')])
        print(f"📁 Found {existing_files} existing node schema files")
        
        # 如果有現有檔案，詢問是否要重新抓取
        print("\nOptions:")
        print("  [e] Use existing files (skip API fetch)")
        print("  [r] Re-fetch from API (overwrite existing)")
        user_input = input("Choose option (e/r) or press Enter for existing: ").lower().strip()
        
        if user_input == '' or user_input == 'e':
            print("✅ Using existing node schema files")
            print(f"✅ Total schemas available: {existing_files}")
            return True
    
    # 步驟 1: 從 n8n API 獲取節點資料
    nodes_data = get_all_nodes_data()
    
    if not nodes_data:
        print("❌ Failed to retrieve nodes data. Please check:")
        print("  - n8n server is running at http://140.115.54.44:5678")
        print("  - API key is valid and has proper permissions")
        print("  - Network connection is stable")
        return False
    
    # 步驟 2: 儲存節點資料為 JSON 檔案
    save_nodes_to_json_files(nodes_data)
    
    print("🎉 Node schema extraction completed!")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n📊 Summary:")
        print(f"  - Data source: n8n API at http://140.115.54.44:5678/types/nodes.json")
        print(f"  - Output directory: ./node_schemas/")
        print(f"  - File format: JSON with UTF-8 encoding")
        print("\n💡 Next steps:")
        print("  - Use these schemas to train AI models")
        print("  - Build documentation or API references")
        print("  - Create node validation tools")
    else:
        print("\n❌ Extraction failed. Please check the error messages above.")