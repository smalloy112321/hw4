import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <section className="section prose">
      <h1>Page not found</h1>
      <p>That page wandered off campus. Let's get you back on track.</p>
      <p><Link to="/products" className="btn">Shop products</Link></p>
    </section>
  )
}
