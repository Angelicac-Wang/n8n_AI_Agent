#!/usr/bin/env python3
import os
import re

def normalize_filename(filename):
    """將檔案名標準化為小寫，移除副檔名"""
    # 移除副檔名
    name = filename.replace('.json', '')
    # 移除可能的後綴
    name = re.sub(r'_schema$', '', name)
    # 轉為小寫
    return name.lower()

def analyze_duplicates():
    """分析兩個資料夾中的重複檔案"""
    base_path = "/Users/angelicawang/Documents/n8n/n8n_json_schema"
    
    # 第一次 fetch 檔案 (node_schemas)
    first_path = os.path.join(base_path, "node_schemas")
    first_files = {}
    if os.path.exists(first_path):
        for filename in os.listdir(first_path):
            if filename.endswith('.json') and not filename.startswith('.'):
                normalized = normalize_filename(filename)
                first_files[normalized] = filename
    
    # 第三次 fetch 檔案 (nodes_base_schemas)  
    third_path = os.path.join(base_path, "nodes_base_schemas")
    third_files = {}
    if os.path.exists(third_path):
        for filename in os.listdir(third_path):
            if filename.endswith('.json') and not filename.startswith('.'):
                normalized = normalize_filename(filename)
                third_files[normalized] = filename
    
    # 找出重複的檔案
    duplicates = []
    unique_to_third = []
    
    for normalized_name in third_files:
        if normalized_name in first_files:
            duplicates.append({
                'normalized': normalized_name,
                'first_file': first_files[normalized_name],
                'third_file': third_files[normalized_name],
                'third_path': os.path.join(third_path, third_files[normalized_name])
            })
        else:
            unique_to_third.append({
                'normalized': normalized_name,
                'third_file': third_files[normalized_name]
            })
    
    print(f"📊 重複分析結果:")
    print(f"第一次 fetch 檔案數: {len(first_files)}")
    print(f"第三次 fetch 檔案數: {len(third_files)}")
    print(f"重複檔案數: {len(duplicates)}")
    print(f"第三次獨有檔案數: {len(unique_to_third)}")
    
    print(f"\\n🔄 重複檔案範例 (前10個):")
    for i, dup in enumerate(duplicates[:10]):
        print(f"  {i+1}. {dup['normalized']}")
        print(f"     第一次: {dup['first_file']}")
        print(f"     第三次: {dup['third_file']}")
    
    print(f"\\n🆕 第三次獨有檔案 (重要的新增):")
    for unique in unique_to_third:
        print(f"  - {unique['third_file']}")
    
    return duplicates, unique_to_third

def remove_duplicates(duplicates):
    """移除重複檔案"""
    print(f"\\n🗑️ 開始移除重複檔案...")
    
    removed_count = 0
    for dup in duplicates:
        try:
            os.remove(dup['third_path'])
            print(f"✅ 已刪除: {dup['third_file']}")
            removed_count += 1
        except Exception as e:
            print(f"❌ 刪除失敗: {dup['third_file']} - {e}")
    
    print(f"\\n📊 刪除總結:")
    print(f"成功刪除: {removed_count} 個檔案")
    print(f"刪除失敗: {len(duplicates) - removed_count} 個檔案")
    
    return removed_count

if __name__ == "__main__":
    duplicates, unique_to_third = analyze_duplicates()
    
    if duplicates:
        print(f"\\n❓ 確認要刪除 {len(duplicates)} 個重複檔案嗎？")
        print("這些檔案在第一次 fetch 中已經存在（只是大小寫不同）")
        
        # 自動執行刪除
        removed = remove_duplicates(duplicates)
        
        print(f"\\n🎯 清理後的 nodes_base_schemas 資料夾:")
        print(f"保留檔案數: {len(unique_to_third)}")
        print("這些是真正新增的、第一次 fetch 沒有的檔案")
    else:
        print("\\n✅ 沒有發現重複檔案")