import re
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
tsx = (ROOT_DIR / "frontend" / "src" / "app" / "page.tsx").read_text(encoding="utf-8")

buttons = re.findall(r"<button[^>]*>", tsx, re.DOTALL)
no_handler = [b.replace("\n", " ")[:140] for b in buttons if "onClick" not in b and 'type="submit"' not in b and "type='submit'" not in b]
hrefs = re.findall(r"href=\{?[^>\n]+", tsx)
suspicious = re.findall(r"(?:TODO|FIXME|console\.log\(|alert\(|placeholder_fake)", tsx, re.I)

out = {
    "total_buttons": len(buttons),
    "buttons_without_handler_or_submit": len(no_handler),
    "buttons_without_handler_samples": no_handler,
    "all_hrefs": hrefs,
    "suspicious_tokens": suspicious,
}
print(json.dumps(out, indent=2, ensure_ascii=False))
