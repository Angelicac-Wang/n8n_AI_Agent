# n8n AI Agent

一個基於 OpenAI 的 n8n 智慧工作流程生成器，能夠根據自然語言指令自動生成完整的 n8n 工作流程 JSON。

## 功能特色

- 🤖 **智慧節點推薦**：基於 OpenAI 分析使用者需求，自動推薦相關的 n8n 節點
- 📋 **完整 Schema 支援**：支援 435+ 個 n8n 節點的完整 JSON Schema
- 🔄 **自動工作流程生成**：自動生成可直接匯入 n8n 的完整工作流程 JSON
- 🔍 **模糊匹配**：智慧節點名稱匹配，提高推薦準確性
- 💾 **檔案輸出**：支援將生成的工作流程保存為 JSON 檔案
- 🖥️ **互動式介面**：友善的命令列互動介面

## 檔案結構

```
n8n_json_schema/
├── n8nAgent（新）.py          # 主程式 - n8n 智慧工作流程生成器
├── fetchNodesName.py          # 節點資訊提取工具
├── fetchAllNodesSchema.py     # Schema 下載工具
├── node_info.json             # 節點資訊資料庫（435個節點）
├── node_info.csv              # 節點資訊 CSV 格式
├── node_schemas/              # 所有節點的 JSON Schema 檔案
│   ├── actionNetwork.json
│   ├── activeCampaign.json
│   └── ... (435+ schema 檔案)
└── generated_workflow_*.json  # 生成的工作流程檔案
```

## 安裝需求

```bash
pip install openai
```

## 設定

### 1. 設定 OpenAI API 金鑰

**方法一：使用環境變數（推薦）**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**方法二：使用 .env 檔案**
1. 複製 `.env.example` 為 `.env`
2. 在 `.env` 檔案中填入你的 API 金鑰

**方法三：直接修改程式碼**
在 `n8nAgent（新）.py` 中直接替換 `your-openai-api-key-here`

## 使用方法

### 1. 基本使用

```bash
python3 n8nAgent（新）.py
```

### 2. 範例指令

- "我想要每天自動抓取 Gmail 信件並用 OpenAI 分析內容"
- "建立一個 HTTP API 接收資料並存入 Google Sheets"
- "設定 Google Calendar 觸發器，當有新事件時發送 Slack 通知"

### 3. 輸出範例

程式會自動：
1. 分析你的需求
2. 推薦相關的 n8n 節點
3. 載入節點的完整 Schema
4. 生成完整的工作流程 JSON
5. 可選擇保存為檔案

生成的 JSON 可以直接匯入到 n8n 中使用！

## 主要功能

### 智慧節點推薦
- 基於 OpenAI GPT-3.5-turbo 模型
- 分析自然語言指令
- 從 435+ 個節點中推薦最相關的節點

### 完整工作流程生成
- 自動配置節點參數
- 建立節點間的連接關係
- 設定合理的畫布位置
- 生成可直接使用的 n8n JSON

### 模糊匹配
- 智慧節點名稱匹配
- 當找不到完全匹配時自動尋找相似節點
- 提高推薦成功率

## 工具程式

### fetchNodesName.py
提取所有節點的基本資訊（名稱、描述）並生成 `node_info.json`

### fetchAllNodesSchema.py  
下載所有 n8n 節點的完整 JSON Schema 到 `node_schemas/` 目錄

## 注意事項

⚠️ **API 金鑰安全**：請確保不要將 OpenAI API 金鑰推送到公開的 repository

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 授權

MIT License
