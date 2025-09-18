#!/usr/bin/env python3
"""
整理Python腳本到不同批次資料夾
根據檔案功能和創建時間進行分類
"""

import os
import shutil
from pathlib import Path

# 定義不同批次的分類規則
batch_classification = {
    "batch1_scripts": [
        # 第一批：基本節點提取和API相關
        "fetchAllNodesSchema.py",
        "fetchNodesName.py", 
        "determineNodes.py",
        "determineNodes_cleaned.py",
        "createDescription.py",
        "analyze_nodes.py",
        "check_settings.py",
        "n8nAgent（新）.py"
    ],
    "batch2_scripts": [
        # 第二批：社群節點相關
        "check_community_nodes.py",
        "install_community_nodes.py",
        "explore_community_nodes.py",
        "test_community_support.py",
        "create_detailed_schemas.py",
        "create_honest_analysis.py",
        "create_missing_node_schemas.py"
    ],
    "batch3_scripts": [
        # 第三批：npm套件分析
        "analyze_npm_packages.py",
        "analyze_npm_packages_backup.py",
        "analyze_packages_simple.py",
        "npm_node_downloader.py",
        "search_official_packages.py",
        "extract_npm_schemas.py"
    ],
    "batch4_scripts": [
        # 第四批：進階社群套件
        "batch_download_packages.py",
        "advanced_schema_extractor.py",
        "extract_complete_schemas.py"
    ],
    "batch5_scripts": [
        # 第五批：全面分析和最終整理
        "comprehensive_analysis.py",
        "comprehensive_node_search.py",
        "final_file_analysis.py",
        "analyze_fetch_overlap.py",
        "remove_duplicate_schemas.py"
    ]
}

def organize_scripts():
    """整理Python腳本到對應的批次資料夾"""
    base_dir = Path("/Users/angelicawang/Documents/n8n/n8n_json_schema")
    
    print("🏗️ 開始整理Python腳本...")
    
    # 統計資訊
    moved_count = 0
    not_found_count = 0
    
    for batch_folder, script_list in batch_classification.items():
        batch_path = base_dir / batch_folder
        
        print(f"\n📁 處理 {batch_folder}:")
        
        for script_name in script_list:
            source_path = base_dir / script_name
            target_path = batch_path / script_name
            
            if source_path.exists():
                # 移動檔案
                shutil.move(str(source_path), str(target_path))
                print(f"  ✅ {script_name} -> {batch_folder}/")
                moved_count += 1
            else:
                print(f"  ❌ {script_name} (檔案不存在)")
                not_found_count += 1
    
    print(f"\n📊 整理完成統計:")
    print(f"  ✅ 成功移動: {moved_count} 個檔案")
    print(f"  ❌ 檔案不存在: {not_found_count} 個檔案")
    
    # 檢查是否還有未分類的Python檔案
    remaining_py_files = list(base_dir.glob("*.py"))
    if remaining_py_files:
        print(f"\n⚠️  未分類的Python檔案:")
        for file in remaining_py_files:
            print(f"  - {file.name}")
    else:
        print("\n🎉 所有Python檔案都已成功分類！")

if __name__ == "__main__":
    organize_scripts()