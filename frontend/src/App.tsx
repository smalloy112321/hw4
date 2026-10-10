import { Route, Routes } from 'react-router-dom'
import { useAuth } from './auth'
import NavBar from './components/NavBar'
import Footer from './components/Footer'
import ChatWidget from './components/ChatWidget'
import ChatResultsPanel from './components/ChatResultsPanel'
import ScrollToTop from './components/ScrollToTop'
import Home from './pages/Home'
import Products from './pages/Products'
import ProductPage from './pages/ProductPage'
import About from './pages/About'
import Login from './pages/Login'
import CreateAccount from './pages/CreateAccount'
import NotFound from './pages/NotFound'

export default function App() {
  const { user, loading } = useAuth()
  return (
    <div className="app">
      <a className="skip-link" href="#main">Skip to content</a>
      <ScrollToTop />
      <NavBar />
      <main id="main" className="main">
        <ChatResultsPanel />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:productId" element={<ProductPage />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/create-account" element={<CreateAccount />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
      {/* Keyed by account: logging in or out starts a fresh widget that loads the right history. */}
      {!loading && <ChatWidget key={user ? `user-${user.id}` : 'guest'} />}
    </div>
  )
}
