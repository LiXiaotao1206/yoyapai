# yoyapai

Fetch the latest free Clash subscription from [yoyapai.com](https://yoyapai.com/category/mianfeijiedian) and save it as `yoyapai.yaml`.

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

The repository includes `.workflow/yoyapai.yml`: it runs daily at 11:30 Beijing time and uploads the result as a pipeline artifact.

1. Open the Gitee repository → Pipelines (Gitee Go) and enable it. Phone binding is required; each repository gets 200 free build minutes per month.
2. If the `yoyapai-daily` pipeline is not created automatically, create one, paste the contents of `.workflow/yoyapai.yml`, and save it.
3. Confirm the schedule is `0 30 11 * * ?`, then run it once manually to test.
4. After a successful run, download the `yoyapai` artifact from the release records; it contains `dist/yoyapai.yaml`.

Notes:

- Gitee Go uses six-field cron: `second minute hour day month weekday`.
- If build timestamps are eight hours off from Beijing time, change the hour to 3: `0 30 3 * * ?`.
- For an 08:00 run with UTC build time, use `0 0 0 * * ?` (00:00 UTC = 08:00 Beijing).
- Artifacts are not a stable subscription URL. For a stable `.../raw/.../yoyapai.yaml` URL, commit the file back with a personal access token.

### Local crontab

```cron
30 11 * * * cd /path/to/yoyapai && .venv/bin/python yoyapai.py >> fetch.log 2>&1
```

## Notes

- If the category page cannot be parsed or contains no dated posts, the script exits with status 1 and will not overwrite an existing `yoyapai.yaml`.
- The response is validated (not HTML, contains Clash config fields) before the output file is replaced atomically.
- Free nodes come from unknown sources. Use them for testing only, and never sign in to banking, email, or other sensitive accounts through them.
