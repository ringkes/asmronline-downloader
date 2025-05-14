import os
import time
from tqdm import tqdm
from modules.utils import ensure_dir

def download_file(session, url, file_path, speed_limit_mb=0, retry=3, chunk_size=1024*1024):
    """
    下载单个文件，支持断点续传、限速（MB/s），重试。
    如果文件已存在且大小与服务器一致，则跳过下载。
    """
    ensure_dir(os.path.dirname(file_path))
    # 检查本地文件是否已存在且完整
    try:
        head = session.head(url, timeout=10)
        if 'Content-Length' in head.headers:
            total_size = int(head.headers['Content-Length'])
            if os.path.exists(file_path) and os.path.getsize(file_path) == total_size:
                print(f"文件已存在且完整，跳过下载: {file_path}")
                return True
    except Exception:
        total_size = None
    temp_file = file_path + ".part"
    headers = {}
    if os.path.exists(temp_file):
        downloaded = os.path.getsize(temp_file)
        headers['Range'] = f'bytes={downloaded}-'
    else:
        downloaded = 0
    for attempt in range(retry):
        try:
            with session.get(url, headers=headers, stream=True, timeout=30) as r:
                r.raise_for_status()
                mode = 'ab' if downloaded else 'wb'
                file_total = int(r.headers.get('Content-Length', 0)) + downloaded if 'Content-Length' in r.headers else None
                with open(temp_file, mode) as f, \
                    tqdm(total=file_total, initial=downloaded, unit='B', unit_scale=True, unit_divisor=1024, desc=os.path.basename(file_path), miniters=1, ascii=True) as bar:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))
                            # 限速
                            if speed_limit_mb > 0:
                                time.sleep(len(chunk) / (speed_limit_mb * 1024 * 1024))
            # 校验并重命名
            final_size = os.path.getsize(temp_file)
            if file_total and final_size != file_total:
                os.remove(temp_file)
                continue
            os.rename(temp_file, file_path)
            return True
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    return False

def single_download(session, work_id, config):
    from modules.work_api import fetch_work_structure
    download_path = config.get('paths', 'download_path')
    speed_limit = config.getfloat('settings', 'download_speed', fallback=0)
    max_workers = config.getint('settings', 'max_workers', fallback=4)
    structure = fetch_work_structure(session, work_id)
    if not structure:
        print(f"获取 {work_id} 目录结构失败")
        return
    file_list = collect_all_files(structure, base_path=os.path.join(download_path, work_id))
    print(f"即将下载 {len(file_list)} 个文件...")
    download_files(session, file_list, speed_limit, max_workers)

def batch_download(session, work_ids, config):
    for i, work_id in enumerate(work_ids, 1):
        print(f"\n[{i}/{len(work_ids)}] 开始下载 {work_id} ...")
        single_download(session, work_id, config)

def collect_all_files(structure, base_path="ROOT"):
    files = []
    if isinstance(structure, list):
        for item in structure:
            files.extend(collect_all_files(item, base_path))
    elif isinstance(structure, dict):
        node_type = structure.get('type', '')
        title = structure.get('title', '')
        children = structure.get('children', [])
        if node_type == 'folder':
            new_base = os.path.join(base_path, title)
            files.extend(collect_all_files(children, new_base))
        else:
            url = structure.get('mediaDownloadUrl')
            if url:
                file_path = os.path.join(base_path, title)
                files.append({'url': url, 'path': file_path})
    return files

def download_files(session, file_info_list, speed_limit, max_workers):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    print(f"使用最大线程数: {max_workers}")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(download_file, session, info['url'], info['path'], speed_limit): info
            for info in file_info_list
        }
        for future in as_completed(future_to_file):
            info = future_to_file[future]
            try:
                future.result()
            except Exception as exc:
                print(f"文件 {info['path']} 下载异常: {exc}") 