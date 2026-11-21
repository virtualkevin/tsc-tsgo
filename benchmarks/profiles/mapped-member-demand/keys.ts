enum Left { Same = "same" }
enum Right { Same = "same" }
type Collisions = { [K in Left | Right]: K };
type Renamed<T> = { [K in keyof T as K extends string ? `renamed_${K}` : never]: T[K] };
type Merge<T> = { [K in keyof T as "result"]: K };
interface Origin { readonly first?: number; second: string }
declare const collisions: Collisions;
declare const renamed: Renamed<Origin>;
declare const merged: Merge<Origin>;
export const same = collisions.same;
export const optional = renamed.renamed_first;
export const both = merged.result;
export const copy = { ...renamed };
export function use(v: { [K in "a" | "b"]: K }) { return [v.a, v.b] as const }
