interface RecordValue { item: { count: number } }
export declare function mapTuple<T extends readonly unknown[]>(t: { [K in keyof T]: T[K] }): T
export const pair = mapTuple([1, "two"] as const)
export function read<T extends RecordValue>(v: T) { return v.item.count }
export function wrap<T extends RecordValue>(v: T) { return { value: read(v), source: v } }

interface Left { kind: "left"; value: number }
interface Right { kind: "right"; value: string }
export type Impossible = Left & Right
export function narrow(v: Left | Right) {
    if (v.kind === "left") return v.value.toFixed()
    return v.value.toUpperCase()
}
interface Branch<T> { entry: T; next?: Branch<T> }
export function descend<T>(b: Branch<T>) { return b.next?.entry }
