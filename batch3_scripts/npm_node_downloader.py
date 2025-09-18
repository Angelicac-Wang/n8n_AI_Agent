#!/usr/bin/env python3
"""
從 npm 抓取 n8n 社群節點套件
這是 n8n 官方推薦的標準流程
"""

import requests
import json
import os
import subprocess
import tarfile
import tempfile
import shutil
from pathlib import Path
import re

class N8nNodePackageDownloader:
    def __init__(self, output_dir="community_packages"):
        self.output_dir = output_dir
        self.npm_registry = "https://registry.npmjs.org"
        self.packages_info = []
        
    def search_n8n_packages(self, limit=100):
        """搜尋 npm 上的 n8n 社群節點套件"""
        print("🔍 搜尋 npm 上的 n8n 社群節點套件...")
        
        # n8n 社群節點的命名規範
        search_queries = [
            "keywords:n8n-community-node-package",
            "n8n-nodes-",
            "n8n-community-",
            "@n8n/"
        ]
        
        all_packages = []
        
        for query in search_queries:
            try:
                url = f"{self.npm_registry}/-/v1/search"
                params = {
                    'text': query,
                    'size': limit,
                    'quality': 0.65,
                    'popularity': 0.35,
                    'maintenance': 0.35
                }
                
                response = requests.get(url, params=params, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    packages = data.get('objects', [])
                    print(f"  查詢 '{query}': 找到 {len(packages)} 個套件")
                    all_packages.extend(packages)
                    
            except Exception as e:
                print(f"  ❌ 搜尋查詢 '{query}' 失敗: {e}")
        
        # 去重並過濾真正的 n8n 節點套件
        unique_packages = {}
        for pkg_obj in all_packages:
            pkg = pkg_obj.get('package', {})
            name = pkg.get('name', '')
            
            if name in unique_packages:
                continue
                
            # 檢查是否為真正的 n8n 社群節點
            keywords = pkg.get('keywords', [])
            description = pkg.get('description', '').lower()
            
            is_n8n_node = (
                'n8n-community-node-package' in keywords or
                'n8n-nodes-' in name or
                'n8n-community-' in name or
                name.startswith('@n8n/') or
                'n8n' in description
            )
            
            if is_n8n_node:
                unique_packages[name] = {
                    'name': name,
                    'version': pkg.get('version', 'latest'),
                    'description': pkg.get('description', ''),
                    'keywords': keywords,
                    'author': pkg.get('author', {}),
                    'repository': pkg.get('repository', {}),
                    'homepage': pkg.get('homepage', ''),
                    'downloads': pkg_obj.get('searchScore', 0)
                }
        
        self.packages_info = sorted(unique_packages.values(), 
                                  key=lambda x: x['downloads'], reverse=True)
        
        print(f"✅ 找到 {len(self.packages_info)} 個獨特的 n8n 社群節點套件")
        return self.packages_info
    
    def get_package_metadata(self, package_name):
        """取得套件的詳細元資料"""
        try:
            url = f"{self.npm_registry}/{package_name}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 無法取得 {package_name} 的元資料")
                return None
                
        except Exception as e:
            print(f"❌ 取得 {package_name} 元資料時發生錯誤: {e}")
            return None
    
    def download_package_tarball(self, package_name, version="latest"):
        """下載套件的 tarball 檔案"""
        print(f"📦 下載套件: {package_name}@{version}")
        
        # 取得套件元資料
        metadata = self.get_package_metadata(package_name)
        if not metadata:
            return None
        
        # 取得最新版本的 tarball URL
        if version == "latest":
            version = metadata.get('dist-tags', {}).get('latest', version)
        
        versions = metadata.get('versions', {})
        if version not in versions:
            print(f"❌ 版本 {version} 不存在")
            return None
        
        tarball_url = versions[version].get('dist', {}).get('tarball')
        if not tarball_url:
            print(f"❌ 無法找到 tarball URL")
            return None
        
        # 下載 tarball
        try:
            response = requests.get(tarball_url, timeout=60)
            if response.status_code == 200:
                # 儲存到臨時檔案
                temp_dir = tempfile.mkdtemp()
                tarball_path = os.path.join(temp_dir, f"{package_name.replace('/', '_')}-{version}.tgz")
                
                with open(tarball_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"  ✅ 下載完成: {tarball_path}")
                return tarball_path, temp_dir, metadata
                
            else:
                print(f"❌ 下載失敗: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 下載錯誤: {e}")
            return None
    
    def extract_package_files(self, tarball_path, package_name, metadata):
        """解壓套件並提取重要檔案"""
        print(f"📂 解壓套件: {package_name}")
        
        # 建立輸出目錄
        safe_name = package_name.replace('/', '_').replace('@', '')
        package_dir = os.path.join(self.output_dir, safe_name)
        os.makedirs(package_dir, exist_ok=True)
        
        try:
            # 解壓 tarball
            with tarfile.open(tarball_path, 'r:gz') as tar:
                tar.extractall(package_dir)
            
            # 尋找解壓後的 package 目錄（通常在 package/ 子目錄中）
            extracted_package_dir = os.path.join(package_dir, 'package')
            if not os.path.exists(extracted_package_dir):
                # 如果沒有 package 子目錄，使用根目錄
                extracted_package_dir = package_dir
            
            # 收集檔案資訊
            file_info = {
                'package_json': None,
                'node_files': [],
                'credential_files': [],
                'typescript_files': [],
                'json_files': [],
                'all_files': []
            }
            
            # 遍歷所有檔案
            for root, dirs, files in os.walk(extracted_package_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, extracted_package_dir)
                    file_info['all_files'].append(rel_path)
                    
                    # 分類檔案
                    if file == 'package.json':
                        file_info['package_json'] = file_path
                    elif file.endswith('.node.ts') or file.endswith('.node.js'):
                        file_info['node_files'].append(rel_path)
                    elif file.endswith('.credentials.ts') or file.endswith('.credentials.js'):
                        file_info['credential_files'].append(rel_path)
                    elif file.endswith('.ts'):
                        file_info['typescript_files'].append(rel_path)
                    elif file.endswith('.json'):
                        file_info['json_files'].append(rel_path)
            
            # 讀取 package.json
            package_json_data = None
            if file_info['package_json']:
                try:
                    with open(file_info['package_json'], 'r', encoding='utf-8') as f:
                        package_json_data = json.load(f)
                except Exception as e:
                    print(f"  ⚠️ 無法讀取 package.json: {e}")
            
            # 儲存套件資訊
            package_info = {
                'name': package_name,
                'version': metadata.get('dist-tags', {}).get('latest', 'unknown'),
                'description': metadata.get('description', ''),
                'keywords': metadata.get('keywords', []),
                'repository': metadata.get('repository', {}),
                'extracted_path': extracted_package_dir,
                'files': file_info,
                'package_json': package_json_data,
                'npm_metadata': metadata
            }
            
            # 儲存套件資訊為 JSON
            info_file = os.path.join(package_dir, 'package_info.json')
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(package_info, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ 解壓完成: {package_dir}")
            print(f"    - Node 檔案: {len(file_info['node_files'])}")
            print(f"    - Credential 檔案: {len(file_info['credential_files'])}")
            print(f"    - TypeScript 檔案: {len(file_info['typescript_files'])}")
            print(f"    - JSON 檔案: {len(file_info['json_files'])}")
            print(f"    - 總檔案: {len(file_info['all_files'])}")
            
            return package_info
            
        except Exception as e:
            print(f"❌ 解壓錯誤: {e}")
            return None
    
    def download_popular_packages(self, max_packages=20):
        """下載熱門的 n8n 社群節點套件"""
        print(f"🚀 開始下載前 {max_packages} 個熱門 n8n 社群節點套件...")
        
        # 建立輸出目錄
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 搜尋套件
        packages = self.search_n8n_packages()
        
        if not packages:
            print("❌ 沒有找到任何 n8n 社群節點套件")
            return []
        
        # 下載前 N 個套件
        downloaded_packages = []
        packages_to_download = packages[:max_packages]
        
        print(f"\n📋 準備下載的套件清單:")
        for i, pkg in enumerate(packages_to_download, 1):
            print(f"  {i}. {pkg['name']} - {pkg['description'][:60]}...")
        
        print(f"\n🔽 開始下載...")
        
        for i, pkg in enumerate(packages_to_download, 1):
            print(f"\n[{i}/{len(packages_to_download)}] 處理套件: {pkg['name']}")
            
            # 下載 tarball
            result = self.download_package_tarball(pkg['name'], pkg['version'])
            if not result:
                continue
                
            tarball_path, temp_dir, metadata = result
            
            try:
                # 解壓套件
                package_info = self.extract_package_files(tarball_path, pkg['name'], metadata)
                if package_info:
                    downloaded_packages.append(package_info)
                
            finally:
                # 清理臨時檔案
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        print(f"\n🎉 下載完成！成功下載 {len(downloaded_packages)} 個套件到 {self.output_dir}")
        
        # 產生總結報告
        self.generate_summary_report(downloaded_packages)
        
        return downloaded_packages
    
    def generate_summary_report(self, downloaded_packages):
        """產生下載總結報告"""
        report_path = os.path.join(self.output_dir, 'download_summary.json')
        
        summary = {
            'download_date': '2025-01-15',
            'total_packages': len(downloaded_packages),
            'packages': []
        }
        
        for pkg in downloaded_packages:
            pkg_summary = {
                'name': pkg['name'],
                'version': pkg['version'],
                'description': pkg['description'],
                'node_files_count': len(pkg['files']['node_files']),
                'credential_files_count': len(pkg['files']['credential_files']),
                'typescript_files_count': len(pkg['files']['typescript_files']),
                'total_files_count': len(pkg['files']['all_files']),
                'has_package_json': pkg['files']['package_json'] is not None
            }
            summary['packages'].append(pkg_summary)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"📊 總結報告已儲存至: {report_path}")

def main():
    print("=== n8n 社群節點套件下載器 ===")
    print("從 npm 下載完整的 n8n 社群節點套件（包含 .ts, .json 等所有檔案）")
    print()
    
    downloader = N8nNodePackageDownloader()
    
    # 下載熱門套件
    downloaded = downloader.download_popular_packages(max_packages=15)
    
    print(f"\n✅ 總共下載了 {len(downloaded)} 個 n8n 社群節點套件")
    print(f"📁 檔案位置: {downloader.output_dir}")
    print("\n💡 這些套件包含:")
    print("  - 完整的 TypeScript 原始碼 (.ts)")
    print("  - 節點定義檔案 (.json)")
    print("  - 認證設定檔案")
    print("  - package.json 和相依性資訊")
    print("  - 完整的套件結構")

if __name__ == "__main__":
    main()