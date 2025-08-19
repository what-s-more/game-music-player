import subprocess
import threading
import time
import webbrowser
import sys
import os

def find_node_executable():
    """查找 node 和 npm 可执行文件"""
    # 常见的 Node.js 安装路径
    common_paths = [
        "C:\\Program Files\\nodejs",
        "C:\\Program Files (x86)\\nodejs",
        os.path.expanduser("~\\AppData\\Roaming\\npm"),
    ]
    
    # 检查系统 PATH
    for path in os.environ.get("PATH", "").split(os.pathsep):
        if "nodejs" in path.lower() or "npm" in path.lower():
            common_paths.append(path)
    
    # 尝试查找 node.exe
    for base_path in common_paths:
        node_exe = os.path.join(base_path, "node.exe")
        npm_exe = os.path.join(base_path, "npm.cmd")  # Windows 上 npm 通常是 .cmd 文件
        
        if os.path.exists(node_exe):
            print(f"找到 Node.js: {node_exe}")
            return node_exe, npm_exe if os.path.exists(npm_exe) else "npm"
    
    return None, None

def start_backend():
    """启动后端服务"""
    print("正在启动后端服务 (FastAPI)...")
    try:
        # 使用当前虚拟环境的 Python 解释器
        backend_process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 实时输出后端日志
        print("后端服务日志:")
        for line in backend_process.stdout:
            print(f"[后端] {line.strip()}")
            
    except Exception as e:
        print(f"启动后端服务失败: {e}")

def start_frontend(node_exe, npm_cmd):
    """启动前端服务"""
    print("正在启动前端服务 (Vue)...")
    try:
        # 检查前端目录是否存在
        frontend_dir = "music-player-frontend"
        if not os.path.exists(frontend_dir):
            print("错误: 前端目录 'music-player-frontend' 不存在")
            return
            
        # 检查 package.json 是否存在
        if not os.path.exists(os.path.join(frontend_dir, "package.json")):
            print("错误: 前端目录中缺少 package.json 文件")
            return
        
        # 等待后端启动
        time.sleep(3)
        
        # 启动前端开发服务器
        frontend_process = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 等待前端启动完成
        time.sleep(8)
        
        # 打开浏览器
        print("正在打开浏览器...")
        webbrowser.open("http://localhost:5173")
        
        # 输出前端日志
        print("前端服务日志:")
        for line in frontend_process.stdout:
            print(f"[前端] {line.strip()}")
            
    except FileNotFoundError:
        print("错误: 找不到 npm 命令，请确保已安装 Node.js")
    except Exception as e:
        print(f"启动前端服务失败: {e}")

def check_dependencies():
    """检查必要的依赖"""
    print("检查运行环境...")
    
    # 检查 Python 环境中的依赖
    try:
        import win32api
        print("✓ win32api 可用")
    except ImportError:
        print("✗ 缺少 win32api 模块，请运行: pip install pywin32")
        return False, None, None
    
    # 检查 Node.js 和 npm
    node_exe, npm_cmd = find_node_executable()
    if node_exe:
        try:
            # 使用找到的可执行文件路径
            node_result = subprocess.run([node_exe, "--version"], 
                                       capture_output=True, text=True, check=True)
            npm_result = subprocess.run([npm_cmd, "--version"], 
                                      capture_output=True, text=True, check=True)
            print(f"✓ Node.js 环境可用 (node {node_result.stdout.strip()}, npm {npm_result.stdout.strip()})")
            return True, node_exe, npm_cmd
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    # 如果通过路径没找到，尝试使用系统命令
    try:
        node_result = subprocess.run(["node", "--version"], 
                                   capture_output=True, text=True, check=True)
        npm_result = subprocess.run(["npm", "--version"], 
                                  capture_output=True, text=True, check=True)
        print(f"✓ Node.js 环境可用 (node {node_result.stdout.strip()}, npm {npm_result.stdout.strip()})")
        return True, "node", "npm"
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ 找不到 node 或 npm 命令，请确保已安装 Node.js")
        return False, None, None
    
    # 检查前端目录
    if not os.path.exists("music-player-frontend"):
        print("✗ 找不到 'music-player-frontend' 目录")
        return False, None, None
        
    return True, node_exe, npm_cmd

if __name__ == "__main__":
    print("音乐播放器开发环境启动器")
    print("=" * 40)
    
    # 检查依赖
    deps_ok, node_exe, npm_cmd = check_dependencies()
    if not deps_ok:
        print("\n请解决上述依赖问题后再尝试启动。")
        sys.exit(1)
    
    # 启动后端线程
    print("\n正在启动后端服务...")
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # 等待后端启动
    print("等待后端服务启动 (约3秒)...")
    time.sleep(3)
    
    # 启动前端线程
    print("\n正在启动前端服务...")
    frontend_thread = threading.Thread(target=lambda: start_frontend(node_exe, npm_cmd), daemon=True)
    frontend_thread.start()
    
    # 等待前端启动并打开浏览器
    print("等待前端服务启动 (约5秒)...")
    time.sleep(5)
    
    # 显示服务信息
    print("\n" + "=" * 40)
    print("✅ 开发环境启动完成!")
    print("📘 后端 API 地址: http://localhost:8000")
    print("🌐 前端页面地址: http://localhost:5173")
    print("🔄 如果浏览器未自动打开，请手动访问前端地址")
    print("⏹️  按 Ctrl+C 停止所有服务")
    print("=" * 40 + "\n")
    
    # 保持主进程运行
    try:
        # 等待任一线程结束
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n正在停止所有服务...")
        print("👋 开发环境已关闭")
        sys.exit(0)