import { Link, Route, Routes } from 'react-router-dom';

function FoundationPage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-16 text-slate-100">
      <section className="mx-auto max-w-3xl rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-xl">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-amber-400">Inventory platform</p>
        <h1 className="mt-3 text-4xl font-bold">Car Dealership Inventory</h1>
        <p className="mt-4 max-w-xl leading-7 text-slate-300">
          The frontend foundation is ready. Authentication and inventory workflows will be built against the reviewed API contract.
        </p>
        <Link className="mt-6 inline-block rounded-lg bg-amber-400 px-4 py-2 font-semibold text-slate-950 focus:outline-none focus:ring-2 focus:ring-amber-200" to="/">
          Home
        </Link>
      </section>
    </main>
  );
}

export default function App() {
  return <Routes><Route path="*" element={<FoundationPage />} /></Routes>;
}
