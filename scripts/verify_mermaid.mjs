#!/usr/bin/env node
/**
 * Parse every Mermaid diagram in pattern articles; exit 1 on syntax errors.
 */
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import mermaid from "mermaid";

const ROOT = join(import.meta.dirname, "..");
const SKIP_DIRS = new Set([".git", "scripts", "docs", "node_modules", "assets/vendor"]);

function walkHtml(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    const st = statSync(p);
    if (st.isDirectory()) {
      if (SKIP_DIRS.has(name)) continue;
      walkHtml(p, out);
    } else if (name.endsWith(".html") && name !== "404.html") {
      if (name === "index.html" && dir !== ROOT) {
        // category indexes may lack diagrams
      }
      out.push(p);
    }
  }
  return out;
}

const MERMAID_RE =
  /<div class="[^"]*mermaid[^"]*"[^>]*>([\s\S]*?)<\/div>|<pre class="mermaid"[^>]*>([\s\S]*?)<\/pre>/gi;

mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });

let files = 0;
let diagrams = 0;
const errors = [];

for (const file of walkHtml(ROOT)) {
  const rel = relative(ROOT, file);
  const html = readFileSync(file, "utf8");
  if (!html.includes('class="mermaid"') && !html.includes("class='mermaid'")) {
    if (html.includes('id="typical-architecture"') && !html.includes('class="mermaid"')) {
      errors.push({ file: rel, message: "missing Mermaid diagram under typical-architecture" });
    }
    continue;
  }
  files++;
  let m;
  MERMAID_RE.lastIndex = 0;
  let idx = 0;
  while ((m = MERMAID_RE.exec(html))) {
    const src = (m[1] || m[2] || "").trim();
    if (!src) continue;
    diagrams++;
    idx++;
    try {
      await mermaid.parse(src);
    } catch (e) {
      errors.push({
        file: rel,
        message: `diagram #${idx}: ${e.message || e}`,
      });
    }
  }
}

console.log(`Checked ${files} files, ${diagrams} Mermaid blocks.`);
if (errors.length) {
  console.error(`Failures: ${errors.length}`);
  for (const err of errors.slice(0, 50)) {
    console.error(`  ${err.file}: ${err.message}`);
  }
  if (errors.length > 50) console.error(`  ... and ${errors.length - 50} more`);
  process.exit(1);
}
console.log("All Mermaid diagrams parsed OK.");