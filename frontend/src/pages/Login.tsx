import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

export default function Login() {
  const { user, login, logout } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const form = new FormData(e.currentTarget)
    setError(null)
    setSubmitting(true)
    try {
      await login(String(form.get('email')), String(form.get('password')))
      navigate('/')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  if (user) {
    return (
      <section className="section auth">
        <h1>You're logged in</h1>
        <p className="lead">Signed in as {user.email}.</p>
        <div className="auth-actions">
          <Link to="/products" className="btn">Shop products</Link>
          <button type="button" className="btn btn-outline" onClick={logout}>Log out</button>
        </div>
      </section>
    )
  }

  return (
    <section className="section auth">
      <h1>Log In</h1>
      <p className="lead">Welcome back, Bulldog.</p>
      <form className="form" onSubmit={submit}>
        <label htmlFor="login-email">Email</label>
        <input id="login-email" name="email" type="email" autoComplete="email" required />
        <label htmlFor="login-password">Password</label>
        <input id="login-password" name="password" type="password" autoComplete="current-password" required />
        <button type="submit" className="btn" disabled={submitting}>
          {submitting ? 'Logging in…' : 'Log In'}
        </button>
        {error && <p className="form-error" role="alert">{error}</p>}
      </form>
      <p className="auth-switch">
        New here? <Link to="/create-account">Create an account</Link>
      </p>
    </section>
  )
}
