# cd music-player-frontend
# npm run dev

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time
import threading
import asyncio
import win32api
import win32con

app = FastAPI(title="游戏乐器自动演奏器")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允许的前端地址
    allow_credentials=True,                     # 允许携带凭据
    allow_methods=["*"],                        # 允许所有 HTTP 方法
    allow_headers=["*"],                        # 允许所有请求头
)

# 全局状态：控制演奏线程
is_playing = False
play_thread = None

# 音符与键盘映射（可根据实际游戏调整）
NOTE_KEY_MAP = {
    # 低音区（低音do到低音si）
    "1-": "a",   # 低音do
    "2-": "s",   # 低音re
    "3-": "d",   # 低音mi
    "4-": "f",   # 低音fa
    "5-": "g",   # 低音sol
    "6-": "h",   # 低音la
    "7-": "j",   # 低音si

    # 中音区（标准音域）
    "1": "q",    # do
    "2": "w",    # re
    "3": "e",    # mi
    "4": "r",    # fa
    "5": "t",    # sol
    "6": "y",    # la
    "7": "u",    # si

    # 高音区（高音do到高音si）
    "1+": "1",   # 高音do
    "2+": "2",   # 高音re
    "3+": "3",   # 高音mi
    "4+": "4",   # 高音fa
    "5+": "5",   # 高音sol
    "6+": "6",   # 高音la
    "7+": "7",   # 高音si

    # 休止符
    "0": " "     # 休止符（空格键）
}

# 数据模型：乐谱音符
class Note(BaseModel):
    note: str  # 音符，如"1"、"2"等
    duration: float  # 音符时长（秒）

# 数据模型：演奏请求
class PlayRequest(BaseModel):
    notes: List[Note]
    speed: float = 1.0  # 演奏速度（1.0为正常速度）
    delay: float = 0.05  # 按键延迟
    loop: bool = False   # 是否循环播放

def press_key_hw(key_char):
    """使用win32api发送硬件级按键事件"""
    try:
        # 详细调试信息
        print(f"处理按键: {repr(key_char)}, 类型: {type(key_char)}, 长度: {len(key_char)}, ASCII码: {ord(key_char)}")
        
        # 确保是单字符字符串
        if not isinstance(key_char, str) or len(key_char) != 1:
            raise ValueError(f"无效的按键字符: {key_char}（必须是长度为1的字符串）")
        
        # 关键修复：直接传递字符给VkKeyScan（而非ASCII码）
        # VkKeyScan要求参数是单字符字符串，而非整数
        vk_code = win32api.VkKeyScan(key_char) & 0xFF
        
        # 验证虚拟键码有效性
        if vk_code == 0:
            raise ValueError(f"无法获取 {key_char} 的虚拟键码（可能不支持该字符）")
        
        # 按下按键
        win32api.keybd_event(vk_code, 0, 0, 0)
        return vk_code
    except Exception as e:
        print(f"按下按键 {repr(key_char)} 失败: {e}")
        return None

def release_key_hw(vk_code):
    """使用win32api释放按键"""
    try:
        # 释放按键
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    except Exception as e:
        print(f"释放按键失败: {e}")

def play_music(notes: List[Note], speed: float, delay: float, loop: bool = False):
    """实际执行演奏的函数，将在后台线程运行"""
    global is_playing
    is_playing = True
    
    try:
        # 循环播放逻辑
        while is_playing and loop:
            for note_info in notes:
                if not is_playing:  # 检查是否需要停止
                    break
                    
                note = note_info.note
                duration = note_info.duration / speed  # 根据速度调整时长
                
                # 获取映射的按键字符
                key_char = NOTE_KEY_MAP.get(note, "")
                
                # 严格验证映射结果
                if not isinstance(key_char, str) or len(key_char) != 1:
                    print(f"音符 {note} 映射无效: {repr(key_char)}，跳过")
                    time.sleep(duration)
                    continue
                
                if note == "0":  # 休止符
                    time.sleep(duration)
                    continue
                
                # 尝试发送按键
                vk_code = press_key_hw(key_char)
                if vk_code is not None:
                    time.sleep(duration)
                    release_key_hw(vk_code)  # 确保release_key_hw也使用正确的vk_code
                
                time.sleep(delay)
            
            # 如果不循环，则跳出循环
            if not loop:
                break
    finally:
        is_playing = False
@app.post("/api/play")
async def start_play(request: PlayRequest, background_tasks: BackgroundTasks):
    """开始演奏"""
    global play_thread, is_playing
    
    if is_playing:
        raise HTTPException(status_code=400, detail="正在演奏中，请先停止")
    
    # 在后台线程中执行演奏，避免阻塞API
    play_thread = threading.Thread(
        target=play_music,
        args=(request.notes, request.speed, request.delay, request.loop)
    )
    play_thread.start()
    
    return {"status": "success", "message": "开始演奏"}

@app.post("/api/stop")
async def stop_play():
    """停止演奏"""
    global is_playing
    is_playing = False
    return {"status": "success", "message": "已停止演奏"}

@app.get("/api/status")
async def get_status():
    """获取当前演奏状态"""
    return {"is_playing": is_playing}

@app.get("/api/key-mapping")
async def get_key_mapping():
    """获取音符与键盘的映射关系"""
    return {"mapping": NOTE_KEY_MAP}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)