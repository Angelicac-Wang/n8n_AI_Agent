import os
import json
import csv

def get_node_info_from_schemas(schema_folder="node_schemas"):
    """
    從 JSON Schema 檔案中提取所有節點的 displayName 和 description。
    """
    node_info = []
    if not os.path.exists(schema_folder):
        print(f"錯誤：找不到資料夾 '{schema_folder}'。")
        return []

    for filename in os.listdir(schema_folder):
        if filename.endswith(".json"):
            filepath = os.path.join(schema_folder, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 從 JSON 內容中獲取 displayName 和 description
                    display_name = data.get("displayName", "")
                    description = data.get("description", "")
                    
                    # 如果沒有 displayName，使用檔案名稱
                    if not display_name:
                        display_name = os.path.splitext(filename)[0]
                    
                    node_info.append({
                        "filename": filename,
                        "displayName": display_name,
                        "description": description
                    })
            except json.JSONDecodeError:
                print(f"錯誤：檔案 '{filename}' 不是有效的 JSON。")
            except Exception as e:
                print(f"錯誤：處理檔案 '{filename}' 時發生錯誤：{e}")
    return node_info

def save_node_info_to_file(node_info, output_file="node_info.json"):
    """
    將節點資訊保存到 JSON 檔案中
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(node_info, f, ensure_ascii=False, indent=2)
        print(f"節點資訊已保存到 '{output_file}'")
    except Exception as e:
        print(f"保存 JSON 檔案時發生錯誤：{e}")

def save_node_info_to_csv(node_info, output_file="node_info.csv"):
    """
    將節點資訊保存到 CSV 檔案中
    """
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # 寫入標題行
            writer.writerow(['檔案名稱', '顯示名稱', '描述'])
            # 寫入資料
            for node in node_info:
                writer.writerow([node['filename'], node['displayName'], node['description']])
        print(f"節點資訊已保存到 '{output_file}'")
    except Exception as e:
        print(f"保存 CSV 檔案時發生錯誤：{e}")

if __name__ == "__main__":
    node_info = get_node_info_from_schemas("./node_schemas")
    if node_info:
        print(f"已成功提取 {len(node_info)} 個節點的資訊")
        # 顯示前5個節點的資訊作為預覽
        print("\n前5個節點預覽：")
        for i, node in enumerate(node_info[:5]):
            print(f"{i+1}. {node['displayName']}")
            print(f"   描述：{node['description'][:100]}{'...' if len(node['description']) > 100 else ''}")
            print()
        
        # 保存到檔案
        save_node_info_to_file(node_info)
        
        # 也可以保存為 CSV 格式
        save_node_info_to_csv(node_info)
    else:
        print("沒有找到任何節點資訊。")