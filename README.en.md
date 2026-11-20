# yoyapai

Fetch the latest free Clash subscription from [yoyapai.com](https://yoyapai.com/category/mianfeijiedian) and save it as `yoyapai.yaml`.

## Stable subscription URL

Gitee raw URL:

```text
https://gitee.com/qingshan1206/yoyapai/raw/master/yoyapai.yaml
```

> Note: Gitee currently returns `451 Unavailable For Legal Reasons` (`The content may contain violation information`) for this YAML, so it cannot be used directly in Clash. Raw access to the `.py` and `.md` files works; only `yoyapai.yaml` is blocked by content moderation. Use object storage, a VPS, or GitHub instead.

## How it works

1. Fetch the category page `https://yoyapai.com/category/mianfeijiedian`.
2. The page is sorted newest first; take the first post (its title contains the latest date, for example, `11月20日`). It does not have to be today.
3. Extract the `.yaml` URL from the "Clash (Clash Meta/Mihomo)" subscription code block.
4. Download the subscription and save it verbatim as `yoyapai.yaml` (UTF-8).

## Requirements

- Python 3.9+
- Network access to `yoyapai.com` and `freenode.yoyapai.com` (set `HTTPS_PROXY` if needed)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python yoyapai.py
```

Custom output path:

```bash
python yoyapai.py -o /path/to/yoyapai.yaml
```

## Schedule

The script does not depend on the current date; it always takes the newest post on the category page:

- After 11:30 Beijing time, this is usually today's post (the site published between 09:54 and 11:18 over the last nine days).
- At 08:00, it is the previous day's post if today's is not published yet; the job still succeeds.

The Gitee Go pipeline is currently set to 11:30. To run at 08:00 as originally planned, change the cron to `0 0 8 * * ?`.

### Gitee Go (cloud, recommended)

The repository includes `.workflow/yoyapai.yml`: it runs daily at 11:30 Beijing time and commits the latest `yoyapai.yaml` back to `master`, updating the stable URL above.

1. Make the repository public: Manage → Basic information → make public. A private repository's raw URL cannot be fetched by Clash.
2. Create a Gitee personal access token with `projects` (repository read/write) permission.
3. In Gitee Go's global/general variables (or environment variables), add `YOYAPAI_TOKEN` with the token value and mark it secret/encrypted.
4. Open the repository → Pipelines (Gitee Go) and enable it. Phone binding is required; each repository gets 200 free build minutes per month.
5. If the `yoyapai-daily` pipeline is not created automatically, create one, paste the contents of `.workflow/yoyapai.yml`, and save it.
6. Confirm the schedule is `0 30 11 * * ?`, then run it once manually. A successful run adds a `chore: update yoyapai.yaml` commit.

Notes:

- Gitee Go uses six-field cron: `second minute hour day month weekday`.
- If build timestamps are eight hours off from Beijing time, change the hour to 3: `0 30 3 * * ?`; for 08:00 use `0 0 0 * * ?`.
- `YOYAPAI_TOKEN` belongs only in Gitee Go variables; do not commit it. The token only needs write access to this repository; revoke it immediately if leaked.
- The YAML (including node credentials) becomes public when the repository is public; evaluate the risk.
- Gitee may moderate proxy/VPN content. If the repository is restricted, the URL stops working, so keep a local or alternative backup.

### Local crontab

```cron
30 11 * * * cd /path/to/yoyapai && .venv/bin/python yoyapai.py >> fetch.log 2>&1
```

Local crontab only updates the local file; commit and push separately to update the Gitee URL, or use the Gitee Go setup above.

## Notes

- If the category page cannot be parsed or contains no dated posts, the script exits with status 1 and will not overwrite an existing `yoyapai.yaml`.
- The response is validated (not HTML, contains Clash config fields) before the output file is replaced atomically.
- Free nodes come from unknown sources. Use them for testing only, and never sign in to banking, email, or other sensitive accounts through them.
