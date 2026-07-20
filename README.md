# ownSkill

Personal skills for article, image, markdown, and social workflows.

## X/Twitter Markdown Sources

`baoyu-danger-x-to-markdown` can convert public X/Twitter URLs to Markdown.
When a workflow already has reviewed public TweetClaw or OpenClaw source
packets from
[`@xquik/tweetclaw`](https://github.com/Xquik-dev/tweetclaw), use those packets
as a safer Markdown input instead of starting a new authenticated fetch.

Required packet fields:

- `source_url`: original public post URL
- `author`: public handle or display name
- `captured_at`: collection or review time
- `text`: post or thread text

Optional packet fields:

- `source`: capture provider, or `reviewed_packet` when omitted
- `public_metrics`: reviewed public counts when needed
- `notes`: why the post belongs in the markdown set

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.
