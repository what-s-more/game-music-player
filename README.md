# 游戏乐器自动演奏器

一个基于 FastAPI 和 Vue.js 的自动演奏器，可以自动演奏游戏中的乐器。

## 功能特点

- 通过定义乐谱自动演奏游戏乐器
- 支持调节演奏速度和按键延迟
- 提供多种示例乐谱
- 支持循环播放

## 技术栈

- **后端**：FastAPI (Python)
- **前端**：Vue 3 + Element Plus
- **通信**：RESTful API

## 安装和运行

### 环境要求

- Python 3.7+
- Node.js 14+
- npm 6+

### 安装步骤

1. **克隆项目：**
   ```bash
   git clone [你的仓库地址]
   cd [项目目录]
   ```

2. **安装后端依赖：**
   ```bash
   pip install -r requirements.txt
   ```

3. **安装前端依赖：**
   ```bash
   cd music-player-frontend
   npm install
   ```

### 运行项目

**方式一：使用启动脚本**
```bash
python start.py
```

**方式二：分别启动前后端**

- **启动后端：**
  ```bash
  python main.py
  ```

- **启动前端：**
  ```bash
  cd music-player-frontend
  npm run dev
  ```

启动成功后，访问 `http://localhost:5173` 使用应用。

## 使用说明

1. 确保游戏窗口在前台。
2. 在前端界面编辑乐谱或选择示例乐谱。
3. 点击“开始演奏”按钮。
4. 如需停止，点击“停止演奏”按钮。

## 注意事项

- 部分游戏可能将自动按键视为作弊行为，请谨慎使用。
- 使用前请确保游戏窗口处于前台。