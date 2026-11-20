# yoyapai

Fetch today's free Clash subscription from [yoyapai.com](https://yoyapai.com/category/mianfeijiedian) and save it as `yoyapai.yaml`.

## How it works

1. Fetch the category page `https://yoyapai.com/category/mianfeijiedian`.
2. Find the post whose title contains today's date (for example, `11月20日`) and open its link, such as `https://yoyapai.com/839`.
3. Extract the `.yaml` URL from the "Clash (Clash Meta/Mihomo)" subscription code block.
4. Download the subscription and save it verbatim as `yoyapai.yaml` (UTF-8).

"Today" is evaluated in the Asia/Shanghai time zone.

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

The site usually publishes in the morning. Example crontab entry (every day at 11:10):

```cron
10 11 * * * cd /path/to/yoyapai && .venv/bin/python yoyapai.py >> fetch.log 2>&1
```

## Notes

- If today's post is not published yet, the script exits with status 1 and lists the latest posts. It will not overwrite an existing `yoyapai.yaml` with stale data.
- The response is validated (not HTML, contains Clash config fields) before the output file is replaced atomically.
- Free nodes come from unknown sources. Use them for testing only, and never sign in to banking, email, or other sensitive accounts through them.
