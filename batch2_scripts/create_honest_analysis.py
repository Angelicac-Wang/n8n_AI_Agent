#!/usr/bin/env python3
import os
import json

def create_honest_documentation():
    """創建誠實的文檔說明現有檔案的真實來源"""
    
    documentation = {
        "metadata": {
            "created_date": "2025-09-18",
            "purpose": "Document actual sources of node schemas",
            "honesty_note": "This documents the real sources of each schema file"
        },
        "file_sources": {
            "真正的官方 schema": {
                "source": "n8n 伺服器 API 提取",
                "location": "../*.json (792 files)",
                "quality": "完整且準確",
                "example_structure": {
                    "name": "n8n-nodes-base.nodeName",
                    "displayName": "Node Display Name", 
                    "description": "Complete description",
                    "properties": "Complete parameter definitions with all options"
                }
            },
            "社群套件提取的 schema": {
                "source": "additional_node_schemas/*.json",
                "location": "*_schema.json files",
                "quality": "部分完整",
                "note": "從社群套件中提取，可能不完整"
            },
            "AI 生成的模板": {
                "source": "基於常見模式的推測模板",
                "location": "大部分的 .node.json files",
                "quality": "基本結構正確但參數可能不準確",
                "warning": "這些是推測的，不是真正的官方定義"
            }
        },
        "recommendations": {
            "for_ai_training": "使用 ../node_schemas/*.json (792個官方檔案)",
            "for_development": "參考官方 n8n 文檔和 GitHub 源碼",
            "for_accuracy": "直接從 n8n 官方 GitHub 獲取 TypeScript 源檔案"
        },
        "honest_assessment": {
            "second_batch_quality": "混合品質 - 部分真實，部分推測",
            "most_accurate_files": [
                "來自 API 的 792 個官方檔案",
                "additional_node_schemas/ 中的 _schema.json 檔案"
            ],
            "least_accurate_files": [
                "大部分 .node.json 檔案（我生成的模板）"
            ]
        }
    }
    
    return documentation

def main():
    base_path = "/Users/angelicawang/Documents/n8n/n8n_json_schema"
    second_schemas_path = os.path.join(base_path, "node_schemas", "second")
    
    # 創建誠實的文檔
    doc = create_honest_documentation()
    
    # 保存文檔
    doc_file = os.path.join(second_schemas_path, "HONEST_SOURCE_ANALYSIS.json")
    with open(doc_file, 'w', encoding='utf-8') as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    
    print("✅ 已創建誠實的來源分析文檔")
    
    # 分析現有檔案
    print("\\n📊 檔案來源分析:")
    print("真正官方 schema: ../node_schemas/*.json (792 files)")
    print("社群提取 schema: *_schema.json (13 files)")  
    print("AI 生成模板: 大部分 .node.json files")
    
    print("\\n🎯 建議:")
    print("1. 使用 ../node_schemas/*.json 作為主要參考（最準確）")
    print("2. *_schema.json 作為社群節點參考")
    print("3. .node.json 僅作為基本結構參考（非官方）")

if __name__ == "__main__":
    main()