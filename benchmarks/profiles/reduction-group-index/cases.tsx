declare global { namespace JSX {
    type Element = {};
    interface IntrinsicElements { box: { value: string } }
} }
type Shared = { kind: "button"; text?: string };
type Same = Shared & { kind: "button"; other: true };
type Conflict = Shared & { kind: "label" };
type Optional = { mode?: "a" } & { mode?: "b" };
declare const good: Same;
declare const neverValue: Conflict;
declare function component<T>(value: T): T;
declare function Button(props: Shared & { other?: boolean }): JSX.Element;
export const tag = component(good).kind;
export const noValue: never = neverValue;
export const optional: Optional = {};
export const element = <Button {...good} />;
export const bad = <Button kind="label" />;
class First { private tag = 1; }
class Second { private tag = 1; }
declare const disjoint: First & Second;
export const unreachable: never = disjoint;
