"""Convert a Design canvas .dc.html artboard into a standalone static page.

Usage: python -I convert.py <Main.dc.html> <out/index.html>
"""
import re
import sys

src_path, out_path = sys.argv[1], sys.argv[2]
src = open(src_path, encoding="utf-8").read()

title = re.search(r"<title>(.*?)</title>", src, re.S).group(1)
helmet = re.search(r"<helmet>(.*?)</helmet>", src, re.S).group(1).strip()
body = re.search(r"</helmet>(.*?)</x-dc>", src, re.S).group(1).strip()
logic = re.search(r"renderVals\(\) \{(.*?)var self = this;", src, re.S).group(1)
jobs_js = re.search(r"var jobData = (\[.*?\]);", src, re.S).group(1)
cat_js = re.search(r"var catInfo = (\{.*?\n    \});", src, re.S).group(1)
industries_js = re.search(r"var data = (\[.*?\]);", logic, re.S).group(1)


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

# Job filters and job cards
body = sub_once(r'<sc-for list="\{\{jobFilters\}\}".*?</sc-for>', "", body)
body = body.replace('<div aria-label="Filter openings"', '<div id="pf-filters" role="group" aria-label="Filter openings"')
body = sub_once(r'<div style="display: grid; grid-template-columns: repeat\(auto-fill, minmax\(320px, 1fr\)\); gap: 20px">\s*<sc-for list="\{\{jobs\}\}".*?</sc-for>\s*</div>',
                '<div id="pf-jobs" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px"></div>', body)

# Contact form states
body = sub_once(r'<sc-if value="\{\{submitted\}\}"[^>]*>\s*<div style="', '<div id="pf-done" hidden style="', body)
body = sub_once(r'(Send another request</button>\s*</div>)\s*</sc-if>', 'Send another request</button>\n</div>', body)
body = body.replace('<button type="button" onClick="{{reset}}"', '<button type="button" id="pf-reset"')
body = sub_once(r'<sc-if value="\{\{notSubmitted\}\}"[^>]*>\s*<form onSubmit="\{\{submit\}\}"', '<form id="pf-form"', body)
body = sub_once(r'</form>\s*</sc-if>', '</form>', body)

leftover = re.findall(r"\{\{|<sc-|onClick=|onSubmit=", body)
if leftover:
    raise SystemExit(f"unconverted template syntax left: {leftover}")

script = f"""
<script>
(function () {{
  var industries = {industries_js};
  var jobData = {jobs_js};
  var catInfo = {cat_js};

  function el(tag, attrs, text) {{
    var e = document.createElement(tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  }}
  var check = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0F766E" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex: none; margin-top: 3px"><path d="M20 6 9 17l-5-5"/></svg>';
  var pin = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>';
  var arrow = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';

  // Industry tabs
  var tabBase = 'min-height: 44px; padding: 0 20px; border-radius: 999px; font-size: 15px; font-weight: 600; cursor: pointer; font-family: inherit; ';
  var tabOn = 'border: 1px solid #0F766E; background: #E6FAF6; color: #0B1530;';
  var tabOff = 'border: 1px solid #C6D1E3; background: #FFFFFF; color: #475569;';
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

  // Job filters and cards
  var badgeBase = 'display: inline-flex; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; letter-spacing: 0.02em; ';
  var fBase = 'min-height: 44px; padding: 0 18px; border-radius: 999px; font-size: 14px; font-weight: 600; cursor: pointer; font-family: inherit; ';
  var fOn = 'border: 1px solid #EA580C; background: #FFF4EC; color: #9A3412;';
  var fOff = 'border: 1px solid #C6D1E3; background: #FFFFFF; color: #475569;';
  var filters = [{{ id: 'all', label: 'All roles' }}, {{ id: 'it', label: 'IT' }}, {{ id: 'ai', label: 'AI' }}, {{ id: 'ba', label: 'Business Analysis' }}];
  var fWrap = document.getElementById('pf-filters');
  var jobsWrap = document.getElementById('pf-jobs');
  function showJobs(fid) {{
    jobsWrap.innerHTML = '';
    jobData.filter(function (j) {{ return fid === 'all' || j.cat === fid; }}).forEach(function (j) {{
      var c = catInfo[j.cat];
      var art = el('article', {{ 'class': 'pf-card', style: 'display: flex; flex-direction: column; gap: 14px; padding: 26px; border: 1px solid #DDE4EF; border-radius: 16px; background: #FFFFFF' }});
      var top = el('div', {{ style: 'display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px' }});
      top.appendChild(el('span', {{ style: badgeBase + c.badge }}, c.label));
      top.appendChild(el('span', {{ style: 'font-size: 13px; font-weight: 600; color: #5B6B82' }}, j.type));
      art.appendChild(top);
      art.appendChild(el('h4', {{ style: "margin: 0; font-family: 'Space Grotesk', sans-serif; font-size: 20px; line-height: 1.25; color: #0B1530" }}, j.title));
      var loc = el('div', {{ style: 'display: flex; align-items: center; gap: 6px; font-size: 14px; color: #5B6B82' }});
      loc.innerHTML = pin;
      loc.appendChild(el('span', {{}}, j.location));
      art.appendChild(loc);
      art.appendChild(el('p', {{ style: 'margin: 0; font-size: 15px; color: #475569' }}, j.summary));
      var sk = el('ul', {{ 'aria-label': 'Key skills', style: 'margin: 0; padding: 0; list-style: none; display: flex; flex-wrap: wrap; gap: 8px' }});
      j.skills.forEach(function (s) {{ sk.appendChild(el('li', {{ style: 'padding: 4px 10px; border-radius: 999px; background: #F1F4F9; border: 1px solid #E2E8F2; font-size: 13px; color: #334155' }}, s)); }});
      art.appendChild(sk);
      var foot = el('div', {{ style: 'margin-top: auto; padding-top: 6px' }});
      var a = el('a', {{ href: '#contact', style: 'display: inline-flex; align-items: center; gap: 8px; min-height: 44px; padding: 0 20px; border-radius: 10px; background: linear-gradient(90deg, #EA580C, #C2410C); color: #FFFFFF; font-weight: 600; font-size: 15px' }});
      a.innerHTML = 'Apply Now ' + arrow;
      foot.appendChild(a);
      art.appendChild(foot);
      jobsWrap.appendChild(art);
    }});
    Array.prototype.forEach.call(fWrap.children, function (b) {{
      var on = b.dataset.id === fid;
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.setAttribute('style', fBase + (on ? fOn : fOff));
    }});
  }}
  filters.forEach(function (f) {{
    var n = f.id === 'all' ? jobData.length : jobData.filter(function (j) {{ return j.cat === f.id; }}).length;
    var b = el('button', {{ type: 'button', 'data-id': f.id }}, f.label + ' (' + n + ')');
    b.addEventListener('click', function () {{ showJobs(f.id); }});
    fWrap.appendChild(b);
  }});
  showJobs('all');

  // Contact form (preview only: shows a confirmation, sends nothing yet)
  var form = document.getElementById('pf-form');
  var done = document.getElementById('pf-done');
  form.addEventListener('submit', function (e) {{ e.preventDefault(); form.hidden = true; done.hidden = false; }});
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
