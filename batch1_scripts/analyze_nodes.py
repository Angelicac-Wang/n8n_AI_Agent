#!/usr/bin/env python3
"""
分析 n8n 節點類型和社群節點統計
"""

import os
import json
from collections import defaultdict

def analyze_node_types():
    """分析節點類型和來源"""
    schema_dir = "/Users/angelicawang/Documents/n8n/n8n_json_schema/node_schemas"
    
    if not os.path.exists(schema_dir):
        print("❌ node_schemas 目錄不存在")
        return
    
    # 統計變數
    total_nodes = 0
    official_nodes = 0
    langchain_nodes = 0
    ai_related_nodes = 0
    tool_nodes = 0
    trigger_nodes = 0
    
    # 分類統計
    categories = defaultdict(int)
    node_types = defaultdict(list)
    
    # AI 相關關鍵字
    ai_keywords = ['openai', 'anthropic', 'gemini', 'gpt', 'ai', 'llm', 'langchain', 
                   'embeddings', 'sentiment', 'classifier', 'chatbot', 'assistant']
    
    print("=== n8n 節點分析報告 ===")
    print(f"分析目錄: {schema_dir}")
    print()
    
    # 遍歷所有節點檔案
    for filename in os.listdir(schema_dir):
        if not filename.endswith('.json'):
            continue
            
        total_nodes += 1
        filepath = os.path.join(schema_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                node_data = json.load(f)
            
            node_name = node_data.get('name', '')
            display_name = node_data.get('displayName', '')
            description = node_data.get('description', '')
            
            # 分類節點來源
            if 'langchain' in node_name.lower() or 'langchain' in filename.lower():
                langchain_nodes += 1
                categories['LangChain'] += 1
                node_types['LangChain'].append(display_name)
            elif node_name.startswith('n8n-nodes-base.'):
                official_nodes += 1
                categories['Official'] += 1
                node_types['Official'].append(display_name)
            else:
                categories['Community'] += 1
                node_types['Community'].append(display_name)
            
            # 檢查是否為 AI 相關節點
            text_to_check = f"{node_name} {display_name} {description}".lower()
            if any(keyword in text_to_check for keyword in ai_keywords):
                ai_related_nodes += 1
                categories['AI-Related'] += 1
            
            # 檢查節點類型
            if 'tool' in display_name.lower() or 'tool' in filename.lower():
                tool_nodes += 1
                categories['Tools'] += 1
            
            if 'trigger' in display_name.lower() or 'trigger' in filename.lower():
                trigger_nodes += 1
                categories['Triggers'] += 1
                
        except Exception as e:
            print(f"⚠️ 無法讀取 {filename}: {e}")
    
    # 輸出統計結果
    print("📊 節點總量統計:")
    print(f"  總節點數: {total_nodes}")
    print(f"  官方節點: {official_nodes} ({official_nodes/total_nodes*100:.1f}%)")
    print(f"  LangChain 節點: {langchain_nodes} ({langchain_nodes/total_nodes*100:.1f}%)")
    print(f"  社群節點: {categories['Community']} ({categories['Community']/total_nodes*100:.1f}%)")
    print()
    
    print("🤖 AI 相關統計:")
    print(f"  AI 相關節點: {ai_related_nodes} ({ai_related_nodes/total_nodes*100:.1f}%)")
    print()
    
    print("⚙️ 功能類型統計:")
    print(f"  工具節點: {tool_nodes}")
    print(f"  觸發器節點: {trigger_nodes}")
    print()
    
    # 顯示 LangChain 節點詳情
    if langchain_nodes > 0:
        print("🔗 LangChain 節點詳細列表:")
        langchain_files = [f for f in os.listdir(schema_dir) if f.endswith('.json') and ('langchain' in f.lower() or 'anthropic' in f.lower() or 'openai' in f.lower())]
        
        langchain_categories = {
            'LLM Models': [],
            'Chat Models': [],
            'Embeddings': [],
            'Vector Stores': [],
            'Memory': [],
            'Tools': [],
            'Chains': [],
            'Agents': [],
            'Other': []
        }
        
        for filename in sorted(langchain_files):
            filepath = os.path.join(schema_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    node_data = json.load(f)
                display_name = node_data.get('displayName', filename.replace('.json', ''))
                
                # 分類 LangChain 節點
                name_lower = display_name.lower()
                if 'chat model' in name_lower:
                    langchain_categories['Chat Models'].append(display_name)
                elif 'model' in name_lower and 'chat' not in name_lower:
                    langchain_categories['LLM Models'].append(display_name)
                elif 'embedding' in name_lower:
                    langchain_categories['Embeddings'].append(display_name)
                elif 'vector' in name_lower:
                    langchain_categories['Vector Stores'].append(display_name)
                elif 'memory' in name_lower:
                    langchain_categories['Memory'].append(display_name)
                elif 'tool' in name_lower:
                    langchain_categories['Tools'].append(display_name)
                elif 'chain' in name_lower:
                    langchain_categories['Chains'].append(display_name)
                elif 'agent' in name_lower:
                    langchain_categories['Agents'].append(display_name)
                else:
                    langchain_categories['Other'].append(display_name)
                    
            except Exception as e:
                print(f"  ⚠️ 無法讀取 {filename}: {e}")
        
        for category, nodes in langchain_categories.items():
            if nodes:
                print(f"  {category} ({len(nodes)} 個):")
                for node in sorted(nodes)[:5]:  # 只顯示前5個
                    print(f"    - {node}")
                if len(nodes) > 5:
                    print(f"    ... 還有 {len(nodes) - 5} 個")
                print()
    
    print("🎉 分析完成！")
    print(f"你的 n8n 伺服器現在支援 {total_nodes} 個節點，包含大量 AI/LangChain 功能！")

if __name__ == "__main__":
    analyze_node_types()