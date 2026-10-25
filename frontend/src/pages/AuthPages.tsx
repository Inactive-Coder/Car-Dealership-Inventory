import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { ApiError } from '../services/api';

function AuthFrame({ children, eyebrow }: { children: React.ReactNode; eyebrow: string }) {
  return (
    <main className="auth-shell">
      <section className="auth-story" aria-label="About the dealership">
        <Link className="brand-lockup" to="/login" aria-label="Incubyte Motors home">
          <span className="brand-mark" aria-hidden="true">IM</span>
          <span>Incubyte <span className="brand-light">Motors</span></span>
        </Link>
        <div className="story-copy">
          <p className="eyebrow">Curated inventory. Clear decisions.</p>
          <h1>Find the car<br />that moves you.</h1>
          <p className="story-note">Explore a considered collection of exceptional vehicles, prepared for the next chapter.</p>
        </div>
        <p className="story-foot">EST. 1987 <span aria-hidden="true">—</span> BUILT AROUND THE DRIVE</p>
      </section>
      <section className="auth-panel">
        <div className="auth-card">
          <p className="eyebrow auth-eyebrow">{eyebrow}</p>
          {children}
        </div>
        <p className="auth-legal">By continuing, you agree to our terms and privacy policy.</p>
      </section>
    </main>
  );
}

function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return 'Something went wrong. Please try again.';
}

export function LoginPage() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setPending(true);
    try {
      await signIn(email.trim(), password);
      navigate('/inventory', { replace: true });
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setPending(false);
    }
  }

  return (
    <AuthFrame eyebrow="Your next drive starts here">
      <h2>Welcome back</h2>
      <p className="auth-description">Sign in to view inventory and manage your shortlist.</p>
      <form className="auth-form" onSubmit={handleSubmit}>
        <label htmlFor="login-email">Email address</label>
        <input id="login-email" name="email" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} />
        <div className="label-row">
          <label htmlFor="login-password">Password</label>
        </div>
        <input id="login-password" name="password" type={showPassword ? 'text' : 'password'} autoComplete="current-password" required value={password} onChange={(event) => setPassword(event.target.value)} />
        <button className="password-toggle" type="button" aria-pressed={showPassword} onClick={() => setShowPassword((visible) => !visible)}>
          {showPassword ? 'Hide password' : 'Show password'}
        </button>
        {error && <p className="form-error" role="alert">{error}</p>}
        <button className="button button-primary auth-submit" type="submit" disabled={pending}>
          {pending ? 'Signing in…' : 'Sign in'}
          <span aria-hidden="true">→</span>
        </button>
      </form>
      <p className="auth-switch">New to Incubyte Motors? <Link to="/register">Create an account</Link></p>
    </AuthFrame>
  );
}

export function RegisterPage() {
  const { signUp } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    if (password !== confirmPassword) {
      setError('Passwords do not match. Please check both fields.');
      return;
    }
    setPending(true);
    try {
      await signUp(email.trim(), password);
      setSuccess(true);
    } catch (reason) {
      setError(errorMessage(reason));
    } finally {
      setPending(false);
    }
  }

  return (
    <AuthFrame eyebrow="A better way to find your next car">
      <h2>Create your account</h2>
      <p className="auth-description">Save time and get a closer look at our current collection.</p>
      {success ? (
        <div className="success-panel" role="status">
          <span className="success-check" aria-hidden="true">✓</span>
          <p>Account created. You can sign in now.</p>
          <Link className="button button-primary" to="/login">Go to sign in</Link>
        </div>
      ) : (
        <form className="auth-form" onSubmit={handleSubmit}>
          <label htmlFor="register-email">Email address</label>
          <input id="register-email" name="email" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} />
          <label htmlFor="register-password">Password</label>
          <input id="register-password" name="password" type={showPassword ? 'text' : 'password'} autoComplete="new-password" minLength={12} required aria-describedby="password-guidance" value={password} onChange={(event) => setPassword(event.target.value)} />
          <p className="input-hint" id="password-guidance">Create a password with at least 12 characters. A longer, unique passphrase is easier to remember and harder to guess.</p>
          <label htmlFor="register-confirm-password">Confirm password</label>
          <input id="register-confirm-password" name="confirm-password" type={showPassword ? 'text' : 'password'} autoComplete="new-password" minLength={12} required value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} />
          <button className="password-toggle" type="button" aria-pressed={showPassword} onClick={() => setShowPassword((visible) => !visible)}>
            {showPassword ? 'Hide password' : 'Show password'}
          </button>
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="button button-primary auth-submit" type="submit" disabled={pending}>
            {pending ? 'Creating account…' : 'Create account'}
            <span aria-hidden="true">→</span>
          </button>
        </form>
      )}
      <p className="auth-switch">Already a member? <Link to="/login">Sign in</Link></p>
    </AuthFrame>
  );
}
