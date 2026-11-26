# Singleton Argv

When two parts of a script supply the same command-line option, Singleton Argv
stops the command from silently picking one of the values. It tells your code
which option repeated and where both occurrences appeared.

## What it does

Pass in the argument array and describe the options your command accepts.
Single-value options can appear once, including through a short alias.
Options declared with `multiple: true` collect every occurrence.

## Quick start

From a copy of this package directory, install it into a fresh example project.

```sh
package_dir="$PWD"
example_dir="$(mktemp -d)"
npm pack --offline --pack-destination "$example_dir" "$package_dir"
cd "$example_dir"
npm init -y
npm install --offline ./singleton-argv-0.1.0.tgz
cat > example.cjs <<'JS'
const { parseSingletons } = require('singleton-argv');

const { values } = parseSingletons({
  args: process.argv.slice(2),
  options: { target: { type: 'string', short: 't' } },
});

console.log(values.target);
JS
node example.cjs --target east
```

Expected output:

```text
east
```

## Common examples

Run `node example.cjs -t east --target west` to see the error
`Option --target appears twice (args[0] and args[2])`.

To collect repeatable options, use this option declaration:

```js
const { parseSingletons } = require('singleton-argv');

const { values } = parseSingletons({
  args: ['--label', 'small', '--label=green'],
  options: { label: { type: 'string', multiple: true } },
});

console.log(JSON.stringify(values.label)); // ["small","green"]
```

## API

`parseSingletons({ args, options })` returns `{ values, positionals }`.
Supply an explicit token array and application-owned Node `util.parseArgs`
option definitions. Supported definitions use `type` (`'string'` or
`'boolean'`), optional `short`, `multiple`, and `default`. Give each
option its own name and short alias. The parser accepts positional arguments
and treats everything after `--` as positional.

Duplicates throw an error with `code` set to `ERR_DUPLICATE_OPTION`,
`option` set to the long name, and zero-based `firstIndex` and
`duplicateIndex`. Both indexes can be the same for grouped short flags
such as `-vv`. Node's strict parsing errors take precedence.

## Requirements

Node.js 22 or later. Use a current patched release. npm is needed for the
install example. The library uses Node built-ins and runs in the caller's
process.

## Security and limitations

Pass trusted option definitions. The library accepts tokens that your shell
or application has already split. Boolean negation, subcommands, config-file
merging, and automatic help are outside this API. Validate values for your
application before passing them to other systems. Duplicate messages omit
values. Other parser errors and successful results may contain input text.

## Troubleshooting

- If a duplicate surprises you, check the reported positions in the combined
  argument array and any aliases. Enable `multiple` only for options that
  your command handles as arrays.
- If a flag is unknown, declare it in `options`. Use `--` when the remaining
  tokens should be treated as positional arguments.
- If npm cannot find the package directory, rerun the quick start from the
  directory containing this README and `package.json`.

The package exposes the same implementation to CommonJS `require` and ESM `import`. No second parser is bundled.


## Installation and support

Install the included .tgz archive using `npm install --offline --ignore-scripts ./singleton-argv-0.1.0.tgz` from a fresh local project (Node.js 22+). Use the included archive and `npx --no-install` to avoid downloading a different version.

```sh
node --input-type=module -e "import {parseSingletons} from 'singleton-argv'; console.log(parseSingletons({args:['--target','east'],options:{target:{type:'string'}}}).values.target)"
```

Use synthetic or redacted inputs in bug reports. Optional support: https://buymeacoffee.com/eztoolgo (no entitlement or subscription).

## Download and run

Use the versioned download ZIP attached to the corresponding release. Extract the complete archive and open index.html for the local interface and setup steps. No account or subscription is required.
