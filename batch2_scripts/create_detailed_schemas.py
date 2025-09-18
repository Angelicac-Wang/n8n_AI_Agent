#!/usr/bin/env python3
import os
import json
import re

def create_node_template(node_name, display_name, description=""):
    """創建一個標準的 n8n 節點模板"""
    template = {
        "displayName": display_name,
        "name": node_name,
        "icon": f"file:{node_name.lower()}.svg",
        "group": ["transform"],
        "version": 1,
        "description": description or f"Node for {display_name}",
        "defaults": {
            "name": display_name
        },
        "inputs": ["main"],
        "outputs": ["main"],
        "credentials": [],
        "properties": [
            {
                "displayName": "Operation",
                "name": "operation",
                "type": "options",
                "noDataExpression": True,
                "default": "get",
                "options": [
                    {
                        "name": "Get",
                        "value": "get",
                        "description": "Get data from the service"
                    }
                ],
                "description": "The operation to perform"
            }
        ]
    }
    return template

# 定義已知節點的詳細配置
KNOWN_NODES = {
    "ElevenLabs": {
        "displayName": "ElevenLabs",
        "name": "elevenLabs",
        "description": "Interact with ElevenLabs API for text-to-speech and voice operations",
        "credentials": [{"name": "elevenLabsApi", "required": True}],
        "properties": [
            {
                "displayName": "Resource",
                "name": "resource",
                "type": "options",
                "noDataExpression": True,
                "default": "voice",
                "options": [
                    {"name": "Voice", "value": "voice", "description": "Work with voices"},
                    {"name": "Speech", "value": "speech", "description": "Generate speech from text"}
                ],
                "description": "The resource to operate on"
            },
            {
                "displayName": "Operation",
                "name": "operation",
                "type": "options",
                "noDataExpression": True,
                "default": "get",
                "displayOptions": {"show": {"resource": ["voice"]}},
                "options": [
                    {"name": "Get", "value": "get", "description": "Get voice details"},
                    {"name": "Get Many", "value": "getAll", "description": "Get all voices"},
                    {"name": "Create Clone", "value": "createClone", "description": "Create voice clone"},
                    {"name": "Delete", "value": "delete", "description": "Delete a voice"}
                ],
                "description": "The operation to perform on voices"
            },
            {
                "displayName": "Voice ID",
                "name": "voiceId",
                "type": "string",
                "default": "",
                "required": True,
                "displayOptions": {"show": {"resource": ["voice"], "operation": ["get", "delete"]}},
                "description": "ID of the voice to operate on"
            },
            {
                "displayName": "Text",
                "name": "text",
                "type": "string",
                "default": "",
                "required": True,
                "displayOptions": {"show": {"resource": ["speech"]}},
                "description": "Text to convert to speech"
            },
            {
                "displayName": "Voice ID",
                "name": "voiceId",
                "type": "string",
                "default": "",
                "required": True,
                "displayOptions": {"show": {"resource": ["speech"]}},
                "description": "Voice to use for speech generation"
            }
        ]
    },
    "Apify": {
        "displayName": "Apify",
        "name": "apify",
        "description": "Interact with Apify platform for web scraping and automation",
        "credentials": [{"name": "apifyApi", "required": True}],
        "properties": [
            {
                "displayName": "Resource",
                "name": "resource",
                "type": "options",
                "noDataExpression": True,
                "default": "actor",
                "options": [
                    {"name": "Actor", "value": "actor", "description": "Work with actors"},
                    {"name": "Dataset", "value": "dataset", "description": "Work with datasets"},
                    {"name": "Run", "value": "run", "description": "Work with actor runs"}
                ],
                "description": "The resource to operate on"
            },
            {
                "displayName": "Operation",
                "name": "operation",
                "type": "options",
                "noDataExpression": True,
                "default": "run",
                "options": [
                    {"name": "Run", "value": "run", "description": "Run an actor"},
                    {"name": "Get", "value": "get", "description": "Get actor details"},
                    {"name": "Get Many", "value": "getAll", "description": "Get all actors"}
                ],
                "description": "The operation to perform"
            },
            {
                "displayName": "Actor ID",
                "name": "actorId",
                "type": "string",
                "default": "",
                "required": True,
                "description": "ID of the actor to run"
            }
        ]
    },
    "GoogleSearch": {
        "displayName": "Google Search",
        "name": "googleSearch",
        "description": "Perform Google searches and retrieve results",
        "credentials": [{"name": "googleSearchApi", "required": True}],
        "properties": [
            {
                "displayName": "Query",
                "name": "query",
                "type": "string",
                "default": "",
                "required": True,
                "description": "Search query to execute"
            },
            {
                "displayName": "Number of Results",
                "name": "num",
                "type": "number",
                "default": 10,
                "description": "Number of search results to return"
            },
            {
                "displayName": "Start Index",
                "name": "start",
                "type": "number",
                "default": 1,
                "description": "Index of the first result to return"
            },
            {
                "displayName": "Safe Search",
                "name": "safe",
                "type": "options",
                "default": "medium",
                "options": [
                    {"name": "High", "value": "high"},
                    {"name": "Medium", "value": "medium"},
                    {"name": "Off", "value": "off"}
                ],
                "description": "Safe search setting"
            }
        ]
    },
    "BraveSearch": {
        "displayName": "Brave Search",
        "name": "braveSearch",
        "description": "Perform searches using Brave Search API",
        "credentials": [{"name": "braveSearchApi", "required": True}],
        "properties": [
            {
                "displayName": "Query",
                "name": "q",
                "type": "string",
                "default": "",
                "required": True,
                "description": "Search query"
            },
            {
                "displayName": "Country",
                "name": "country",
                "type": "string",
                "default": "US",
                "description": "Country code for search results"
            },
            {
                "displayName": "Search Type",
                "name": "search_type",
                "type": "options",
                "default": "web",
                "options": [
                    {"name": "Web", "value": "web"},
                    {"name": "News", "value": "news"},
                    {"name": "Images", "value": "images"}
                ],
                "description": "Type of search to perform"
            }
        ]
    },
    "Excel": {
        "displayName": "Excel",
        "name": "excel",
        "description": "Read and write Excel files",
        "properties": [
            {
                "displayName": "Operation",
                "name": "operation",
                "type": "options",
                "noDataExpression": True,
                "default": "read",
                "options": [
                    {"name": "Read from File", "value": "read", "description": "Read data from Excel file"},
                    {"name": "Write to File", "value": "write", "description": "Write data to Excel file"}
                ],
                "description": "The operation to perform"
            },
            {
                "displayName": "Binary Property",
                "name": "binaryProperty",
                "type": "string",
                "default": "data",
                "displayOptions": {"show": {"operation": ["read"]}},
                "description": "Name of the binary property containing the Excel file"
            },
            {
                "displayName": "Worksheet Name",
                "name": "worksheetName",
                "type": "string",
                "default": "",
                "description": "Name of the worksheet to read/write"
            }
        ]
    },
    "MongoDbOperations": {
        "displayName": "MongoDB Operations",
        "name": "mongoDbOperations",
        "description": "Perform operations on MongoDB databases",
        "credentials": [{"name": "mongoDb", "required": True}],
        "properties": [
            {
                "displayName": "Operation",
                "name": "operation",
                "type": "options",
                "noDataExpression": True,
                "default": "find",
                "options": [
                    {"name": "Find", "value": "find", "description": "Find documents"},
                    {"name": "Insert", "value": "insert", "description": "Insert documents"},
                    {"name": "Update", "value": "update", "description": "Update documents"},
                    {"name": "Delete", "value": "delete", "description": "Delete documents"}
                ],
                "description": "The operation to perform"
            },
            {
                "displayName": "Collection",
                "name": "collection",
                "type": "string",
                "default": "",
                "required": True,
                "description": "Name of the collection"
            },
            {
                "displayName": "Query",
                "name": "query",
                "type": "json",
                "default": "{}",
                "description": "MongoDB query as JSON"
            }
        ]
    }
}

