# Workflow review

Checked 2026-11-25. A script receives a token array assembled by two wrappers. Both wrappers can supply the same target option, including through its short alias. The script needs one target or a diagnostic before invoking a handler.

[Node.js parsing reference](https://nodejs.org/download/release/latest-jod/docs/api/util.html) documents last-value behavior and exposes tokens for custom checks. [Commander parsing reference](https://github.com/tj/commander.js/blob/master/docs/options-in-depth.md) documents grouping and option arguments. Both are free developer tools. No relevant commercial plan was verified for this in-process policy.

Keep Node's input and result shapes for common cases. Provide the duplicate check as part of the parse call. Put canonical option name and zero-based input indexes in a plain-text error. Keep values out of duplicate diagnostics.

Pass criterion fixed before implementation. On four shared inputs, reject both duplicate cases the stock built-in accepts and match both successful outputs. Verify intentional repeats separately. Use local tests and an installed archive to check the API. Browser and hosted checks are inapplicable to this library.

## Results

On Node 22.23.4, both duplicate fixtures produced the expected diagnostic,
and both valid fixtures matched the built-in output. All nine local tests
passed. A fresh offline archive install passed the README success case,
the duplicate case, and the repeatable case with an ESM import. The
[review](../../specs/npm-yargs-parser.md) records the comparison and pending
release checks.
