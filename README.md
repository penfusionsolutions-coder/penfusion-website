# PenFusion Solutions website

Coded homepage for penfusionsolutions.com, converted from the Claude Design canvas
"PenFusion Solutions Website" (https://claude.ai/artifact/9Vzhudg15QUD4x9ZRLmyu1).

## Files

- `index.html` — the whole site: one static page, no build step. Open it in a browser to preview.
- `convert.py` — turns the design canvas's `Main.dc.html` into `index.html`.

## Updating after editing the design

1. Edit the design canvas on claude.ai.
2. Ask Claude Code: "update the site from my latest design". It downloads `Main.dc.html` and runs:

   ```
   python convert.py Main.dc.html index.html
   ```

3. Commit and push the new `index.html`.

## Still to do before going live

- Contact form only shows "Request received"; it doesn't send anywhere yet.
- "Response within [RESPONSE TIME]" placeholder needs a real value.
- Job listings: confirm they are real openings.
- Client Portal, Privacy Policy and Terms links go nowhere yet.
- The page has `noindex` set while it's a test site; remove it from `index.html` at launch.
