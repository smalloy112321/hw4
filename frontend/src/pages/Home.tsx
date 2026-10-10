import { Link } from 'react-router-dom'
import heroImage from '../assets/hero-yale-fans.jpg'

// One catalogue photo per collection. scripts/build_collection_tiles.py writes trimmed, centered
// copies to /collections/ from the data pack; if they're missing, the raw product photo is used.
const COLLECTIONS = [
  { category: 'Hoodies', tile: 'hoodies', productId: 'district-vit-hoodie-vintage-bulldog' },
  { category: 'Crewnecks', tile: 'crewnecks', productId: 'champion-mens-triumph-raglan-crew' },
  { category: 'T-Shirts', tile: 't-shirts', productId: 'district-tri-blend-t-shirt-vintage-shield' },
  { category: 'Quarter-Zips', tile: 'quarter-zips', productId: 'branford-1-4-zip' },
]

export default function Home() {
  return (
    <>
      <section className="hero">
        <img
          className="hero-image"
          src={heroImage}
          alt="Yale fans cheering in the stands, holding a Let's Go Yale banner and a Boola Boola sign"
        />
        <div className="hero-inner">
          <p className="eyebrow">Yale gear from New Haven</p>
          <h1>Wear your Bulldog pride every day.</h1>
          <div className="hero-actions">
            <Link to="/products" className="btn btn-light">Shop all products</Link>
            <Link to="/about" className="btn btn-ghost">Our story</Link>
          </div>
        </div>
      </section>

      <section className="section">
        <h2>Shop by collection</h2>
        <ul className="collections">
          {COLLECTIONS.map((c) => (
            <li key={c.category}>
              <Link to={`/products?category=${encodeURIComponent(c.category)}`} className="collection">
                <span className="collection-image">
                  <img
                    src={`/collections/${c.tile}.jpg`}
                    alt=""
                    loading="lazy"
                    onError={(e) => {
                      const img = e.currentTarget
                      const fallback = `/images/${c.productId}.jpg`
                      if (!img.src.endsWith(fallback)) img.src = fallback
                    }}
                  />
                </span>
                <span className="collection-text">
                  <span className="collection-name">{c.category}</span>
                  <span className="collection-cta" aria-hidden="true">Shop now →</span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </>
  )
}
