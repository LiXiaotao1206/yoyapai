# yoyapai

每天抓取 [优雅数字派](https://yoyapai.com/category/mianfeijiedian) 的免费 Clash 订阅，并保存为 `yoyapai.yaml`。

## 工作流程

1. 请求分类页 `https://yoyapai.com/category/mianfeijiedian`；
2. 根据文章标题中的“11月20日”找到当天的文章，例如 `https://yoyapai.com/839`；
3. 请求文章页，读取“Clash（Clash Meta/Mihomo）免费节点订阅地址”代码块里的 `.yaml` 链接；
4. 下载订阅内容，按 UTF-8 原样保存为 `yoyapai.yaml`。

脚本以北京时间判断“今天”。

## 环境要求

- Python 3.9+
- 能访问 `yoyapai.com` 和 `freenode.yoyapai.com`（如需要，可设置 `HTTPS_PROXY`）

## 安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 使用

```bash
python yoyapai.py
```

成功时输出类似：

```text
日期：2026-11-20（北京时间）
[1/3] 获取分类页：https://yoyapai.com/category/mianfeijiedian
[2/3] 今日文章：2026免费节点分享88个丨每日更新Clash/V2Ray/SSR最新机场订阅丨11月20日
      链接：https://yoyapai.com/839
      订阅：https://freenode.yoyapai.com/2026/11/20-yoyapai.com-clash-vpn-mian-fei-jie-dian.yaml
[3/3] 下载 Clash 订阅内容 ...
完成：/path/to/yoyapai.yaml（127,353 字节）
```

指定输出路径：

```bash
python yoyapai.py -o /path/to/yoyapai.yaml
```

## 定时运行

站点最近 9 天的发布时间为 09:54–11:18（北京时间），因此建议 11:30 之后再运行。不建议 8:00 运行：此时当天文章通常还没发布，脚本会以退出码 1 结束。

### Gitee Go（云端，推荐）

仓库已包含 `.workflow/yoyapai.yml`，每天北京时间 11:30 执行，并把结果上传为流水线制品。

首次使用：

1. 打开 Gitee 仓库 →「流水线」（Gitee Go），按提示开通。账号需绑定手机号；每个仓库每月有 200 分钟免费构建时长。
2. 如果流水线列表里没有自动出现 `yoyapai-daily`，点击「新建流水线」→ 选择空模板/自定义，把 `.workflow/yoyapai.yml` 的内容粘贴进去并保存。
3. 在流水线的「定时触发」中确认 cron 为 `0 30 11 * * ?`，然后点击「立即执行」测试。
4. 构建成功后，在「发布记录」下载 `yoyapai` 制品，里面是 `dist/yoyapai.yaml`。

说明：

- Gitee Go 的 cron 为 6 段格式：`秒 分 时 日 月 周`。
- 如果构建记录显示的时间与北京时间相差 8 小时，把 cron 的小时改为 3，即 `0 30 3 * * ?`。
- 制品不是固定的订阅 URL。如果需要 `https://gitee.com/qingshan1206/yoyapai/raw/.../yoyapai.yaml` 这样的固定地址，需要配置私人令牌把文件回写到仓库。

### 本机 crontab

```cron
30 11 * * * cd /path/to/yoyapai && .venv/bin/python yoyapai.py >> fetch.log 2>&1
```

## 说明

- 若当天文章尚未发布，脚本会以退出码 1 结束，并列出最近几篇文章的标题；此时不会用旧数据覆盖已有的 `yoyapai.yaml`。
- 下载内容会做基本校验（非 HTML、包含 Clash 配置字段），确认无误后才原子替换 `yoyapai.yaml`。
- 免费节点来源不明，仅供学习与测试，请勿用于登录网银、邮箱等重要账号。
