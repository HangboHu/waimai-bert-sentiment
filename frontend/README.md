# 听见 · 外卖评价情感分析

苹果风格的中文响应式界面，使用 Vue 3 Composition API、单文件组件、CSS 和 Vite。所有分析结果来自项目的 Flask 接口；示例按钮只填入评价，不生成模拟结果。

页面使用视口高度自适应布局，桌面端输入与结果并排展示，移动端紧凑上下排列。标题、输入、统计、操作与页脚在一屏内展示，长文本和结果在各自区域内滚动。为保持文字与操作可读，桌面端最低布局高度为 580px，移动端为 720px；低于此高度或浏览器放大时允许页面滚动，不裁切功能。

`src/App.vue` 组织页面与连接设置，`components/InputPanel.vue`、`ResultsPanel.vue` 分别负责输入和结果，`composables/useAnalysis.js` 集中管理请求与响应式状态，`src/api.js` 负责接口请求及响应校验。

## 本地启动

需要 Node.js 20.19+ 或 22.12+，以及能够运行本项目模型的 Python 环境。

在项目根目录启动后端（确保 `model/ft_bert_dir` 和 `model/thy_labels.txt` 存在，Python 环境已安装 Flask、PyTorch、Transformers 等后端依赖）：

```powershell
python wsgi.py
```

另开终端启动前端：

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

打开 <http://127.0.0.1:5173>。Windows PowerShell 使用 `npm.cmd` 可避免 `npm.ps1` 执行策略限制；其他终端可使用 `npm`。

开发服务器将 `/api` 代理到 `http://127.0.0.1:8000`。后端端口不同，可将 `.env.example` 复制为 `.env.local` 并修改 `API_PROXY_TARGET`，之后重启前端。右上角的「连接设置」也支持填写完整接口基础地址（如 `http://127.0.0.1:8000/api/v1`），保存在当前浏览器中。「恢复默认」后需点击「保存并连接」。

## 功能

- 单条或多行文本分析，空行自动跳过；支持 Ctrl / Command + Enter 提交。
- UTF-8 TXT 文件选择、拖放、编码检查和预览条数；支持带 BOM 的文件。
- 展示真实分类、置信度、高置信度条数和平均置信度；低置信度结果提示复核。
- 按返回的分类筛选、按文本搜索；导出全部结果为带 UTF-8 BOM 的 CSV，方便 Excel 打开。
- 连接状态、重试、加载状态、超时、错误提示；请求失败时保留上一次成功结果。
- 适配桌面和移动端，支持键盘操作、读屏状态提示和减少动态效果偏好。

每次最多 500 条，上传文件不超过 2 MB。这是前端为避免误提交超大批次设置的限制，并非后端服务端限制。文本输入框最多 100,000 个字符。当前后端对每条文本使用 `max_length=32` 截断，长评价的判断可能不覆盖全部内容。

评价内容和分析结果只保留在当前页面内存，刷新后清空；连接地址保存在 localStorage。CSV 导出始终包含本次全部结果，不受筛选条件影响，并对可能被表格软件解释为公式的字段进行转义。

## 接口对应

| 功能 | 接口 | 请求 |
| --- | --- | --- |
| 服务检查 | `GET /api/v1/` | 无 |
| 分类标签 | `GET /api/v1/labels` | 无 |
| 文本分析 | `POST /api/v1/classify` | JSON：`{"text":"评价"}` 或 `{"text":["评价1","评价2"]}` |
| 文件分析 | `POST /api/v1/classify_from_file` | multipart 表单，文件字段 `text_file` |

后端响应使用 `code` 表示业务状态，分析结果读取 `results` 数组中的 `text`、`label`、`confidence`（百分比字符串）与 `is_certain`。

## 构建与部署

```powershell
npm.cmd run build
npm.cmd run preview
```

构建输出在 `frontend/dist`。本地预览地址为 <http://127.0.0.1:4173>，同样配置了 `/api` 代理。

生产环境将 `dist` 部署到静态服务器，在同域反向代理 `/api/` 到 Flask 服务，例如 Nginx：

```nginx
location / {
    root /path/to/frontend/dist;
    try_files $uri $uri/ /index.html;
}

location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_read_timeout 120s;
}
```

Vite 的开发代理不会打包进静态文件。如使用跨域地址，后端需允许该前端来源；HTTPS 页面应连接 HTTPS 接口。

## 后端联调修复

`app/extensions.py` 的 `warmup()` 原先引用了未定义的 `self.preprocessor` 属性，导致后端启动时抛出 `AttributeError`。此分支移除了该无效引用，文本清洗仍使用已有的 `clean_text_for_bert` 函数。

本机使用 CUDA 推理时，原实现将输入移至 GPU，但模型仍在 CPU，导致分析接口返回 500。模型加载后现会移动到 `self.device` 并设置为评估模式，使模型和输入设备一致。
