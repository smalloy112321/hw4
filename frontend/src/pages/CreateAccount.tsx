import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

const MIN_PASSWORD = 8

export default function CreateAccount() {
  const { user, register } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const form = new FormData(e.currentTarget)
    const password = String(form.get('password'))
    if (password.length < MIN_PASSWORD) {
      setError(`Password must be at least ${MIN_PASSWORD} characters.`)
      return
    }
    if (password !== form.get('confirm')) {
      setError('Passwords do not match.')
      return
    }
    setError(null)
    setSubmitting(true)
    try {
      await register({
        first_name: String(form.get('first_name')),
        last_name: String(form.get('last_name')),
        email: String(form.get('email')),
        password,
      })
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
        <h1>You already have an account</h1>
        <p className="lead">You're signed in as {user.email}.</p>
        <Link to="/products" className="btn">Shop products</Link>
      </section>
    )
  }

  return (
    <section className="section auth">
      <h1>Create Account</h1>
      <p className="lead">Join the Campus Customs family to chat with us and keep your favorites handy.</p>
      <form className="form" onSubmit={submit}>
        <div className="form-row">
          <div>
            <label htmlFor="first-name">First name</label>
            <input id="first-name" name="first_name" autoComplete="given-name" maxLength={60} required />
          </div>
          <div>
            <label htmlFor="last-name">Last name</label>
            <input id="last-name" name="last_name" autoComplete="family-name" maxLength={60} required />
          </div>
        </div>
        <label htmlFor="signup-email">Email</label>
        <input id="signup-email" name="email" type="email" autoComplete="email" required />
        <label htmlFor="signup-password">Password</label>
        <input
          id="signup-password"
          name="password"
          type="password"
          autoComplete="new-password"
          minLength={MIN_PASSWORD}
          maxLength={128}
          aria-describedby="password-hint"
          required
        />
        <p id="password-hint" className="hint">At least {MIN_PASSWORD} characters.</p>
        <label htmlFor="signup-confirm">Confirm password</label>
        <input id="signup-confirm" name="confirm" type="password" autoComplete="new-password" required />
        <button type="submit" className="btn" disabled={submitting}>
          {submitting ? 'Creating account…' : 'Create Account'}
        </button>
        {error && <p className="form-error" role="alert">{error}</p>}
      </form>
      <p className="auth-switch">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </section>
  )
}
