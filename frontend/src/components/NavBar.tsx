import { Link, NavLink, useNavigate } from 'react-router-dom'
import { CATEGORIES } from '../api'
import { useAuth } from '../auth'
import { useChatResults } from '../chatResults'
import Logo from './Logo'

const GUEST_LINKS = [
  { to: '/login', label: 'Log In' },
  { to: '/create-account', label: 'Create Account' },
]

// Clicking a dropdown link moves focus off the menu so it closes (it opens on hover or focus).
function closeMenu() {
  if (document.activeElement instanceof HTMLElement) document.activeElement.blur()
}

export default function NavBar() {
  const { user, logout } = useAuth()
  const { clear: clearChatResults } = useChatResults()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    clearChatResults() // don't leave one shopper's chat matches on screen for the next
    navigate('/')
  }

  return (
    <>
      <header className="site-header">
        <div className="announce">OFFICIAL YALE GEAR FOR THE WHOLE FAMILY</div>
        <Link to="/" className="brand" aria-label="Campus Customs home">
          <Logo className="brand-logo" />
        </Link>
      </header>
      <nav className="nav" aria-label="Main">
        <ul className="nav-links">
          <li>
            <NavLink to="/" end className="nav-link">Home</NavLink>
          </li>
          <li className="nav-dropdown">
            <NavLink to="/products" className="nav-link" aria-haspopup="true">
              Products <span className="caret" aria-hidden="true">▾</span>
            </NavLink>
            <ul className="dropdown" aria-label="Collections">
              <li>
                <Link to="/products" className="dropdown-link" onClick={closeMenu}>All products</Link>
              </li>
              {CATEGORIES.map((c) => (
                <li key={c}>
                  <Link
                    to={`/products?category=${encodeURIComponent(c)}`}
                    className="dropdown-link"
                    onClick={closeMenu}
                  >
                    {c}
                  </Link>
                </li>
              ))}
            </ul>
          </li>
          <li>
            <NavLink to="/about" end className="nav-link">About Us</NavLink>
          </li>
          {user ? (
            <>
              <li className="nav-greeting">Hi, {user.first_name || user.name}</li>
              <li>
                <button type="button" className="nav-link nav-button" onClick={handleLogout}>Log Out</button>
              </li>
            </>
          ) : (
            GUEST_LINKS.map((link) => (
              <li key={link.to}>
                <NavLink to={link.to} end className="nav-link">{link.label}</NavLink>
              </li>
            ))
          )}
        </ul>
      </nav>
    </>
  )
}
