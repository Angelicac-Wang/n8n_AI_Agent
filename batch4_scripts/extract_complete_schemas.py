#!/usr/bin/env python3
import os
import json
import re
import subprocess

def extract_complete_node_definition(js_file_path):
    """從 .node.js 檔案中提取完整的節點定義"""
    try:
        with open(js_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 嘗試解析 node.js 檔案的結構
        node_definition = {}
        
        # 提取基本資訊
        display_name_match = re.search(r'displayName:\s*[\'"]([^\'"]+)[\'"]', content)
        if display_name_match:
            node_definition['displayName'] = display_name_match.group(1)
        
        name_match = re.search(r'name:\s*[\'"]([^\'"]+)[\'"]', content)
        if name_match:
            node_definition['name'] = name_match.group(1)
        
        description_match = re.search(r'description:\s*[\'"]([^\'"]+)[\'"]', content)
        if description_match:
            node_definition['description'] = description_match.group(1)
        
        version_match = re.search(r'version:\s*(\d+(?:\.\d+)*)', content)
        if version_match:
            node_definition['version'] = float(version_match.group(1))
        
        # 提取 group
        group_match = re.search(r'group:\s*\[([^\]]+)\]', content)
        if group_match:
            group_str = group_match.group(1)
            groups = re.findall(r'[\'"]([^\'"]+)[\'"]', group_str)
            node_definition['group'] = groups
        
        # 提取 icon
        icon_match = re.search(r'icon:\s*[\'"]([^\'"]+)[\'"]', content)
        if icon_match:
            node_definition['icon'] = icon_match.group(1)
        
        # 提取 subtitle
        subtitle_match = re.search(r'subtitle:\s*[\'"]([^\'"]+)[\'"]', content)
        if subtitle_match:
            node_definition['subtitle'] = subtitle_match.group(1)
        
        # 提取 inputs/outputs
        inputs_match = re.search(r'inputs:\s*\[([^\]]+)\]', content)
        if inputs_match:
            inputs_str = inputs_match.group(1)
            inputs = re.findall(r'[\'"]([^\'"]+)[\'"]', inputs_str)
            node_definition['inputs'] = inputs
        
        outputs_match = re.search(r'outputs:\s*\[([^\]]+)\]', content)
        if outputs_match:
            outputs_str = outputs_match.group(1)
            outputs = re.findall(r'[\'"]([^\'"]+)[\'"]', outputs_str)
            node_definition['outputs'] = outputs
        
        # 提取 credentials
        credentials_pattern = r'credentials:\s*\[\s*\{[^}]*name:\s*[\'"]([^\'"]+)[\'"][^}]*required:\s*(true|false)[^}]*\}'
        credentials_match = re.search(credentials_pattern, content)
        if credentials_match:
            node_definition['credentials'] = [{
                'name': credentials_match.group(1),
                'required': credentials_match.group(2) == 'true'
            }]
        
        # 提取 defaults
        defaults_match = re.search(r'defaults:\s*\{[^}]*name:\s*[\'"]([^\'"]+)[\'"]', content)
        if defaults_match:
            node_definition['defaults'] = {
                'name': defaults_match.group(1)
            }
        
        return node_definition
        
    except Exception as e:
        print(f"Error processing {js_file_path}: {e}")
        return None

def extract_properties_from_descriptions(base_path, node_name):
    """從 Descriptions 資料夾中提取 properties"""
    try:
        # 尋找相關的描述檔案
        desc_files = []
        for root, dirs, files in os.walk(base_path):
            if 'Descriptions' in root or 'descriptions' in root:
                for file in files:
                    if file.endswith('.js'):
                        desc_files.append(os.path.join(root, file))
        
        properties = []
        
        for desc_file in desc_files:
            try:
                with open(desc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找 exports 定義
                exports_pattern = r'exports\.(\w+)\s*=\s*\[(.*?)\];'
                exports_matches = re.finditer(exports_pattern, content, re.DOTALL)
                
                for match in exports_matches:
                    export_name = match.group(1)
                    export_content = match.group(2)
                    
                    # 解析每個 property 物件
                    property_pattern = r'\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
                    property_matches = re.finditer(property_pattern, export_content)
                    
                    for prop_match in property_matches:
                        prop_content = prop_match.group(1)
                        property_obj = {}
                        
                        # 提取基本屬性
                        name_match = re.search(r'name:\s*[\'"]([^\'"]+)[\'"]', prop_content)
                        if name_match:
                            property_obj['name'] = name_match.group(1)
                        
                        display_name_match = re.search(r'displayName:\s*[\'"]([^\'"]+)[\'"]', prop_content)
                        if display_name_match:
                            property_obj['displayName'] = display_name_match.group(1)
                        
                        type_match = re.search(r'type:\s*[\'"]([^\'"]+)[\'"]', prop_content)
                        if type_match:
                            property_obj['type'] = type_match.group(1)
                        
                        description_match = re.search(r'description:\s*[\'"]([^\'"]+)[\'"]', prop_content)
                        if description_match:
                            property_obj['description'] = description_match.group(1)
                        
                        default_match = re.search(r'default:\s*[\'"]([^\'"]+)[\'"]', prop_content)
                        if default_match:
                            property_obj['default'] = default_match.group(1)
                        elif re.search(r'default:\s*(true|false)', prop_content):
                            bool_match = re.search(r'default:\s*(true|false)', prop_content)
                            property_obj['default'] = bool_match.group(1) == 'true'
                        
                        # 提取 options
                        options_pattern = r'options:\s*\[(.*?)\]'
                        options_match = re.search(options_pattern, prop_content, re.DOTALL)
                        if options_match:
                            options_content = options_match.group(1)
                            options = []
                            option_pattern = r'\{\s*name:\s*[\'"]([^\'"]+)[\'"]\s*,\s*value:\s*[\'"]([^\'"]+)[\'"]\s*(?:,\s*description:\s*[\'"]([^\'"]+)[\'"])?\s*\}'
                            option_matches = re.finditer(option_pattern, options_content)
                            for opt_match in option_matches:
                                option = {
                                    'name': opt_match.group(1),
                                    'value': opt_match.group(2)
                                }
                                if opt_match.group(3):
                                    option['description'] = opt_match.group(3)
                                options.append(option)
                            if options:
                                property_obj['options'] = options
                        
                        if property_obj:
                            properties.append(property_obj)
            
            except Exception as e:
                print(f"Error processing description file {desc_file}: {e}")
                continue
        
        return properties
        
    except Exception as e:
        print(f"Error extracting properties for {node_name}: {e}")
        return []

def create_complete_node_schema(js_file_path):
    """創建完整的節點 schema"""
    
    # 提取基本節點定義
    node_def = extract_complete_node_definition(js_file_path)
    if not node_def:
        return None
    
    # 提取屬性定義
    base_path = os.path.dirname(js_file_path)
    properties = extract_properties_from_descriptions(base_path, node_def.get('name', ''))
    
    if properties:
        node_def['properties'] = properties
    
    return node_def

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
        base_name = os.path.basename(js_file).replace('.node.js', '')
        json_file_path = os.path.join(second_schemas_path, f"{base_name}.node.json")
        
        print(f"\\n處理節點: {base_name}")
        
        # 創建完整的 schema
        complete_schema = create_complete_node_schema(js_file)
        
        if complete_schema:
            # 保存為 JSON 檔案
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(complete_schema, f, indent=2, ensure_ascii=False)
            print(f"✅ 已更新: {json_file_path}")
            print(f"   - 包含 {len(complete_schema.get('properties', []))} 個屬性")
        else:
            print(f"❌ 無法處理: {js_file}")

if __name__ == "__main__":
    main()