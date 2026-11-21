# yoyapai

每天抓取 [优雅数字派](https://yoyapai.com/category/mianfeijiedian) 最新日期的免费 Clash 订阅，并通过 GitHub Actions 自动更新。

## 固定订阅地址

GitHub Pages（已启用），可直接填入 Clash：

```text
https://lixiaotao1206.github.io/yoyapai/yoyapai.yaml
```

GitHub raw（部分地区可能无法访问）：

```text
https://raw.githubusercontent.com/LiXiaotao1206/yoyapai/master/yoyapai.yaml
```

## 工作流程

1. 请求分类页 `https://yoyapai.com/category/mianfeijiedian`；
2. 分类页按发布时间倒序排列，取第一篇文章（标题中的日期即最新日期，例如“11月20日”），不要求日期是今天；
3. 请求文章页，读取“Clash（Clash Meta/Mihomo）免费节点订阅地址”代码块里的 `.yaml` 链接；
4. 从网页内容中解析最新订阅日期，写入文件第一行 `# 最新订阅日期: YYYY-MM-DD`，再按 UTF-8 保存为 `yoyapai.yaml`。

## 日期注释

生成的 `yoyapai.yaml` 第一行形如：

```text
# 最新订阅日期: 2026-11-21
```

日期取自网页中最新订阅的 URL 路径、文章 `datePublished` 或文章标题，**不是脚本运行时的系统时间**。

## 本地运行

环境要求：Python 3.9+，能访问 `yoyapai.com` 和 `freenode.yoyapai.com`（如需要，可设置 `HTTPS_PROXY`）。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python yoyapai.py
```

指定输出路径：

```bash
python yoyapai.py -o /path/to/yoyapai.yaml
```

成功时输出类似：

```text
[1/3] 获取分类页：https://yoyapai.com/category/mianfeijiedian
[2/3] 最新文章：2026免费节点分享87个丨每日更新Clash/V2Ray/SSR最新机场订阅丨11月21日
      链接：https://yoyapai.com/844
      订阅：https://freenode.yoyapai.com/2026/11/21-yoyapai.com-clash-vpn-mian-fei-jie-dian.yaml
      最新订阅日期：2026-11-21
[3/3] 下载 Clash 订阅内容 ...
完成：/path/to/yoyapai.yaml（129,981 字节）
```

## GitHub Actions 定时更新

仓库包含 `.github/workflows/yoyapai.yml`：每天北京时间 11:30 运行，抓取后自动提交 `yoyapai.yaml`。

首次使用：

1. 仓库 Settings → Actions → General → Workflow permissions，选择「Read and write permissions」。
2. 打开 Actions → `yoyapai-daily` → Run workflow，手动测试。
3. 仓库 Settings → Pages → Build and deployment → Source 选择「Deploy from a branch」→ Branch 选 `master`、目录 `/ (root)` → Save。
4. 等 Pages 部署完成，访问固定地址。

说明：

- GitHub Actions 的 cron 使用 UTC：`30 3 * * *` = 11:30 北京；要 8:00 改成 `0 0 * * *`。脚本总是取页面最新文章，所以 8:00 会拿到前一天的最新订阅。
- 公开仓库连续 60 天无活动，定时工作流会被暂停；第一行的订阅日期每天变化，因此每天都会产生一次提交，通常能保持活跃。
- Pages 在每次提交后自动重建，通常有 1–2 分钟延迟。
- 如果 GitHub Pages/raw 在国内不可用，建议改用阿里云 OSS / 腾讯云 COS 托管。
- 仓库和 `yoyapai.yaml` 是公开的，节点信息会公开，请自行评估风险。
- 免费节点来源不明，仅供学习与测试，请勿用于登录网银、邮箱等重要账号。
