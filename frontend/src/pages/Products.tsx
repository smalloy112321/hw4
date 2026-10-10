import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { CATEGORIES, SIZES, categoryOf, fetchProducts, type ProductSummary } from '../api'
import ProductCard from '../components/ProductCard'
import { ErrorMessage, Loading } from '../components/Status'

const SORTS = [
  { value: '', label: 'Featured' },
  { value: 'price-asc', label: 'Price: Low to High' },
  { value: 'price-desc', label: 'Price: High to Low' },
] as const

// Every filter lives in the URL (?category=&color=&size=&sort=&q=) so views can be shared,
// bookmarked, and restored with the Back button.
export default function Products() {
  const [products, setProducts] = useState<ProductSummary[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [params, setParams] = useSearchParams()
  const category = params.get('category') ?? ''
  const search = params.get('q') ?? ''
  const color = params.get('color') ?? ''
  const size = params.get('size') ?? ''
  const sort = params.get('sort') ?? ''

  function load() {
    fetchProducts()
      .then(setProducts)
      .catch((e: Error) => setError(e.message))
  }
  useEffect(load, [])

  function retry() {
    setError(null)
    load()
  }

  // Read the live URL (not the last render's copy) so quick successive clicks never undo each other.
  function update(key: string, value: string) {
    const next = new URLSearchParams(window.location.search)
    if (value) next.set(key, value)
    else next.delete(key)
    setParams(next, { replace: true })
  }

  function clearFilters() {
    const next = new URLSearchParams()
    const current = new URLSearchParams(window.location.search).get('category')
    if (current) next.set('category', current)
    setParams(next, { replace: true })
  }

  // Items in the current collection (category + search), before color/size narrow it down.
  const inCollection = useMemo(() => {
    if (!products) return []
    const q = search.trim().toLowerCase()
    return products.filter((p) => {
      if (category && categoryOf(p.garment_type) !== category) return false
      if (!q) return true
      return [p.name, p.garment_type, p.description, ...p.colors].some((f) => f.toLowerCase().includes(q))
    })
  }, [products, category, search])

  // Dropdown options with counts, so shoppers never pick a combination with zero results blindly.
  const colorOptions = useMemo(() => {
    const counts = new Map<string, number>()
    for (const p of inCollection) if (p.color_family) counts.set(p.color_family, (counts.get(p.color_family) ?? 0) + 1)
    return [...counts.entries()].sort((a, b) => b[1] - a[1])
  }, [inCollection])

  const sizeOptions = useMemo(
    () => SIZES.map((s) => [s, inCollection.filter((p) => p.sizes_in_stock.includes(s)).length] as const),
    [inCollection],
  )

  const shown = useMemo(() => {
    const list = inCollection.filter(
      (p) => (!color || p.color_family === color) && (!size || p.sizes_in_stock.includes(size)),
    )
    if (sort === 'price-asc') return [...list].sort((a, b) => a.price - b.price || a.name.localeCompare(b.name))
    if (sort === 'price-desc') return [...list].sort((a, b) => b.price - a.price || a.name.localeCompare(b.name))
    return list
  }, [inCollection, color, size, sort])

  const filtersOn = Boolean(color || size || sort || search)

  return (
    <section className="section">
      <h1>{category ? `Shop ${category}` : 'Shop all products'}</h1>
      <p className="lead">Every piece below comes straight from our current catalogue, with live prices.</p>

      <div className="filters">
        <label htmlFor="product-search" className="sr-only">Search products</label>
        <input
          id="product-search"
          type="search"
          placeholder="Search hoodies, colors, sports…"
          value={search}
          onChange={(e) => update('q', e.target.value)}
        />
        <div className="chips" role="group" aria-label="Filter by category">
          <button type="button" className="chip" aria-pressed={!category} onClick={() => update('category', '')}>
            All
          </button>
          {CATEGORIES.map((c) => (
            <button key={c} type="button" className="chip" aria-pressed={category === c} onClick={() => update('category', c)}>
              {c}
            </button>
          ))}
        </div>

        <div className="refine" role="group" aria-label="Refine and sort">
          <div className="select-field">
            <label htmlFor="filter-color">Color</label>
            <select id="filter-color" value={color} onChange={(e) => update('color', e.target.value)}>
              <option value="">All colors</option>
              {colorOptions.map(([c, n]) => (
                <option key={c} value={c}>{c} ({n})</option>
              ))}
              {color && !colorOptions.some(([c]) => c === color) && <option value={color}>{color} (0)</option>}
            </select>
          </div>
          <div className="select-field">
            <label htmlFor="filter-size">Size in stock</label>
            <select id="filter-size" value={size} onChange={(e) => update('size', e.target.value)}>
              <option value="">All sizes</option>
              {sizeOptions.map(([s, n]) => (
                <option key={s} value={s} disabled={n === 0 && size !== s}>{s} ({n})</option>
              ))}
            </select>
          </div>
          <div className="select-field">
            <label htmlFor="sort">Sort by</label>
            <select id="sort" value={sort} onChange={(e) => update('sort', e.target.value)}>
              {SORTS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
          {filtersOn && (
            <button type="button" className="clear-filters" onClick={clearFilters}>
              Clear filters
            </button>
          )}
        </div>
      </div>

      {error && <ErrorMessage message={error} onRetry={retry} />}
      {!products && !error && <Loading label="Loading products…" />}
      {products && (
        <>
          <p className="result-count" aria-live="polite">
            {shown.length} {shown.length === 1 ? 'item' : 'items'}
          </p>
          {shown.length === 0 ? (
            <p className="empty">
              Nothing matches those filters right now.{' '}
              <button type="button" className="link-button" onClick={clearFilters}>Clear filters</button> to see more.
            </p>
          ) : (
            <div className="grid">
              {shown.map((p) => <ProductCard key={p.product_id} product={p} />)}
            </div>
          )}
        </>
      )}
    </section>
  )
}
