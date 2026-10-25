import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import App from '../App';

const userSession = { id: 'u1', email: 'buyer@example.com', role: 'user', created_at: '2026-10-25T00:00:00Z' };
const vehicle = { id: 'v1', make: 'Volvo', model: 'XC60', category: 'SUV', price: 42000, quantity: 2, created_at: '2026-10-25T00:00:00Z', updated_at: '2026-10-25T00:00:00Z' };
const page = { items: [vehicle], offset: 0, limit: 20, total: 1 };

function renderInventory(role = 'user') {
  localStorage.setItem('car-inventory-token', 'test-token');
  localStorage.setItem('car-inventory-user', JSON.stringify({ ...userSession, role }));
  return render(<MemoryRouter initialEntries={['/inventory']}><App /></MemoryRouter>);
}

describe('inventory dashboard', () => {
  beforeEach(() => { localStorage.clear(); vi.stubGlobal('fetch', vi.fn()); });

  it('loads and renders vehicles and purchases one unit', async () => {
    const user = userEvent.setup();
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => page } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ ...vehicle, quantity: 1 }) } as Response);
    renderInventory();
    expect(await screen.findByRole('heading', { name: /volvo xc60/i })).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /purchase/i }));
    expect(screen.getByText('2 available')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /pay ₹42,000.00 and confirm/i }));
    expect(await screen.findByText(/purchase complete/i)).toBeInTheDocument();
    expect(screen.getByText('1 available')).toBeInTheDocument();
  });

  it('shows a payment confirmation and leaves stock unchanged when cancelled', async () => {
    const user = userEvent.setup();
    vi.mocked(fetch).mockResolvedValueOnce({ ok: true, status: 200, json: async () => page } as Response);
    renderInventory();
    await screen.findByRole('heading', { name: /volvo xc60/i });
    await user.click(screen.getByRole('button', { name: /purchase/i }));
    expect(screen.getByRole('dialog', { name: /confirm your purchase/i })).toBeInTheDocument();
    expect(within(screen.getByRole('dialog')).getByText('₹42,000.00')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /cancel/i }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(screen.getByText('2 available')).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it('formats prices as Indian rupees with Indian digit grouping', async () => {
    vi.mocked(fetch).mockResolvedValue({ ok: true, status: 200, json: async () => ({ ...page, items: [{ ...vehicle, price: 1234567 }] }) } as Response);
    renderInventory();
    expect(await screen.findByText('₹12,34,567.00')).toBeInTheDocument();
  });

  it('shows admin vehicle controls only to administrators', async () => {
    vi.mocked(fetch).mockResolvedValue({ ok: true, status: 200, json: async () => page } as Response);
    const { unmount } = renderInventory();
    await screen.findByRole('heading', { name: /volvo xc60/i });
    expect(screen.queryByRole('heading', { name: /manage vehicles/i })).not.toBeInTheDocument();
    unmount();
    localStorage.clear();
    vi.mocked(fetch).mockResolvedValue({ ok: true, status: 200, json: async () => page } as Response);
    renderInventory('admin');
    expect(await screen.findByRole('heading', { name: /manage vehicles/i })).toBeInTheDocument();
  });

  it('disables purchase for unavailable stock and sends search filters to the API', async () => {
    const unavailable = { ...vehicle, quantity: 0 };
    vi.mocked(fetch).mockResolvedValue({ ok: true, status: 200, json: async () => ({ ...page, items: [unavailable] }) } as Response);
    renderInventory();
    expect(await screen.findByRole('heading', { name: /volvo xc60/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /out of stock/i })).toBeDisabled();
    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/make/i), 'Volvo');
    await user.click(screen.getByRole('button', { name: /search/i }));
    expect(fetch).toHaveBeenLastCalledWith(expect.stringMatching(/\/api\/vehicles\/search\?make=Volvo/), expect.objectContaining({ headers: expect.any(Headers) }));
  });

  it('lets an administrator create a vehicle through the protected API', async () => {
    const user = userEvent.setup();
    const created = { ...vehicle, id: 'v2', make: 'Honda', model: 'Civic', quantity: 4 };
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ ...page, items: [] }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 201, json: async () => created } as Response);
    renderInventory('admin');
    const adminPanel = screen.getByRole('heading', { name: /manage vehicles/i }).closest('section')!;
    const admin = within(adminPanel);
    await user.type(admin.getByLabelText(/^make$/i), 'Honda');
    await user.type(admin.getByLabelText(/^model$/i), 'Civic');
    await user.type(admin.getByLabelText(/^category$/i), 'Sedan');
    await user.clear(admin.getByLabelText(/^price$/i));
    await user.type(admin.getByLabelText(/^price$/i), '25000');
    await user.clear(admin.getByLabelText(/^quantity$/i));
    await user.type(admin.getByLabelText(/^quantity$/i), '4');
    await user.click(screen.getByRole('button', { name: /add vehicle/i }));
    expect(await screen.findByRole('heading', { name: /honda civic/i })).toBeInTheDocument();
    expect(fetch).toHaveBeenLastCalledWith(expect.stringMatching(/\/api\/vehicles$/), expect.objectContaining({ method: 'POST', headers: expect.any(Headers), body: JSON.stringify({ make: 'Honda', model: 'Civic', category: 'Sedan', price: 25000, quantity: 4 }) }));
  });

  it('shows an API error when a purchase fails without changing displayed stock', async () => {
    const user = userEvent.setup();
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => page } as Response)
      .mockResolvedValueOnce({ ok: false, status: 409, json: async () => ({ error: { code: 'out_of_stock', message: 'Vehicle is currently out of stock.' } }) } as Response);
    renderInventory();
    await screen.findByRole('heading', { name: /volvo xc60/i });
    await user.click(screen.getByRole('button', { name: /purchase/i }));
    await user.click(screen.getByRole('button', { name: /pay ₹42,000.00 and confirm/i }));
    expect(await within(screen.getByRole('dialog')).findByRole('alert')).toHaveTextContent(/out of stock/i);
    expect(screen.getByText('2 available')).toBeInTheDocument();
  });

  it('supports administrator update, restock, and confirmed deletion', async () => {
    const user = userEvent.setup();
    vi.spyOn(window, 'prompt').mockReturnValue('3');
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    const changed = { ...vehicle, model: 'XC60 Recharge' };
    vi.mocked(fetch)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => page } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => changed } as Response)
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ ...changed, quantity: 5 }) } as Response)
      .mockResolvedValueOnce({ ok: true, status: 204, json: async () => null } as Response);
    renderInventory('admin');
    await screen.findByRole('heading', { name: /volvo xc60/i });
    await user.click(screen.getByRole('button', { name: /edit/i }));
    const admin = within(screen.getByRole('heading', { name: /manage vehicles/i }).closest('section')!);
    await user.clear(admin.getByLabelText(/^model$/i));
    await user.type(admin.getByLabelText(/^model$/i), 'XC60 Recharge');
    await user.click(screen.getByRole('button', { name: /save changes/i }));
    expect(await screen.findByRole('heading', { name: /volvo xc60 recharge/i })).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /restock/i }));
    expect(await screen.findByText('5 available')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /delete/i }));
    expect(await screen.findByRole('heading', { name: /no vehicles found/i })).toBeInTheDocument();
    expect(window.confirm).toHaveBeenCalledWith('Delete Volvo XC60 Recharge?');
  });
});
