import glob
from pathlib import Path

nav_html = """<!-- Pragmatic Sysadmin Global Navigation -->
<nav style="background:#0f172a; border-bottom:1px solid #334155; padding:0.6rem 1.25rem; display:flex; justify-content:space-between; align-items:center; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; font-size:0.875rem; color:#cbd5e1; z-index:99999; position:relative;">
  <div style="display:flex; align-items:center; gap:0.75rem;">
    <a href="https://pragmaticsysadmin.help/" style="color:#f8fafc; font-weight:700; text-decoration:none; display:flex; align-items:center; gap:0.4rem;">
      <span>🐧</span> Pragmatic Sysadmin
    </a>
    <span style="color:#475569;">|</span>
    <span style="color:#94a3b8;">Free Web Tools</span>
  </div>
  <div style="display:flex; gap:1.25rem; align-items:center;">
    <a href="https://pragmaticsysadmin.help/tools/" style="color:#93c5fd; text-decoration:none;">All Tools</a>
    <a href="https://pragmaticsysadmin.help/sysadmin/" style="color:#cbd5e1; text-decoration:none;">Guides</a>
    <a href="https://pragmaticsysadmin.help/" style="background:#2563eb; color:#fff; padding:0.25rem 0.65rem; border-radius:4px; text-decoration:none; font-weight:500; font-size:0.8rem;">Home →</a>
  </div>
</nav>
"""

repo_root = Path(__file__).resolve().parent.parent
tools = list((repo_root / "static" / "tools").glob("*.html"))

for tool in tools:
    content = tool.read_text(encoding="utf-8")
    if "Pragmatic Sysadmin Global Navigation" not in content and "<body" in content:
        idx = content.find("<body")
        end_body_tag = content.find(">", idx)
        if end_body_tag != -1:
            new_content = content[:end_body_tag+1] + "\n" + nav_html + content[end_body_tag+1:]
            tool.write_text(new_content, encoding="utf-8")
            print(f"Injected nav into {tool.name}")
        else:
            print(f"Skipped {tool.name} (no end of body tag)")
    else:
        print(f"Already injected or no body in {tool.name}")
