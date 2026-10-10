import { Link } from 'react-router-dom'
import { formatPrice, shortDescription, type ChatProductCard, type ProductSummary } from '../api'

// Used by the Products page (ProductSummary) and by chat results (ChatProductCard).
// Either way, clicking the card opens the product's detail page (PDP).
export default function ProductCard({ product }: { product: ProductSummary | ChatProductCard }) {
  const info = 'short_description' in product ? product.short_description : shortDescription(product.description)
  return (
    <Link to={`/products/${product.product_id}`} className="card">
      <div className="card-image">
        <img src={product.image_url} alt={product.name} loading="lazy" />
        {!product.in_stock && <span className="badge">Sold out</span>}
      </div>
      <div className="card-body">
        <h3 className="card-title">{product.name}</h3>
        <p className="card-price">{formatPrice(product.price)}</p>
        <p className="card-desc">{info}</p>
        {'sizes_in_stock' in product && product.in_stock && (
          <p className="card-sizes">In stock: {product.sizes_in_stock.join(', ')}</p>
        )}
      </div>
    </Link>
  )
}
