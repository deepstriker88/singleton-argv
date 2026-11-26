'use strict';

import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const assert = require('node:assert/strict');
const { test } = require('node:test');
const { parseArgs } = require('node:util');
const { parseSingletons } = require('singleton-argv');

const options = { target: { type: 'string', short: 't' } };

for (const args of [
  ['--target', 'east'],
  ['--target=east', '--', '--target=west'],
]) {
  test(`preserves the built-in result for ${JSON.stringify(args)}`, () => {
    assert.deepEqual(
      parseSingletons({ args, options }),
      parseArgs({ args, options, allowPositionals: true }),
    );
  });
}

for (const [args, duplicateIndex] of [
  [['--target=east', '--target=west'], 1],
  [['-t', 'east', '--target=west'], 2],
]) {
  test(`rejects silent override for ${JSON.stringify(args)}`, () => {
    assert.equal(parseArgs({ args, options }).values.target, 'west');
    assert.throws(() => parseSingletons({ args, options }), {
      code: 'ERR_DUPLICATE_OPTION',
      option: 'target',
      firstIndex: 0,
      duplicateIndex,
      message: `Option --target appears twice (args[0] and args[${duplicateIndex}])`,
    });
  });
}

test('preserves explicitly repeatable string flags', () => {
  const { values } = parseSingletons({
    args: ['--label', 'small', '--label=green'],
    options: { label: { type: 'string', multiple: true } },
  });
  assert.deepEqual(values.label, ['small', 'green']);
});

test('rejects grouped repeated boolean aliases at the same index', () => {
  assert.throws(() => parseSingletons({
    args: ['-vv'],
    options: { verbose: { type: 'boolean', short: 'v' } },
  }), { code: 'ERR_DUPLICATE_OPTION', option: 'verbose', firstIndex: 0, duplicateIndex: 0 });
});

test('keeps defaults without counting them as occurrences', () => {
  const config = { target: { ...options.target, default: 'central' } };
  assert.equal(parseSingletons({ args: [], options: config }).values.target, 'central');
  assert.equal(parseSingletons({ args: ['-teast'], options: config }).values.target, 'east');
});

test('preserves unknown option and missing value errors', () => {
  assert.throws(() => parseSingletons({ args: ['--typo'], options }), {
    code: 'ERR_PARSE_ARGS_UNKNOWN_OPTION',
  });
  assert.throws(() => parseSingletons({ args: ['--target'], options }), {
    code: 'ERR_PARSE_ARGS_INVALID_OPTION_VALUE',
  });
});

test('requires an explicit token array', () => {
  assert.throws(() => parseSingletons({ options }), TypeError);
});

test('ESM and CommonJS export the same implementation', async () => {
  const esm = await import('singleton-argv');
  assert.equal(esm.parseSingletons, parseSingletons);
});

test('duplicate diagnostics omit the option values', () => {
  assert.throws(() => parseSingletons({ args: ['--target=SECRET_SENTINEL_ONE', '--target=SECRET_SENTINEL_TWO'], options }), e => e.code === 'ERR_DUPLICATE_OPTION' && !e.message.includes('SECRET_SENTINEL'));
});
