import os
import json
import openai

# 設定 OpenAI API 金鑰
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("❌ Error: OPENAI_API_KEY environment variable not set")
    exit(1)
client = openai.OpenAI(api_key=api_key)

def load_node_info():
    """載入節點資訊"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(current_dir, "node_info.json")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 '{json_file}'，請先執行 fetchNodesName.py")
        return []
    except Exception as e:
        print(f"載入節點資訊時發生錯誤：{e}")
        return []

def get_recommended_nodes(user_instruction, node_info):
    """使用 OpenAI API 獲取推薦的節點"""
    try:
        # 格式化節點資訊為字典
        nodes_dict = {}
        for node in node_info:
            display_name = node.get('displayName', '')
            description = node.get('description', '')
            if display_name:
                short_desc = description[:50] + "..." if len(description) > 50 else description
                nodes_dict[display_name] = short_desc
        
        # 將節點字典轉換為字串格式
        nodes_str = ", ".join([f'"{name}": "{desc}"' for name, desc in nodes_dict.items()])
        
        prompt = f"""你是一位 n8n 智慧助理。請從提供的 n8n 節點列表中，找出所有相關的節點。

**重要：輸出格式**
請直接輸出一個純 JSON 陣列，不要包含任何 markdown 格式、代碼塊標記或其他文字。

正確輸出範例：
["HTTP Request", "Set"]

可用節點：
{{{nodes_str}}}

使用者指令：
{user_instruction}

推薦節點陣列："""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"呼叫 OpenAI API 時發生錯誤：{e}")
        return None

def load_node_schema(node_display_name):
    """根據節點顯示名稱載入對應的完整 JSON Schema"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    schema_folder = os.path.join(current_dir, "node_schemas")
    
    try:
        for filename in os.listdir(schema_folder):
            if filename.endswith(".json"):
                filepath = os.path.join(schema_folder, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                    if schema_data.get("displayName") == node_display_name:
                        return schema_data
        return None
    except Exception as e:
        print(f"載入節點 Schema 時發生錯誤：{e}")
        return None

def find_similar_node_schema(node_name):
    """模糊匹配節點名稱，找到最相似的節點 Schema"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    schema_folder = os.path.join(current_dir, "node_schemas")
    
    try:
        node_name_lower = node_name.lower()
        best_match = None
        best_score = 0
        
        for filename in os.listdir(schema_folder):
            if filename.endswith(".json"):
                filepath = os.path.join(schema_folder, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                    display_name = schema_data.get("displayName", "")
                    
                    if display_name:
                        display_name_lower = display_name.lower()
                        
                        # 完全匹配
                        if display_name_lower == node_name_lower:
                            return schema_data
                        
                        # 部分匹配
                        if node_name_lower in display_name_lower or display_name_lower in node_name_lower:
                            score = len(set(node_name_lower.split()) & set(display_name_lower.split()))
                            if score > best_score:
                                best_score = score
                                best_match = schema_data
        
        return best_match
        
    except Exception as e:
        print(f"模糊匹配時發生錯誤：{e}")
        return None

def generate_workflow_json(user_instruction, node_schemas_list):
    """根據使用者指令和節點 Schema 生成完整的 n8n 工作流程 JSON"""
    try:
        # 確保是陣列格式
        if not isinstance(node_schemas_list, list):
            node_schemas_list = [node_schemas_list]
        
        # 整合所有節點 Schema
        all_schemas = []
        for i, schema in enumerate(node_schemas_list):
            schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
            all_schemas.append(f"節點 {i+1} Schema:\n{schema_json}")
        
        schemas_content = "\n\n".join(all_schemas)
        
        prompt = f"""你是一位 n8n 智慧助理，請根據提供的節點 JSON Schema 和使用者指令，生成一個完整的 n8n 工作流程 JSON。

**所需節點的 JSON Schema:**
{schemas_content}

**使用者指令:**
{user_instruction}

**請生成符合使用者需求的完整 n8n 工作流程 JSON，格式如下:**
```json
{{
  "name": "工作流程名稱",
  "nodes": [
    {{
      "id": "1",
      "name": "節點名稱1",
      "type": "節點類型1",
      "typeVersion": 1,
      "position": [100, 200],
      "parameters": {{
        "參數名": "參數值"
      }}
    }}
  ],
  "connections": {{
    "節點名稱1": {{
      "main": [
        [
          {{
            "node": "節點名稱2",
            "type": "main",
            "index": 0
          }}
        ]
      ]
    }}
  }}
}}
```

**重要提醒:**
1. 根據 Schema 中的 `name` 欄位作為節點的 `type`
2. 根據 Schema 中的 `displayName` 作為節點的 `name`
3. 根據使用者指令正確設定每個節點的 parameters 參數
4. 如果只有一個節點，connections 可以是空物件 {{}}
5. 如果有多個節點，建立合理的節點連接順序
6. 只輸出 JSON，不要包含其他解釋文字"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1500
        )
        
        generated_json = response.choices[0].message.content.strip()
        
        # 清理回應，只保留 JSON 部分
        if "```json" in generated_json:
            start = generated_json.find("```json") + 7
            end = generated_json.find("```", start)
            if end != -1:
                generated_json = generated_json[start:end].strip()
        
        return generated_json
        
    except Exception as e:
        print(f"生成工作流程 JSON 時發生錯誤：{e}")
        return None

