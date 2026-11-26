'use strict';

const { parseArgs } = require('node:util');

function parseSingletons({ args, options }) {
  if (!Array.isArray(args)) {
    throw new TypeError('args must be an array of command-line tokens');
  }

  const { values, positionals, tokens } = parseArgs({
    args,
    options,
    strict: true,
    allowPositionals: true,
    tokens: true,
  });

  const firstIndexes = new Map();
  for (const token of tokens) {
    if (token.kind !== 'option' || options[token.name].multiple === true) {
      continue;
    }

    if (firstIndexes.has(token.name)) {
      const firstIndex = firstIndexes.get(token.name);
      const error = new Error(
        `Option --${token.name} appears twice (args[${firstIndex}] and args[${token.index}])`,
      );
      error.code = 'ERR_DUPLICATE_OPTION';
      error.option = token.name;
      error.firstIndex = firstIndex;
      error.duplicateIndex = token.index;
      throw error;
    }

    firstIndexes.set(token.name, token.index);
  }

  return { values, positionals };
}

module.exports = { parseSingletons };
