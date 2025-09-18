#!/usr/bin/env python3
import os
import json
import re

def extract_node_info_from_js(js_file_path):
    """從 .node.js 檔案中提取節點基本資訊"""
    try:
        with open(js_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取 displayName
        display_name_match = re.search(r'displayName:\s*[\'"]([^\'"]+)[\'"]', content)
        display_name = display_name_match.group(1) if display_name_match else "Unknown"
        
        # 提取 name
        name_match = re.search(r'name:\s*[\'"]([^\'"]+)[\'"]', content)
        name = name_match.group(1) if name_match else display_name
        
        # 提取 description
        description_match = re.search(r'description:\s*[\'"]([^\'"]+)[\'"]', content)
        description = description_match.group(1) if description_match else f"Node for {display_name}"
        
        # 提取 version
        version_match = re.search(r'version:\s*(\d+(?:\.\d+)*)', content)
        version = float(version_match.group(1)) if version_match else 1.0
        
        # 提取 group
        group_match = re.search(r'group:\s*\[[\'"]([^\'"]+)[\'"]', content)
        group = [group_match.group(1)] if group_match else ["transform"]
        
        return {
            "displayName": display_name,
            "name": name,
            "description": description,
            "version": version,
            "group": group,
            "defaults": {
                "name": display_name
            }
        }
    except Exception as e:
        print(f"Error processing {js_file_path}: {e}")
        return None

def main():
    base_path = "/Users/angelicawang/Documents/n8n/n8n_json_schema"
    additional_packages_path = os.path.join(base_path, "additional_community_packages")
    second_schemas_path = os.path.join(base_path, "node_schemas", "second")
    
    # 找出所有 .node.js 檔案
    node_js_files = []
    for root, dirs, files in os.walk(additional_packages_path):
        for file in files:
            if file.endswith('.node.js'):
                node_js_files.append(os.path.join(root, file))
    
    print(f"找到 {len(node_js_files)} 個 .node.js 檔案")
    
    for js_file in node_js_files:
        # 檢查是否已經有對應的 .node.json 檔案
        base_name = os.path.basename(js_file).replace('.node.js', '')
        json_file_path = os.path.join(second_schemas_path, f"{base_name}.node.json")
        
        if not os.path.exists(json_file_path):
            print(f"創建缺失的 schema: {base_name}")
            
            # 從 .js 檔案提取資訊
            node_info = extract_node_info_from_js(js_file)
            
            if node_info:
                # 保存為 JSON 檔案
                with open(json_file_path, 'w', encoding='utf-8') as f:
                    json.dump(node_info, f, indent=2, ensure_ascii=False)
                print(f"✅ 已創建: {json_file_path}")
            else:
                print(f"❌ 無法處理: {js_file}")
        else:
            print(f"⏭️  已存在: {base_name}.node.json")

if __name__ == "__main__":
    main()