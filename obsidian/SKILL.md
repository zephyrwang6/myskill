# Obsidian

Obsidian vault = a normal folder on disk.

Vault structure (typical)

- Attachments: whatever folder you chose in Obsidian settings (images/PDFs/etc.)
- Canvases:`*.canvas`(JSON)
- Config:`.obsidian/`(workspace + plugin settings; usually don't touch from scripts)
- Notes:`*.md`(plain text Markdown; edit with any editor)

## Find the active vault(s)

Obsidian desktop tracks vaults here (source of truth):

- `~/Library/Application Support/obsidian/obsidian.json`

`obsidian-cli` resolves vaults from that file; vault name is typically the folder name (path suffix).

Fast "what vault is active / where are the notes?"

- Otherwise, read`~/Library/Application Support/obsidian/obsidian.json` and use the vault entry with`"open": true`.
- If you've already set a default:`obsidian-cli print-default --path-only`

Notes

- Avoid writing hardcoded vault paths into scripts; prefer reading the config or using`print-default`.
- Multiple vaults common (iCloud vs`~/Documents`, work/personal, etc.). Don't guess; read config.

## obsidian-cli quick start

Pick a default vault (once):

- `obsidian-cli print-default`/`obsidian-cli print-default --path-only`
- `obsidian-cli set-default "<vault-name>"`

Search

- `obsidian-cli search-content "query"`(inside notes; shows snippets + lines)
- `obsidian-cli search "query"`(note names)

Create

- Avoid creating notes under "hidden" dot-folders (e.g.`.something/...`) via URI; Obsidian may refuse.
- Requires Obsidian URI handler (`obsidian://…`) working (Obsidian installed).
- `obsidian-cli create "Folder/New note" --content "..." --open`

Move/rename (safe refactor)

- Updates`[[wikilinks]]` and common Markdown links across the vault (this is the main win vs`mv`).
- `obsidian-cli move "old/path/note" "new/path/note"`

Delete

- `obsidian-cli delete "path/note"`

Prefer direct edits when appropriate: open the`.md` file and change it; Obsidian will pick it up.