def main():
    base_path = "/Users/angelicawang/Documents/n8n/n8n_json_schema"
    second_schemas_path = os.path.join(base_path, "node_schemas", "second")
    
    # 處理已知節點
    for node_key, node_config in KNOWN_NODES.items():
        json_file_path = os.path.join(second_schemas_path, f"{node_key}.node.json")
        
        # 創建完整的節點定義
        complete_node = {
            "displayName": node_config["displayName"],
            "name": node_config["name"],
            "icon": f"file:{node_config['name'].lower()}.svg",
            "group": ["transform"],
            "version": 1,
            "description": node_config["description"],
            "defaults": {
                "name": node_config["displayName"]
            },
            "inputs": ["main"],
            "outputs": ["main"],
            "credentials": node_config.get("credentials", []),
            "properties": node_config["properties"]
        }
        
        # 保存檔案
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(complete_node, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已更新 {node_key}: {len(node_config['properties'])} 個屬性")
    
    # 處理其他節點（使用通用模板）
    other_nodes = [
        ("Fireflies", "會議記錄和轉錄服務"),
        ("CloudConvert", "文件格式轉換服務"),
        ("Formbricks", "表單和調查工具"),
        ("ChatWoot", "客服聊天平台"),
        ("JSONata", "JSON 查詢和轉換語言"),
        ("PdfMerge", "PDF 文件合併工具"),
        ("Puppeteer", "網頁自動化工具"),
        ("WAHA", "WhatsApp HTTP API"),
        ("WAHATrigger", "WhatsApp HTTP API 觸發器")
    ]
    
    for node_name, description in other_nodes:
        json_file_path = os.path.join(second_schemas_path, f"{node_name}.node.json")
        
        # 創建基本模板
        template = create_node_template(
            node_name.lower().replace("trigger", "Trigger"),
            node_name,
            description
        )
        
        # 保存檔案
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已創建 {node_name} (基本模板)")

if __name__ == "__main__":
    main()