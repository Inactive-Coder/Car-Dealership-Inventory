import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import App from './App';

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

describe('authentication routes', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.stubGlobal('fetch', vi.fn());
  });

  it('shows an accessible login form at /login', () => {
    renderAt('/login');

    expect(screen.getByRole('heading', { name: /welcome back/i })).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: /email address/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toHaveAttribute('type', 'password');
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('lets the user show and hide the login password', async () => {
    const user = userEvent.setup();
    renderAt('/login');
    const password = screen.getByLabelText(/^password$/i);
    await user.click(screen.getByRole('button', { name: /show password/i }));
    expect(password).toHaveAttribute('type', 'text');
    await user.click(screen.getByRole('button', { name: /hide password/i }));
    expect(password).toHaveAttribute('type', 'password');
  });

  it('lets the user reveal and hide both registration password fields', async () => {
    const user = userEvent.setup();
    renderAt('/register');

    const password = screen.getByLabelText(/^password$/i);
    const confirmation = screen.getByLabelText(/confirm password/i);
    await user.click(screen.getByRole('button', { name: /show password/i }));
    expect(password).toHaveAttribute('type', 'text');
    expect(confirmation).toHaveAttribute('type', 'text');
    await user.click(screen.getByRole('button', { name: /hide password/i }));
    expect(password).toHaveAttribute('type', 'password');
    expect(confirmation).toHaveAttribute('type', 'password');
  });

  it('requires matching passwords before submitting registration', async () => {
    const user = userEvent.setup();
    renderAt('/register');
    await user.type(screen.getByRole('textbox', { name: /email address/i }), 'driver@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'a-long-test-password');
    await user.type(screen.getByLabelText(/confirm password/i), 'a-different-password');
    await user.click(screen.getByRole('button', { name: /create account/i }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/passwords do not match/i);
    expect(fetch).not.toHaveBeenCalled();
  });

  it('shows an accessible registration form at /register', () => {
    renderAt('/register');

    expect(screen.getByRole('heading', { name: /create your account/i })).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: /email address/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toHaveAttribute('type', 'password');
    expect(screen.getByLabelText(/confirm password/i)).toHaveAttribute('type', 'password');
    expect(screen.getByText(/at least 12 characters/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  });

  it('shows a useful error when login is rejected by the API', async () => {
    const user = userEvent.setup();
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ error: { code: 'invalid_credentials', message: 'Email or password is incorrect.' } }),
    } as Response);
    renderAt('/login');

    await user.type(screen.getByRole('textbox', { name: /email address/i }), 'driver@example.com');
    await user.type(screen.getByLabelText(/password/i), 'incorrect-password');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent('Email or password is incorrect.');
    expect(localStorage.getItem('car-inventory-token')).toBeNull();
  });

  it('submits registration and confirms successful account creation', async () => {
    const user = userEvent.setup();
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        id: '123e4567-e89b-42d3-a456-426614174000',
        email: 'driver@example.com',
        role: 'user',
        created_at: '2026-10-25T10:00:00Z',
      }),
    } as Response);
    renderAt('/register');

    await user.type(screen.getByRole('textbox', { name: /email address/i }), 'driver@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'a-long-test-password');
    await user.type(screen.getByLabelText(/confirm password/i), 'a-long-test-password');
    await user.click(screen.getByRole('button', { name: /create account/i }));

    expect(await screen.findByRole('status')).toHaveTextContent(/account created/i);
    await waitFor(() => expect(fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/auth\/register$/),
      expect.objectContaining({ method: 'POST' }),
    ));
  });
});
