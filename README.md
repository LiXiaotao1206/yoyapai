# yoyapai

每天抓取 [优雅数字派](https://yoyapai.com/category/mianfeijiedian) 最新日期的免费 Clash 订阅，并保存为 `yoyapai.yaml`。

## 固定订阅地址

仓库改为公开后，可以直接填入 Clash：

```text
https://gitee.com/qingshan1206/yoyapai/raw/master/yoyapai.yaml
```

Gitee 会重定向到 `raw.giteeusercontent.com`，Clash 会自动跟随；Gitee 对 raw 文件有 60–300 秒缓存。仓库中的 `yoyapai.yaml` 已提交一份最新数据，之后由 Gitee Go 每天自动更新。

## 工作流程

1. 请求分类页 `https://yoyapai.com/category/mianfeijiedian`；
2. 分类页按发布时间倒序排列，取第一篇文章（标题中的日期即最新日期，例如“11月20日”），不要求日期是今天；
3. 请求文章页，读取“Clash（Clash Meta/Mihomo）免费节点订阅地址”代码块里的 `.yaml` 链接；
4. 下载订阅内容，按 UTF-8 原样保存为 `yoyapai.yaml`。

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
[1/3] 获取分类页：https://yoyapai.com/category/mianfeijiedian
[2/3] 最新文章：2026免费节点分享88个丨每日更新Clash/V2Ray/SSR最新机场订阅丨11月20日
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

脚本不依赖当天日期，总是抓取分类页当前最新的一篇：

- 11:30 之后运行，通常能拿到当天文章（站点最近 9 天的发布时间为 09:54–11:18）；
- 8:00 运行会拿到前一天的文章（如果当天还未发布），任务仍然成功。

当前 Gitee Go 流水线按 11:30 配置；如果希望像最初计划那样每天 8:00 跑，把 cron 改成 `0 0 8 * * ?` 即可。

### Gitee Go（云端，推荐）

仓库已包含 `.workflow/yoyapai.yml`，每天北京时间 11:30 执行，并自动把最新的 `yoyapai.yaml` 提交回 `master`，从而更新上面的固定地址。

首次使用：

1. 把仓库改为公开：仓库 →「管理」→「基本信息」→ 仓库公开/开源。私有仓库的 raw 地址无法被 Clash 直接拉取。
2. 生成私人令牌：Gitee 头像 →「设置」→「安全设置」→「私人令牌」→ 生成新令牌，勾选 `projects`（仓库读写）权限，复制令牌。
3. 在 Gitee Go 的「全局参数 / 通用变量 / 环境变量」中添加变量 `YOYAPAI_TOKEN`，值为刚复制的令牌，并勾选加密/私密（不同版本菜单名可能不同）。
4. 打开仓库 →「流水线」（Gitee Go），按提示开通。账号需绑定手机号；每个仓库每月有 200 分钟免费构建时长。
5. 如果流水线列表里没有自动出现 `yoyapai-daily`，点击「新建流水线」→ 选择空模板/自定义，把 `.workflow/yoyapai.yml` 的内容粘贴进去并保存。
6. 在「定时触发」中确认 cron 为 `0 30 11 * * ?`，然后点击「立即执行」测试。成功后会新增一条 `chore: update yoyapai.yaml` 提交，raw 地址随即更新。

说明：

- Gitee Go 的 cron 为 6 段格式：`秒 分 时 日 月 周`。
- 如果构建记录显示的时间与北京时间相差 8 小时，把 cron 的小时改为 3，即 `0 30 3 * * ?`；8:00 对应 `0 0 0 * * ?`。
- `YOYAPAI_TOKEN` 只放在 Gitee Go 变量里，不要写进仓库；令牌只需要该仓库的写权限，泄露后立即在 Gitee 设置中撤销。
- 仓库公开后，`yoyapai.yaml` 里的节点信息也会公开，请自行评估风险。
- Gitee 可能对代理/VPN 类内容进行审核；如果仓库被限制，固定地址会失效，建议保留本地或其他托管方式作为备份。

### 本机 crontab

```cron
30 11 * * * cd /path/to/yoyapai && .venv/bin/python yoyapai.py >> fetch.log 2>&1
```

本机 crontab 只更新本地文件；如果要更新 Gitee 上的固定地址，需要再执行 `git add/commit/push`，或直接使用上面的 Gitee Go 方案。

## 说明

- 脚本只要求分类页能解析出带日期的文章；如果页面结构变化或没有文章，会以退出码 1 结束，并且不会覆盖已有的 `yoyapai.yaml`。
- 下载内容会做基本校验（非 HTML、包含 Clash 配置字段），确认无误后才原子替换 `yoyapai.yaml`。
- 免费节点来源不明，仅供学习与测试，请勿用于登录网银、邮箱等重要账号。
