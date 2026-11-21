declare function mapRows<T, U>(rows: T[], fn: (row: T) => U): U[];
declare function listen(fn: (value: string) => void): void;
const projected = mapRows([1, 2], value => ({ text: value.toFixed() }));
const inferred = () => ({ label: projected[0].text });
const invalid = () => ({ label: projected[0].unknownProperty });
listen(value => ({ label: value.toUpperCase() }));
const wrong: number = inferred().label;
