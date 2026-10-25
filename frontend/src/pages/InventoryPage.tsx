import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { ApiError } from '../services/api';
import { createVehicle, deleteVehicle, listVehicles, purchaseVehicle, restockVehicle, updateVehicle } from '../services/vehicles';
import type { Vehicle, VehicleInput } from '../types/api';

const blank: VehicleInput = { make: '', model: '', category: '', price: 0, quantity: 0 };
const rupeeFormatter = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', minimumFractionDigits: 2, maximumFractionDigits: 2 });

export default function InventoryPage() {
  const { session, signOut } = useAuth();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [query, setQuery] = useState({ make: '', model: '', category: '', min_price: '', max_price: '' });
  const [filters, setFilters] = useState({});
  const [form, setForm] = useState<VehicleInput>(blank);
  const [editing, setEditing] = useState('');
  const [busy, setBusy] = useState('');
  const [purchaseCandidate, setPurchaseCandidate] = useState<Vehicle | null>(null);
  const isAdmin = session?.user.role === 'admin';
  const refresh = useCallback(async () => {
    setLoading(true); setError('');
    try { setVehicles((await listVehicles(filters)).items); }
    catch (e) { setError(e instanceof ApiError ? e.message : 'Could not load inventory.'); }
    finally { setLoading(false); }
  }, [filters]);
  useEffect(() => { void refresh(); }, [refresh]);

  async function buy(vehicle: Vehicle) {
    setBusy(vehicle.id); setError('');
    try { const updated = await purchaseVehicle(vehicle.id); setVehicles((items) => items.map((v) => v.id === updated.id ? updated : v)); setNotice('Payment approved. Purchase complete. Inventory has been updated.'); setPurchaseCandidate(null); }
    catch (e) { setError(e instanceof ApiError ? e.message : 'Purchase could not be completed.'); }
    finally { setBusy(''); }
  }

  async function save(event: React.FormEvent) {
    event.preventDefault(); setError('');
    try {
      const updated = editing ? await updateVehicle(editing, form) : await createVehicle(form);
      setVehicles((items) => editing ? items.map((v) => v.id === updated.id ? updated : v) : [...items, updated]);
      setForm(blank); setEditing(''); setNotice(editing ? 'Vehicle updated.' : 'Vehicle added.');
    } catch (e) { setError(e instanceof ApiError ? e.message : 'Vehicle could not be saved.'); }
  }

  async function restock(vehicle: Vehicle) {
    const input = window.prompt(`How many ${vehicle.make} ${vehicle.model} units should be added?`);
    if (input === null) return;
    const quantity = Number(input);
    if (!Number.isInteger(quantity) || quantity < 1) { setError('Restock quantity must be a positive whole number.'); return; }
    try { const updated = await restockVehicle(vehicle.id, quantity); setVehicles((items) => items.map((v) => v.id === updated.id ? updated : v)); setNotice('Inventory restocked.'); }
    catch (e) { setError(e instanceof ApiError ? e.message : 'Restock failed.'); }
  }
  return (
    <main className="inventory-shell">
      <header className="topbar">
        <Link className="brand-lockup dark-brand" to="/inventory">
          <span className="brand-mark" aria-hidden="true">IM</span>
          <span>Incubyte <span className="brand-light">Motors</span></span>
        </Link>
        <div className="account-actions">
          <span className="account-email">{session?.user.email}</span>
          <button className="button button-quiet" onClick={signOut}>Sign out</button>
        </div>
      </header>
      <section className="inventory-welcome">
        <p className="eyebrow">The collection</p>
        <h1>Your next drive<br /><span>is waiting.</span></h1>
        <p>Explore the Incubyte collection.</p>
      </section>
      <section className="inventory-content">
        <div className="inventory-heading"><h2>Available inventory</h2><span>{vehicles.length} vehicles</span></div>
        <form className="filter-bar" onSubmit={(e) => { e.preventDefault(); setFilters(Object.fromEntries(Object.entries(query).filter(([, v]) => v))); }}>
          {(['make', 'model', 'category', 'min_price', 'max_price'] as const).map((key) => <label key={key}>{key.replace('_', ' ')}<input type={key.includes('price') ? 'number' : 'search'} min={key.includes('price') ? 0 : undefined} step={key.includes('price') ? '0.01' : undefined} value={query[key]} onChange={(e) => setQuery({ ...query, [key]: e.target.value })} /></label>)}
          <button className="button button-primary">Search</button><button type="button" className="button button-quiet" onClick={() => { setQuery({ make: '', model: '', category: '', min_price: '', max_price: '' }); setFilters({}); }}>Clear</button>
        </form>
        {notice && <p className="notice-success" role="status">{notice}</p>}{error && <p role="alert" className="form-error">{error} <button className="button button-quiet" onClick={() => void refresh()}>Retry</button></p>}
        {loading ? <p role="status">Loading inventory…</p> : vehicles.length === 0 ? <div className="inventory-state"><h3>No vehicles found</h3><p>Change your search or clear the filters.</p></div> : <div className="vehicle-grid">{vehicles.map((vehicle) => <article className="vehicle-card" key={vehicle.id}>
          <div className="vehicle-visual"><span>{vehicle.category}</span><span className="vehicle-monogram">{vehicle.make[0]}{vehicle.model[0]}</span></div><div className="vehicle-details"><p>{vehicle.category}</p><h3>{vehicle.make} {vehicle.model}</h3><p className="vehicle-price">{rupeeFormatter.format(Number(vehicle.price))}</p><p>{vehicle.quantity} available</p>
          <button className="button button-primary purchase-button" disabled={!vehicle.quantity || busy === vehicle.id} onClick={() => { setNotice(''); setError(''); setPurchaseCandidate(vehicle); }}>{busy === vehicle.id ? 'Processing…' : vehicle.quantity ? 'Purchase' : 'Out of stock'}</button>
          {isAdmin && <div className="admin-actions"><button className="button button-quiet" onClick={() => { setEditing(vehicle.id); setForm({ make: vehicle.make, model: vehicle.model, category: vehicle.category, price: vehicle.price, quantity: vehicle.quantity }); }}>Edit</button><button className="button button-quiet" onClick={() => void restock(vehicle)}>Restock</button><button className="button button-quiet" onClick={async () => { if (window.confirm(`Delete ${vehicle.make} ${vehicle.model}?`)) { try { await deleteVehicle(vehicle.id); setVehicles((items) => items.filter((v) => v.id !== vehicle.id)); } catch (e) { setError(e instanceof ApiError ? e.message : 'Delete failed.'); } } }}>Delete</button></div>}
          </div></article>)}</div>}
        {isAdmin && <section className="admin-panel"><p className="eyebrow">Administration</p><h2>Manage vehicles</h2><form className="vehicle-form" onSubmit={(e) => void save(e)}>{(['make', 'model', 'category', 'price', 'quantity'] as const).map((key) => <label key={key}>{key}<input required type={key === 'price' || key === 'quantity' ? 'number' : 'text'} min={key === 'price' || key === 'quantity' ? 0 : undefined} step={key === 'price' ? '0.01' : key === 'quantity' ? '1' : undefined} value={form[key]} onChange={(e) => setForm({ ...form, [key]: key === 'price' || key === 'quantity' ? Number(e.target.value) : e.target.value })} /></label>)}<button className="button button-primary">{editing ? 'Save changes' : 'Add vehicle'}</button>{editing && <button type="button" className="button button-quiet" onClick={() => { setEditing(''); setForm(blank); }}>Cancel</button>}</form></section>}
      </section>
      {purchaseCandidate && <div className="payment-backdrop"><section className="payment-dialog" role="dialog" aria-modal="true" aria-labelledby="payment-title">
        <p className="eyebrow">Secure checkout preview</p><h2 id="payment-title">Confirm your purchase</h2>
        <p className="payment-vehicle">{purchaseCandidate.make} {purchaseCandidate.model}</p>
        <dl className="payment-summary"><div><dt>Quantity</dt><dd>1 vehicle</dd></div><div><dt>Total</dt><dd>{rupeeFormatter.format(Number(purchaseCandidate.price))}</dd></div></dl>
        <p className="payment-disclaimer">Demo payment only. No payment details are collected or charged.</p>
        {error && <p className="form-error" role="alert">{error}</p>}
        <div className="payment-actions"><button className="button button-quiet" type="button" disabled={busy === purchaseCandidate.id} onClick={() => setPurchaseCandidate(null)}>Cancel</button><button className="button button-primary" type="button" disabled={busy === purchaseCandidate.id} onClick={() => void buy(purchaseCandidate)}>{busy === purchaseCandidate.id ? 'Processing…' : `Pay ${rupeeFormatter.format(Number(purchaseCandidate.price))} and confirm`}</button></div>
      </section></div>}
    </main>
  );
}
