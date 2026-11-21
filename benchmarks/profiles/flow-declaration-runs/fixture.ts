export function narrow(input: { kind: "a"; value: string } | { kind: "b"; value: number }) {
    let current = input;
    if (current.kind === "a") {
        const first = current.value;
        const second = first.length;
        const third = second + 1;
        {
            const current = { value: third };
            const shadow = current.value;
            if (shadow < 1) return shadow;
        }
        const after = current.value;
        return after.toUpperCase();
    }
    current = { kind: "a", value: String(current.value) };
    const next = current.kind;
    const last = current.value;
    return next + last;
}

export function keys(maybe: Record<string, number> | undefined) {
    let result = 0;
    for (const key in maybe) {
        const a = 1;
        const b = 2;
        result += maybe[key] + a + b;
    }
    return result;
}

export function branch(value: { prop?: number }, flag: boolean) {
    if (flag) value.prop = 1;
    else value.prop = 2;
    const a = value.prop;
    const b = a + 1;
    const c = b + 2;
    return [value["prop"], value.prop, c];
}

export const first = { nested: { count: 2 } };
export const second = first.nested.count;
export const third = second + 1;
export const fourth = first.nested.count;
