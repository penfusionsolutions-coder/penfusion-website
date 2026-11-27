# PenFusion Solutions website

Live test site: https://new.penfusionsolutions.com (GitHub Pages, from the `main` branch).

Coded from the Claude Design canvas "PenFusion Solutions Website"
(https://claude.ai/artifact/9Vzhudg15QUD4x9ZRLmyu1).

## Files

- `design/Main.dc.html`: the design canvas source (copied from the artifact).
- `index.html`: the homepage, generated from the design. Don't edit by hand; regenerate it.
- `privacy.html`, `terms.html`, `legal.css`: Privacy Policy and Terms of Service pages.
- `convert.py`: turns `design/Main.dc.html` into `index.html` and wires up the contact form.
- `CNAME`: tells GitHub Pages to serve the site at new.penfusionsolutions.com.

## Updating after editing the design

1. Edit the design canvas on claude.ai.
2. Ask Claude Code: "update the site from my latest design". It copies the canvas's
   `project/Main.dc.html` to `design/Main.dc.html` and runs:

   ```
   python convert.py design/Main.dc.html index.html
   ```

3. Commit and push. GitHub Pages republishes in about a minute.

## Contact form

Submissions go to info@penfusionsolutions.com through FormSubmit (formsubmit.co).
The very first submission triggers an activation email from FormSubmit to that inbox;
click its link once and later submissions are delivered. The address is set in
`FORM_EMAIL` at the top of `convert.py`.

## Before going live on the main domain

- Remove `<meta name="robots" content="noindex, nofollow">` (in `convert.py`, `privacy.html`, `terms.html`).
- Point `penfusionsolutions.com` and `www` DNS at GitHub Pages and update `CNAME`.
- Have the Privacy Policy and Terms reviewed; they are general templates, not legal advice.
