import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, formatPrice, type ProductDetail } from '../api'
import { ErrorMessage, Loading } from '../components/Status'

const LOW_STOCK = 3

// PDP: large image on the left; Name, Sizes, Price, Description on the right.
export default function ProductPage() {
  const { productId = '' } = useParams()
  // Keying by product id gives each product fresh state (no leftover size or image).
  return <ProductView key={productId} productId={productId} />
}

function ProductView({ productId }: { productId: string }) {
  const [product, setProduct] = useState<ProductDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [size, setSize] = useState<string | null>(null)
  const [cartMessage, setCartMessage] = useState<{ ok: boolean; text: string } | null>(null)

  useEffect(() => {
    fetchProduct(productId)
      .then(setProduct)
      .catch((e: Error) => setError(e.message))
  }, [productId])

  const selected = product?.sizes.find((s) => s.size === size)
  const soldOut = product ? !product.in_stock : false

  function chooseSize(next: string) {
    setSize(next)
    setCartMessage(null)
  }

  // No checkout yet: the button confirms the choice on the page but does not save a cart.
  function addToCart() {
    if (!product) return
    if (!selected) {
      setCartMessage({ ok: false, text: 'Choose a size first.' })
      return
    }
    setCartMessage({ ok: true, text: `Added ${product.name} (size ${selected.size}) to your cart.` })
  }

  return (
    <section className="section">
      <Link to="/products" className="back-link">← Back to products</Link>
      {error && <ErrorMessage message={error} />}
      {!product && !error && <Loading label="Loading product…" />}
      {product && (
        <div className="pdp">
          <div className="pdp-image">
            <img src={product.image_url} alt={product.name} />
          </div>
          <div className="pdp-info">
            <h1 className="pdp-name">{product.name}</h1>

            <fieldset className="sizes">
              <legend>Sizes</legend>
              <div className="size-options">
                {product.sizes.map((s) => (
                  <button
                    key={s.size}
                    type="button"
                    className="size"
                    disabled={!s.in_stock}
                    aria-pressed={size === s.size}
                    aria-label={s.in_stock ? `Size ${s.size}` : `Size ${s.size}, sold out`}
                    onClick={() => chooseSize(s.size)}
                  >
                    {s.size}
                  </button>
                ))}
              </div>
              <p className="size-note" aria-live="polite">
                {selected && selected.quantity <= LOW_STOCK && `Only ${selected.quantity} left in ${selected.size}.`}
                {selected && selected.quantity > LOW_STOCK && `${selected.size} is in stock.`}
              </p>
            </fieldset>

            <p className="pdp-price">{formatPrice(product.price)}</p>

            <div className="add-to-cart">
              <button type="button" className="btn btn-block" onClick={addToCart} disabled={soldOut}>
                {soldOut ? 'Sold out' : 'Add to cart'}
              </button>
              {cartMessage && (
                <p className={cartMessage.ok ? 'cart-note' : 'cart-note cart-note-error'} role={cartMessage.ok ? 'status' : 'alert'}>
                  {cartMessage.text}
                </p>
              )}
            </div>

            <div className="pdp-desc">
              <h2>Description</h2>
              <p>{product.description}</p>
              <p className="pdp-colors">Colors: {product.colors.join(', ')}</p>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}
