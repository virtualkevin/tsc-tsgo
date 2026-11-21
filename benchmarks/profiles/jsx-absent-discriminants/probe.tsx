declare namespace JSX {
    interface Element {}
    interface IntrinsicElements {
        box: { kind?: "a"; value: string } | { kind: "b"; value: number }
    }
}
const rows = [
    <box value="one" />,
    <box value="two" />,
    <box value="three" />,
    <box kind="b" value={4} />,
];
