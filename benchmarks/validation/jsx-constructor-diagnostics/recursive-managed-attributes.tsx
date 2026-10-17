type Loop<C> = C extends new (props: any) => any ? Loop<C> : never;
declare namespace JSX {
  interface Element {}
  interface IntrinsicElements { item: {} }
  type LibraryManagedAttributes<C, P> = Loop<C>;
}
const first = <item />;
const second = <item />;
