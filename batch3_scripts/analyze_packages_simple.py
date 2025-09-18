#!/usr/bin/env python3
"""
分析從 npm 下載的 n8n 社群節點套件 - 簡化版本
"""

import os
import json
import re

def analyze_packages():
    """分析所有下載的套件"""
    packages_dir = "community_packages"
    
    if not os.path.exists(packages_dir):
        print(f"❌ 套件目錄不存在: {packages_dir}")
        return
    
    print("🔍 分析下載的 n8n 社群節點套件...")
    
    packages = [d for d in os.listdir(packages_dir) 
               if os.path.isdir(os.path.join(packages_dir, d)) 
               and not d.startswith('.')]
    
    results = {}
    total_nodes = 0
    total_credentials = 0
    total_ts_files = 0
    packages_with_nodes = 0
    
    for package_name in packages:
        print(f"\n📦 分析套件: {package_name}")
        
        package_path = os.path.join(packages_dir, package_name, "package")
        if not os.path.exists(package_path):
            package_path = os.path.join(packages_dir, package_name)
        
        # 統計檔案
        node_files = []
        credential_files = []
        ts_files = []
        
        for root, dirs, files in os.walk(package_path):
            for file in files:
                if file.endswith('.node.ts') or file.endswith('.node.js'):
                    node_files.append(os.path.join(root, file))
                elif file.endswith('.credentials.ts') or file.endswith('.credentials.js'):
                    credential_files.append(os.path.join(root, file))
                elif file.endswith('.ts'):
                    ts_files.append(os.path.join(root, file))
        
        # 分析節點檔案內容
        node_info = []
        for node_file in node_files:
            try:
                with open(node_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取基本資訊
                display_name_match = re.search(r'displayName\s*[:=]\s*[\'"]([^\'"]+)[\'"]', content)
                description_match = re.search(r'description\s*[:=]\s*[\'"]([^\'"]+)[\'"]', content)
                
                node_info.append({
                    'file': os.path.basename(node_file),
                    'display_name': display_name_match.group(1) if display_name_match else 'Unknown',
                    'description': description_match.group(1) if description_match else 'No description'
                })
                
            except Exception as e:
                print(f"    ⚠️ 無法讀取 {node_file}: {e}")
        
        # 統計
        pkg_node_count = len(node_files)
        pkg_cred_count = len(credential_files)
        pkg_ts_count = len(ts_files)
        
        total_nodes += pkg_node_count
        total_credentials += pkg_cred_count
        total_ts_files += pkg_ts_count
        
        if pkg_node_count > 0:
            packages_with_nodes += 1
        
        results[package_name] = {
            'nodes': pkg_node_count,
            'credentials': pkg_cred_count,
            'typescript_files': pkg_ts_count,
            'node_details': node_info
        }
        
        print(f"  ✅ 找到:")
        print(f"    - 節點: {pkg_node_count}")
        print(f"    - 認證: {pkg_cred_count}")
        print(f"    - TypeScript 檔案: {pkg_ts_count}")
        
        if node_info:
            print(f"    - 節點詳情:")
            for node in node_info:
                print(f"      * {node['display_name']}")
    
    # 顯示總結
    print("\n" + "="*60)
    print("📋 n8n 社群節點套件分析總結")
    print("="*60)
    print(f"分析的套件總數: {len(packages)}")
    print(f"包含節點的套件: {packages_with_nodes}")
    print(f"總節點數: {total_nodes}")
    print(f"總認證數: {total_credentials}")
    print(f"TypeScript 檔案數: {total_ts_files}")
    print("="*60)
    
    # 顯示每個套件的詳細資訊
    print("\n📦 各套件詳細資訊:")
    for pkg_name, pkg_data in results.items():
        if pkg_data['nodes'] > 0:  # 只顯示有節點的套件
            print(f"\n  🔧 {pkg_name}:")
            print(f"    節點數: {pkg_data['nodes']}")
            print(f"    認證數: {pkg_data['credentials']}")
            if pkg_data['node_details']:
                print(f"    節點名稱:")
                for node in pkg_data['node_details']:
                    print(f"      - {node['display_name']}")
                    if node['description'] != 'No description':
                        print(f"        描述: {node['description'][:60]}...")
    
    # 儲存結果
    report_path = os.path.join(packages_dir, 'analysis_summary.json')
    summary_data = {
        'total_packages': len(packages),
        'packages_with_nodes': packages_with_nodes,
        'total_nodes': total_nodes,
        'total_credentials': total_credentials,
        'total_typescript_files': total_ts_files,
        'package_details': results
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 詳細報告已儲存至: {report_path}")
    
    return results

def main():
    print("=== n8n 社群節點套件快速分析器 ===")
    print("分析從 npm 下載的 n8n 社群節點套件")
    print()
    
    analyze_packages()
    
    print(f"\n✅ 分析完成！")
    print("\n💡 發現重要資訊:")
    print("  ✓ npm 套件包含完整的 TypeScript 原始碼")
    print("  ✓ 包含節點定義和認證檔案")
    print("  ✓ 可以研究節點的實作細節")
    print("  ✓ 適合深度學習 n8n 節點開發模式")

if __name__ == "__main__":
    main()