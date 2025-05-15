import requests
from bs4 import BeautifulSoup
import json
import configparser
from urllib.parse import quote
import time
from typing import List, Dict, Any

class DirectorySpider:
    def __init__(self, config_path: str = 'config.ini'):
        self.config = self._load_config(config_path)
        self.base_url = self.config.get('settings', 'base_url')
        self.work_id = 'RJ01332053'  # 固定为目标作品ID
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _load_config(self, config_path: str) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')
        return config

    def _get_directory_content(self, path: List[str] = None) -> Dict[str, Any]:
        """获取指定路径的目录内容"""
        if path is None:
            path = []
        
        # 构建URL
        path_param = quote(json.dumps(path))
        url = f"{self.base_url}/work/{self.work_id}?path={path_param}#work-tree"
        
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 解析目录内容
            directory_items = []
            tree_items = soup.select('.tree-item')
            
            for item in tree_items:
                name = item.get_text(strip=True)
                is_directory = 'folder' in item.get('class', [])
                directory_items.append({
                    'name': name,
                    'is_directory': is_directory
                })
            
            return {
                'path': path,
                'items': directory_items
            }
            
        except Exception as e:
            print(f"Error fetching directory content for path {path}: {str(e)}")
            return {
                'path': path,
                'items': [],
                'error': str(e)
            }

    def get_full_directory_structure(self) -> Dict[str, Any]:
        """递归获取完整的目录结构"""
        def explore_directory(current_path: List[str]) -> Dict[str, Any]:
            content = self._get_directory_content(current_path)
            structure = {
                'path': current_path,
                'items': []
            }
            
            for item in content['items']:
                if item['is_directory']:
                    new_path = current_path + [item['name']]
                    sub_structure = explore_directory(new_path)
                    structure['items'].append({
                        'name': item['name'],
                        'type': 'directory',
                        'children': sub_structure['items']
                    })
                else:
                    structure['items'].append({
                        'name': item['name'],
                        'type': 'file'
                    })
                
                # 添加延时避免请求过快
                time.sleep(1)
            
            return structure

        return explore_directory([])

    def save_directory_structure(self, structure: Dict[str, Any], filename: str = 'directory_structure.json'):
        """保存目录结构到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(structure, f, ensure_ascii=False, indent=2)

def main():
    spider = DirectorySpider()
    print("开始获取目录结构...")
    directory_structure = spider.get_full_directory_structure()
    spider.save_directory_structure(directory_structure)
    print(f"目录结构已保存到 directory_structure.json")

if __name__ == '__main__':
    main() 