def parse_recommended_nodes(recommended_nodes):
    """解析推薦節點字串，返回節點名稱列表"""
    try:
        cleaned_response = recommended_nodes.strip()
        
        # 移除 markdown 代碼塊標記
        if "```json" in cleaned_response:
            start = cleaned_response.find("```json") + 7
            end = cleaned_response.find("```", start)
            if end != -1:
                cleaned_response = cleaned_response[start:end].strip()
        elif "```" in cleaned_response:
            cleaned_response = cleaned_response.replace("```", "").strip()
        
        # 嘗試解析 JSON 格式
        if cleaned_response.startswith('[') and cleaned_response.endswith(']'):
            nodes_list = json.loads(cleaned_response)
        else:
            # 如果不是 JSON 格式，用逗號分隔
            nodes_list = [node.strip().strip('"\'') for node in cleaned_response.split(',')]
        
        # 確保是字串陣列
        if len(nodes_list) == 1 and isinstance(nodes_list[0], list):
            nodes_list = nodes_list[0]
        
        return [node for node in nodes_list if node.strip()]
        
    except json.JSONDecodeError:
        # JSON 解析失敗，回到逗號分隔
        cleaned_response = recommended_nodes.replace("```json", "").replace("```", "").strip()
        return [node.strip().strip('"\'') for node in cleaned_response.split(',') if node.strip()]

def main():
    """主程式"""
    print("n8n 智慧工作流程生成器")
    print("="*50)
    
    # 載入節點資訊
    print("載入節點資訊...")
    node_info = load_node_info()
    if not node_info:
        return
    
    print(f"已載入 {len(node_info)} 個節點資訊")
    
    # 互動式介面
    while True:
        try:
            print("\n" + "="*50)
            user_instruction = input("請輸入您的指令（輸入 'quit' 結束）：")
            
            if user_instruction.lower() in ['quit', 'exit', '結束']:
                print("程式結束，再見！")
                break
            
            if not user_instruction.strip():
                print("請輸入有效的指令。")
                continue
            
            # 步驟 1: 分析推薦節點
            print("\n步驟 1: 分析推薦節點...")
            recommended_nodes = get_recommended_nodes(user_instruction, node_info)
            
            if not recommended_nodes:
                print("無法獲取推薦結果，請稍後再試。")
                continue
                
            print(f"推薦的節點：{recommended_nodes}")
            
            # 步驟 2: 解析推薦節點
            nodes_list = parse_recommended_nodes(recommended_nodes)
            
            if not nodes_list:
                print("無法解析推薦的節點名稱。")
                continue
            
            print(f"解析後的節點列表：{nodes_list}")
            
            # 步驟 3: 載入節點 Schema
            print(f"\n步驟 2: 載入所有推薦節點的 Schema...")
            node_schemas = []
            valid_nodes = []
            
            for i, node_name in enumerate(nodes_list):
                print(f"  載入節點 {i+1}: '{node_name}'...")
                node_schema = load_node_schema(node_name)
                
                # 如果找不到完全匹配的節點，嘗試模糊匹配
                if not node_schema:
                    print(f"    嘗試模糊匹配...")
                    node_schema = find_similar_node_schema(node_name)
                    if node_schema:
                        actual_name = node_schema.get("displayName", "未知")
                        print(f"    找到相似節點：'{actual_name}'")
                        node_name = actual_name
                
                if node_schema:
                    node_schemas.append(node_schema)
                    valid_nodes.append(node_name)
                    print(f"    ✓ 成功載入 '{node_name}' 的 Schema")
                else:
                    print(f"    ✗ 無法載入節點 '{node_name}' 的 Schema")
            
            if not node_schemas:
                print("無法載入任何節點的 Schema。")
                continue
            
            print(f"\n成功載入 {len(node_schemas)} 個節點的 Schema：{', '.join(valid_nodes)}")
            
            # 步驟 4: 生成工作流程
            print(f"\n步驟 3: 根據指令生成完整的 n8n 工作流程...")
            generated_json = generate_workflow_json(user_instruction, node_schemas)
            
            if generated_json:
                print(f"\n生成的 n8n 工作流程：")
                print("="*50)
                print(generated_json)
                print("="*50)
                
                # 詢問是否保存
                try:
                    save_choice = input("\n是否要將工作流程保存到檔案？(y/n): ")
                    if save_choice.lower() in ['y', 'yes', '是']:
                        # 生成檔案名稱
                        if len(valid_nodes) == 1:
                            filename = f"generated_workflow_{valid_nodes[0].replace(' ', '_').lower()}.json"
                        else:
                            filename = f"generated_workflow_{'_'.join([node.replace(' ', '_').lower() for node in valid_nodes[:3]])}.json"
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(generated_json)
                        print(f"工作流程已保存到 '{filename}'")
                        print(f"你可以將此檔案匯入到 n8n 中使用！")
                        
                except Exception as e:
                    print(f"保存檔案時發生錯誤：{e}")
                except EOFError:
                    print("\n輸入中斷，跳過保存步驟。")
            else:
                print("無法生成工作流程，請稍後再試。")
                
        except EOFError:
            print("\n\n輸入中斷，程式結束。")
            break
        except KeyboardInterrupt:
            print("\n\n程式被使用者中斷，再見！")
            break

if __name__ == "__main__":
    main()
