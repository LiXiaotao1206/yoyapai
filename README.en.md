# yoyapai

Fetch the latest free Clash subscription from [yoyapai.com](https://yoyapai.com/category/mianfeijiedian) and update a stable subscription URL automatically with GitHub Actions.

## Stable subscription URL

GitHub Pages (enabled):

```text
https://lixiaotao1206.github.io/yoyapai/yoyapai.yaml
```

GitHub raw (may be blocked in some regions):

```text
https://raw.githubusercontent.com/LiXiaotao1206/yoyapai/master/yoyapai.yaml
```

## How it works

1. Fetch the category page `https://yoyapai.com/category/mianfeijiedian`.
2. The page is sorted newest first; take the first post (its title contains the latest date, for example, `11月20日`). It does not have to be today.
3. Extract the `.yaml` URL from the "Clash (Clash Meta/Mihomo)" subscription code block.
4. Extract the latest subscription date from the webpage, write it as the first line `# 最新订阅日期: YYYY-MM-DD`, and save the result as `yoyapai.yaml` (UTF-8).

## Date comment

The first line of the generated `yoyapai.yaml` looks like:

```text
# 最新订阅日期: 2026-11-21
```

The date comes from the latest subscription URL path, the article's `datePublished`, or the article title. It is **not** the system time when the script runs.

## Local usage

Requires Python 3.9+ and network access to `yoyapai.com` and `freenode.yoyapai.com` (set `HTTPS_PROXY` if needed).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python yoyapai.py
```

Custom output path:

```bash
python yoyapai.py -o /path/to/yoyapai.yaml
```

## GitHub Actions

The repository includes `.github/workflows/yoyapai.yml`: it is scheduled daily at 04:00 and 12:00 Beijing time and commits `yoyapai.yaml` only when the content changes.

1. Settings → Actions → General → Workflow permissions → select "Read and write permissions".
2. Actions → `yoyapai-daily` → Run workflow to test manually.
3. Settings → Pages → Build and deployment → Source: "Deploy from a branch" → Branch: `master`, folder `/ (root)` → Save.
4. Wait for the Pages deployment, then use the stable URL.

Notes:

- GitHub Actions cron uses UTC: `0 20 * * *` is 04:00 the next day in Beijing, and `0 4 * * *` is 12:00 the same day. If the site has not published today's subscription yet, the script fetches the latest available one. Scheduled runs may be delayed.
- In public repositories, scheduled workflows are disabled after 60 days without repository activity; the subscription date on the first line changes daily, so the workflow usually creates a commit every day and stays active.
- Pages rebuilds after each commit, with a 1–2 minute delay.
- If GitHub Pages/raw is unavailable in your region, use Aliyun OSS or Tencent COS.
- The repository and `yoyapai.yaml` are public; node information is exposed.
- Free nodes come from unknown sources. Use them for testing only, and never sign in to banking, email, or other sensitive accounts through them.
