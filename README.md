# Local File Server

基于 FastAPI 的本地文件服务器，支持文件浏览、下载（含断点续传）、上传和目录创建。

## 安装

```bash
pip install -r requirements.txt
```

## 配置

复制 `.env.example` 为 `.env` 并按需修改：

```bash
cp .env.example .env
```

| 环境变量 | 默认值 | 说明 |
|---|---|---|
| `LFS_ROOT_DIR` | `~` | 对外暴露的根目录 |
| `LFS_HOST` | `0.0.0.0` | 监听地址 |
| `LFS_PORT` | `12000` | 监听端口 |
| `LFS_AUTH_ENABLED` | `false` | 是否启用 HTTP Basic 认证 |
| `LFS_AUTH_USERNAME` | `admin` | 认证用户名 |
| `LFS_AUTH_PASSWORD` | _(空)_ | 认证密码 |
| `LFS_ALLOW_DELETE` | `false` | 是否允许删除文件 |
| `LFS_MAX_UPLOAD_SIZE` | `10737418240` | 最大上传大小（字节，默认 10GB） |

环境变量也可以直接在 shell 中设置，优先级高于 `.env` 文件：

```bash
LFS_ROOT_DIR=/data LFS_PORT=8080 python main.py
```

---

## 启动方式

### 1. 直接运行

```bash
python main.py
```

### 2. systemd 服务（开机自启）

将配置文件放到 `~/.config/local-file-server.env`（内容与 `.env` 相同），然后：

```bash
# 安装服务单元
cp local-file-server.service ~/.config/systemd/user/

# 启用并启动
systemctl --user daemon-reload
systemctl --user enable local-file-server
systemctl --user start local-file-server

# 查看状态 / 日志
systemctl --user status local-file-server
journalctl --user -u local-file-server -f
```

---

## 使用方式

### 浏览器 Web UI

访问 `http://<host>:12000`，可视化浏览目录、下载和上传文件。

---

### 命令行（curl / wget）

以下示例默认服务运行在 `http://localhost:12000`，未启用认证。  
启用认证时，所有请求加 `-u admin:yourpassword`。

#### 健康检查

```bash
curl http://localhost:12000/health
```

#### 列出目录

```bash
# 列出根目录
curl http://localhost:12000/api/list

# 列出子目录
curl "http://localhost:12000/api/list?path=Documents"
```

#### 下载文件

```bash
# 下载到当前目录，保留原文件名（-J 读取服务端 Content-Disposition 头）
curl -OJ "http://localhost:12000/api/download?path=Documents/report.pdf"

# 指定保存路径
curl -o /tmp/report.pdf "http://localhost:12000/api/download?path=Documents/report.pdf"

# 断点续传（-C - 自动检测已下载字节数）
curl -C - -OJ "http://localhost:12000/api/download?path=Videos/movie.mp4"

# wget 下载
wget "http://localhost:12000/api/download?path=Documents/report.pdf"

# wget 断点续传
wget -c "http://localhost:12000/api/download?path=Videos/movie.mp4"
```

#### 上传文件

```bash
# 上传到根目录
curl -F "file=@/path/to/local/file.txt" http://localhost:12000/api/upload

# 上传到指定子目录
curl -F "file=@/path/to/local/file.txt" "http://localhost:12000/api/upload?path=Documents"
```

#### 创建目录

```bash
curl "http://localhost:12000/api/mkdir?path=NewFolder/SubFolder"
```

#### 带认证的请求

```bash
curl -u admin:yourpassword "http://localhost:12000/api/list?path=Documents"
```

---

### Python 脚本调用

```python
import requests

BASE = "http://localhost:12000"

# 列出目录
resp = requests.get(f"{BASE}/api/list", params={"path": "Documents"})
data = resp.json()
for f in data["files"]:
    print(f["name"], f["size_human"])

# 下载文件（流式，适合大文件）
with requests.get(f"{BASE}/api/download", params={"path": "Videos/movie.mp4"}, stream=True) as r:
    with open("movie.mp4", "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            f.write(chunk)

# 上传文件
with open("report.pdf", "rb") as f:
    resp = requests.post(f"{BASE}/api/upload", files={"file": f}, params={"path": "Documents"})
print(resp.json())
```

---

## API 速览

| 方法 | 路径 | 参数 | 说明 |
|---|---|---|---|
| GET | `/health` | — | 服务健康状态 |
| GET | `/api/list` | `path`（可选） | 列出目录内容 |
| GET | `/api/download` | `path` | 下载文件，支持 Range 断点续传 |
| POST | `/api/upload` | `path`（可选），`file`（multipart） | 上传文件 |
| GET | `/api/mkdir` | `path` | 创建目录（含中间层级） |
