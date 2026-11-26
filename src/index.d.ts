export interface Option {type: 'string' | 'boolean'; short?: string; multiple?: boolean; default?: string | boolean | string[] | boolean[]}
export function parseSingletons(input: {args: string[]; options: Record<string, Option>}): {values: Record<string, string | boolean | string[] | boolean[] | undefined>; positionals: string[]};
