# yoyapai

Fetch the latest free Clash subscription from [yoyapai.com](https://yoyapai.com/category/mianfeijiedian) and update a stable subscription URL automatically with GitHub Actions.

## Stable subscription URL

After enabling GitHub Pages:

```text
https://lixiaotao1206.github.io/yoyapai/yoyapai.yaml
```

GitHub raw (may be blocked in some regions):

```text
https://raw.githubusercontent.com/LiXiaotao1206/yoyapai/master/yoyapai.yaml
```

> Gitee raw returns 451 for this file and is no longer used.

## How it works

1. Fetch the category page `https://yoyapai.com/category/mianfeijiedian`.
2. The page is sorted newest first; take the first post (its title contains the latest date, for example, `11月20日`). It does not have to be today.
3. Extract the `.yaml` URL from the "Clash (Clash Meta/Mihomo)" subscription code block.
4. Download the subscription and save it verbatim as `yoyapai.yaml` (UTF-8).

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

The repository includes `.github/workflows/yoyapai.yml`: it runs daily at 11:30 Beijing time and commits `yoyapai.yaml`.

1. Settings → Actions → General → Workflow permissions → select "Read and write permissions".
2. Actions → `yoyapai-daily` → Run workflow to test manually.
3. Settings → Pages → Build and deployment → Source: "Deploy from a branch" → Branch: `master`, folder `/ (root)` → Save.
4. Wait for the Pages deployment, then use the stable URL.

Notes:

- GitHub Actions cron is UTC: `30 3 * * *` = 11:30 Beijing; use `0 0 * * *` for 08:00. The script always takes the newest post, so an 08:00 run usually gets the previous day's data.
- In public repositories, scheduled workflows are disabled after 60 days without repository activity; the daily commit usually keeps it active.
- Pages rebuilds after each commit, with a 1–2 minute delay.
- If GitHub Pages/raw is unavailable in your region, use Aliyun OSS or Tencent COS.
- The Gitee `.workflow/yoyapai.yml` does not run on GitHub Actions. Disable the Gitee Go pipeline to avoid divergence.
- The repository and `yoyapai.yaml` are public; node information is exposed.
- Free nodes come from unknown sources. Use them for testing only, and never sign in to banking, email, or other sensitive accounts through them.
