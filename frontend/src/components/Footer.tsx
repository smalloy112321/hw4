import { Link } from 'react-router-dom'

const YEAR = new Date().getFullYear()

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div>
          <p className="footer-brand">Campus Customs</p>
          <p>Bulldog gear for students, alumni, and the whole family. New Haven, CT.</p>
        </div>
        <nav aria-label="Footer">
          <ul className="footer-links">
            <li><Link to="/products">Shop all</Link></li>
            <li><Link to="/about">About Us</Link></li>
            <li><Link to="/create-account">Create Account</Link></li>
          </ul>
        </nav>
      </div>
      <p className="footer-fine">© {YEAR} Campus Customs · Officially licensed merchandise</p>
    </footer>
  )
}
