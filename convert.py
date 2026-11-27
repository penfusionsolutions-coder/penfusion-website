"""Convert a Design canvas .dc.html artboard into a standalone static page.

Usage: python -I convert.py design/Main.dc.html index.html
"""
import re
import sys

# Contact form submissions are emailed here through FormSubmit (formsubmit.co).
FORM_EMAIL = "info@penfusionsolutions.com"

src_path, out_path = sys.argv[1], sys.argv[2]
src = open(src_path, encoding="utf-8").read()

title = re.search(r"<title>(.*?)</title>", src, re.S).group(1)
helmet = re.search(r"<helmet>(.*?)</helmet>", src, re.S).group(1).strip()
body = re.search(r"</helmet>(.*?)</x-dc>", src, re.S).group(1).strip()
logic = re.search(r"renderVals\(\) \{(.*?)var self = this;", src, re.S).group(1)
industries_js = re.search(r"var data = (\[.*?\]);", logic, re.S).group(1)
# Styles that live in the design's script/template, so color changes in the design carry over
tab_base = re.search(r"var base = '([^']*)';", src).group(1)
tab_on, tab_off = re.search(r"tabStyle: base \+ \(on\s*\?\s*'([^']*)'\s*:\s*'([^']*)'\)", src).groups()
check_svg = re.search(r'<sc-for list="\{\{active\.apps\}\}".*?(<svg.*?</svg>)', src, re.S).group(1)


def sub_once(pattern, repl, text):
    new, n = re.subn(pattern, lambda m: repl, text, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"pattern not found: {pattern[:60]}")
    return new


# Industry tabs and active panel
body = sub_once(r'<sc-for list="\{\{industries\}\}".*?</sc-for>', "", body)
body = body.replace('<div role="tablist" aria-label="Industries"', '<div id="pf-tabs" role="tablist" aria-label="Industries"')
body = body.replace("{{active.kicker}}", '<span id="pf-kicker"></span>')
body = body.replace("{{active.name}}", '<span id="pf-ind-name"></span>')
body = body.replace("{{active.summary}}", '<span id="pf-summary"></span>')
body = sub_once(r'(<ul )(style="flex: 1 1 340px;[^"]*">)\s*<sc-for list="\{\{active\.apps\}\}".*?</sc-for>\s*</ul>',
                '<ul id="pf-apps" style="flex: 1 1 340px; min-width: 0; margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 12px"></ul>', body)

# Contact form states
body = sub_once(r'<sc-if value="\{\{submitted\}\}"[^>]*>\s*<div style="', '<div id="pf-done" hidden style="', body)
body = sub_once(r'(Send another request</button>\s*</div>)\s*</sc-if>', 'Send another request</button>\n</div>', body)
body = body.replace('<button type="button" onClick="{{reset}}"', '<button type="button" id="pf-reset"')
body = sub_once(r'<sc-if value="\{\{notSubmitted\}\}"[^>]*>\s*<form onSubmit="\{\{submit\}\}"', '<form id="pf-form"', body)
body = sub_once(r'</form>\s*</sc-if>', '</form>', body)
# Hidden fields for FormSubmit (email subject, layout, spam honeypot) and an error line
form_tag = re.search(r'<form id="pf-form"[^>]*>', body).group(0)
body = body.replace(form_tag,
                    form_tag.replace('<form id="pf-form"', '<form id="pf-form" action="https://formsubmit.co/' + FORM_EMAIL + '" method="POST"')
                    + '\n<input type="hidden" name="_subject" value="New website enquiry - PenFusion Solutions">'
                    '\n<input type="hidden" name="_template" value="table">'
                    '\n<input type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true" style="display: none">', 1)
body = body.replace('No spam, ever.', 'No spam, ever.<span id="pf-error" role="alert" style="display: block; color: #B91C1C"></span>', 1)

leftover = re.findall(r"\{\{|<sc-|onClick=|onSubmit=", body)
if leftover:
    raise SystemExit(f"unconverted template syntax left: {leftover}")

script = f"""
<script>
(function () {{
  var industries = {industries_js};

  function el(tag, attrs, text) {{
    var e = document.createElement(tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  }}
  var check = '{check_svg}';

  // Industry tabs
  var tabBase = '{tab_base}';
  var tabOn = '{tab_on}';
  var tabOff = '{tab_off}';
  var tabs = document.getElementById('pf-tabs');
  function showIndustry(i) {{
    var d = industries[i];
    document.getElementById('pf-kicker').textContent = d.kicker;
    document.getElementById('pf-ind-name').textContent = d.name;
    document.getElementById('pf-summary').textContent = d.summary;
    var ul = document.getElementById('pf-apps');
    ul.innerHTML = '';
    d.apps.forEach(function (a) {{
      var li = el('li', {{ style: 'display: flex; gap: 12px; align-items: flex-start; padding: 14px 16px; border-radius: 12px; background: #F6F8FC; border: 1px solid #E2E8F2; color: #1E293B; font-size: 15px' }});
      li.innerHTML = check;
      li.appendChild(el('span', {{}}, a));
      ul.appendChild(li);
    }});
    Array.prototype.forEach.call(tabs.children, function (b, j) {{
      b.setAttribute('aria-selected', j === i ? 'true' : 'false');
      b.setAttribute('style', tabBase + (j === i ? tabOn : tabOff));
    }});
  }}
  industries.forEach(function (d, i) {{
    var b = el('button', {{ type: 'button', role: 'tab' }}, d.name);
    b.addEventListener('click', function () {{ showIndustry(i); }});
    tabs.appendChild(b);
  }});
  showIndustry(0);

  // Contact form: send to FORM_EMAIL through FormSubmit's AJAX endpoint
  var form = document.getElementById('pf-form');
  var done = document.getElementById('pf-done');
  var err = document.getElementById('pf-error');
  var btn = form.querySelector('button[type=submit]');
  var btnText = btn.textContent;
  form.addEventListener('submit', function (e) {{
    e.preventDefault();
    err.textContent = '';
    btn.disabled = true;
    btn.textContent = 'Sending...';
    fetch(form.action.replace('formsubmit.co/', 'formsubmit.co/ajax/'), {{
      method: 'POST',
      headers: {{ 'Accept': 'application/json' }},
      body: new FormData(form)
    }}).then(function (r) {{ return r.json().then(function (d) {{ return {{ ok: r.ok, d: d }}; }}); }})
      .then(function (res) {{
        if (!res.ok || String(res.d.success) !== 'true') throw new Error(res.d.message || 'send failed');
        form.hidden = true; done.hidden = false;
      }})
      .catch(function () {{
        err.textContent = 'Sorry, your message could not be sent. Please email info@penfusionsolutions.com directly.';
      }})
      .then(function () {{ btn.disabled = false; btn.textContent = btnText; }});
  }});
  document.getElementById('pf-reset').addEventListener('click', function () {{ form.reset(); done.hidden = true; form.hidden = false; }});
}})();
</script>
"""

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{title}</title>
{helmet}
<style>[hidden]{{display:none !important}}html{{scroll-behavior:smooth}}section[id]{{scroll-margin-top:80px}}</style>
</head>
<body>
{body}
{script}
</body>
</html>
"""

open(out_path, "w", encoding="utf-8", newline="\n").write(page)
print(f"wrote {out_path} ({len(page)} bytes)")
