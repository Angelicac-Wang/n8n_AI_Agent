#!/usr/bin/env python3
"""
分析從 npm 下載的 n8n 社群節點套件
提取節點定義、TypeScript 原始碼和完整結構資訊
"""

import os
import json
import re
from pathlib import Path

class N8nPackageAnalyzer:
    def __init__(self, packages_dir="community_packages"):
        self.packages_dir = packages_dir
          print("="*50)
        print("📋 n8n 社群節點套件分析摘要")
        print("="*50)
        print(f"總套件數: {len(self.analysis_results)}")
        print(f"包含節點的套件: {summary['packages_with_nodes']}")
        print(f"包含認證的套件: {summary['packages_with_credentials']}")
        print(f"總節點數: {summary['total_nodes']}")
        print(f"總認證數: {summary['total_credentials']}")
        print(f"TypeScript 檔案數: {summary['total_typescript_files']}")
        print(f"總檔案數: {summary['total_files']}")
        print("="*50)analysis_results = {}
        
    def analyze_all_packages(self):
        """分析所有下載的套件"""
        if not os.path.exists(self.packages_dir):
            print(f"❌ 套件目錄不存在: {self.packages_dir}")
            return
        
        print("🔍 分析下載的 n8n 社群節點套件...")
        
        packages = [d for d in os.listdir(self.packages_dir) 
                   if os.path.isdir(os.path.join(self.packages_dir, d)) 
                   and d != "." and d != ".."]
        
        print(f"找到 {len(packages)} 個套件:")
        for pkg in packages:
            print(f"  - {pkg}")
        
        print("\n開始詳細分析...")
        
        for package_name in packages:
            print(f"\n📦 分析套件: {package_name}")
            result = self.analyze_single_package(package_name)
            if result:
                self.analysis_results[package_name] = result
        
        # 生成總結報告
        self.generate_comprehensive_report()
        
        return self.analysis_results
    
    def analyze_single_package(self, package_name):
        """分析單個套件"""
        package_path = os.path.join(self.packages_dir, package_name)
        
        # 尋找實際的套件目錄（通常在 package/ 子目錄中）
        actual_package_path = os.path.join(package_path, "package")
        if not os.path.exists(actual_package_path):
            actual_package_path = package_path
        
        analysis = {
            'package_name': package_name,
            'package_path': actual_package_path,
            'package_json': None,
            'nodes': [],
            'credentials': [],
            'typescript_files': [],
            'structure': {},
            'total_files': 0
        }
        
        try:
            # 讀取 package.json
            package_json_path = os.path.join(actual_package_path, 'package.json')
            if os.path.exists(package_json_path):
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    analysis['package_json'] = json.load(f)
                print(f"  ✅ 讀取 package.json")
            
            # 分析檔案結構
            self._analyze_file_structure(actual_package_path, analysis)
            
            # 尋找和分析節點檔案
            self._find_and_analyze_nodes(actual_package_path, analysis)
            
            # 尋找和分析認證檔案
            self._find_and_analyze_credentials(actual_package_path, analysis)
            
            print(f"  📊 找到:")
            print(f"    - 節點: {len(analysis['nodes'])}")
            print(f"    - 認證: {len(analysis['credentials'])}")
            print(f"    - TypeScript 檔案: {len(analysis['typescript_files'])}")
            print(f"    - 總檔案: {analysis['total_files']}")
            
            return analysis
            
        except Exception as e:
            print(f"  ❌ 分析錯誤: {e}")
            return None
    
    def _analyze_file_structure(self, package_path, analysis):
        """分析檔案結構"""
        structure = {}
        
        for root, dirs, files in os.walk(package_path):
            rel_root = os.path.relpath(root, package_path)
            if rel_root == ".":
                rel_root = "root"
            
            structure[rel_root] = {
                'directories': dirs,
                'files': files,
                'file_types': {}
            }
            
            # 統計檔案類型
            for file in files:
                analysis['total_files'] += 1
                ext = os.path.splitext(file)[1].lower()
                if ext in structure[rel_root]['file_types']:
                    structure[rel_root]['file_types'][ext] += 1
                else:
                    structure[rel_root]['file_types'][ext] = 1
                
                # 收集 TypeScript 檔案
                if ext == '.ts':
                    file_path = os.path.join(root, file)
                    rel_file_path = os.path.relpath(file_path, package_path)
                    analysis['typescript_files'].append(rel_file_path)
        
        analysis['structure'] = structure
    
    def _find_and_analyze_nodes(self, package_path, analysis):
        """尋找和分析節點檔案"""
        # 尋找 .node.ts 或 .node.js 檔案
        for root, dirs, files in os.walk(package_path):
            for file in files:
                if file.endswith('.node.ts') or file.endswith('.node.js'):
                    file_path = os.path.join(root, file)
                    node_info = self._analyze_node_file(file_path, package_path)
                    if node_info:
                        analysis['nodes'].append(node_info)
    
    def _analyze_node_file(self, file_path, package_path):
        """分析單個節點檔案"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            rel_path = os.path.relpath(file_path, package_path)
            
            node_info = {
                'file_path': rel_path,
                'file_name': os.path.basename(file_path),
                'content_preview': content[:500] + "..." if len(content) > 500 else content,
                'class_name': None,
                'display_name': None,
                'description': None,
                'exports': [],
                'imports': []
            }
            
            # 提取類別名稱
            class_match = re.search(r'class\s+(\w+)', content)
            if class_match:
                node_info['class_name'] = class_match.group(1)
            
            # 提取顯示名稱
            display_name_match = re.search(r'displayName\s*[:=]\s*[\'"]([^\'"]+)[\'"]', content)
            if display_name_match:
                node_info['display_name'] = display_name_match.group(1)
            
            # 提取描述
            description_match = re.search(r'description\s*[:=]\s*[\'"]([^\'"]+)[\'"]', content)
            if description_match:
                node_info['description'] = description_match.group(1)
            
            # 提取 imports
            import_matches = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', content)
            node_info['imports'] = import_matches
            
            # 提取 exports
            export_matches = re.findall(r'export\s+(?:class|function|const)\s+(\w+)', content)
            node_info['exports'] = export_matches
            
            return node_info
            
        except Exception as e:
            print(f"    ⚠️ 無法分析節點檔案 {file_path}: {e}")
            return None
    
    def _find_and_analyze_credentials(self, package_path, analysis):
        """尋找和分析認證檔案"""
        for root, dirs, files in os.walk(package_path):
            for file in files:
                if file.endswith('.credentials.ts') or file.endswith('.credentials.js'):
                    file_path = os.path.join(root, file)
                    cred_info = self._analyze_credential_file(file_path, package_path)
                    if cred_info:
                        analysis['credentials'].append(cred_info)
    
    def _analyze_credential_file(self, file_path, package_path):
        """分析單個認證檔案"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            rel_path = os.path.relpath(file_path, package_path)
            
            cred_info = {
                'file_path': rel_path,
                'file_name': os.path.basename(file_path),
                'content_preview': content[:300] + "..." if len(content) > 300 else content,
                'class_name': None,
                'credential_name': None,
                'properties': []
            }
            
            # 提取類別名稱
            class_match = re.search(r'class\s+(\w+)', content)
            if class_match:
                cred_info['class_name'] = class_match.group(1)
            
            # 提取認證名稱
            name_match = re.search(r'name\s*[:=]\s*[\'"]([^\'"]+)[\'"]', content)
            if name_match:
                cred_info['credential_name'] = name_match.group(1)
            
            return cred_info
            
        except Exception as e:
            print(f"    ⚠️ 無法分析認證檔案 {file_path}: {e}")
            return None
    
    def generate_comprehensive_report(self):
        """生成綜合分析報告"""
        report_path = os.path.join(self.packages_dir, 'package_analysis_report.json')
        
        # 準備報告資料
        report = {
            'analysis_date': '2025-01-15',
            'total_packages_analyzed': len(self.analysis_results),
            'summary': {
                'total_nodes': 0,
                'total_credentials': 0,
                'total_typescript_files': 0,
                'total_files': 0,
                'packages_with_nodes': 0,
                'packages_with_credentials': 0
            },
            'packages': self.analysis_results
        }
        
        # 計算統計資訊
        for pkg_name, pkg_analysis in self.analysis_results.items():
            report['summary']['total_nodes'] += len(pkg_analysis['nodes'])
            report['summary']['total_credentials'] += len(pkg_analysis['credentials'])
            report['summary']['total_typescript_files'] += len(pkg_analysis['typescript_files'])
            report['summary']['total_files'] += pkg_analysis['total_files']
            
            if pkg_analysis['nodes']:
                report['summary']['packages_with_nodes'] += 1
            if pkg_analysis['credentials']:
                report['summary']['packages_with_credentials'] += 1
        
        # 儲存報告
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 詳細分析報告已儲存至: {report_path}")
        
        # 顯示摘要
        self.print_summary_report(report['summary'])
    
    def print_summary_report(self, summary):
        """顯示摘要報告"""
        print("\n" + "="*50)
        print("📋 n8n 社群節點套件分析摘要")
        print("="*50)
        print(f"總套件數: {len(self.analysis_results)}")
        print(f"包含節點的套件: {summary['packages_with_nodes']}")
        print(f"包含認證的套件: {summary['packages_with_credentials']}")
        print(f"總節點數: {summary['total_nodes']}")
        print(f"總認證數: {summary['total_credentials']}")
        print(f"TypeScript 檔案數: {summary['total_typescript_files']}")
        print(f"總檔案數: {summary['total_files']}")
        print("="*50)
        
        # 顯示每個套件的詳細資訊
        print("\n📦 套件詳細資訊:")
        for pkg_name, pkg_analysis in self.analysis_results.items():
            print(f"\n  {pkg_name}:")
            if pkg_analysis['package_json']:
                version = pkg_analysis['package_json'].get('version', 'unknown')
                description = pkg_analysis['package_json'].get('description', 'No description')
                print(f"    版本: {version}")
                print(f"    描述: {description[:80]}...")
            
            print(f"    節點: {len(pkg_analysis['nodes'])}")
            print(f"    認證: {len(pkg_analysis['credentials'])}")
            print(f"    檔案: {pkg_analysis['total_files']}")
            
            # 顯示節點資訊
            if pkg_analysis['nodes']:
                print(f"    節點詳情:")
                for node in pkg_analysis['nodes']:
                    display_name = node.get('display_name', node.get('file_name', 'Unknown'))
                    print(f"      - {display_name}")

def main():
    print("=== n8n 社群節點套件分析器 ===")
    print("分析從 npm 下載的完整 n8n 社群節點套件")
    print()
    
    analyzer = N8nPackageAnalyzer()
    results = analyzer.analyze_all_packages()
    
    print(f"\n✅ 分析完成！")
    print(f"📁 詳細報告位置: community_packages/package_analysis_report.json")

if __name__ == "__main__":
    main()