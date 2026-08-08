import { useEffect, useState } from 'react'

export default function Store() {
  const [products, setProducts] = useState([])
  const [creator, setCreator] = useState(null)
  const [loading, setLoading] = useState(true)
  const [tg, setTg] = useState(null)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://your-bot.fly.dev'

  useEffect(() => {
    // Инициализация Telegram WebApp
    const initTg = () => {
      if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
        const webapp = window.Telegram.WebApp
        webapp.ready()
        webapp.expand()
        setTg(webapp)

        // Получаем параметры из URL
        const params = new URLSearchParams(window.location.search)
        const creatorId = params.get('creator')
        const productId = params.get('product')

        loadData(creatorId, productId)
      }
    }

    // Загружаем скрипт Telegram WebApp
    if (typeof window !== 'undefined') {
      if (window.Telegram?.WebApp) {
        initTg()
      } else {
        const script = document.createElement('script')
        script.src = 'https://telegram.org/js/telegram-web-app.js'
        script.onload = initTg
        document.head.appendChild(script)
      }
    }
  }, [])

  const loadData = async (creatorId, productId) => {
    try {
      let url = `${API_URL}/api/products`
      if (creatorId) url += `?creator_id=${creatorId}`
      if (productId) url = `${API_URL}/api/products/${productId}`

      const res = await fetch(url)
      const data = await res.json()

      if (productId) {
        setProducts([data])
        if (data.creator) setCreator(data.creator)
      } else {
        setProducts(data.products || [])
        if (data.creator) setCreator(data.creator)
      }
    } catch (err) {
      console.error('Error loading products:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleBuy = (product) => {
    if (!tg) return

    // Открываем бота для покупки
    tg.openTelegramLink(`https://t.me/${process.env.NEXT_PUBLIC_BOT_USERNAME || 'your_bot'}?start=buy_${product.id}`)
  }

  const handleShare = (product) => {
    if (!tg) return
    const text = `🛍 ${product.name} — ${product.price_stars} Stars`
    const url = `${window.location.origin}?product=${product.id}`
    tg.openTelegramLink(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`)
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Загрузка...</div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="header">
        <h1>🛍 Digital Store</h1>
        <p>Цифровые товары от креаторов</p>
      </div>

      {creator && (
        <div className="creator-info">
          <div className="creator-avatar">
            {creator.first_name?.[0] || '?'}
          </div>
          <div>
            <div className="creator-name">{creator.first_name}</div>
            <div className="creator-stats">{products.length} товаров</div>
          </div>
        </div>
      )}

      {products.length === 0 ? (
        <div className="empty-state">
          <p>📭 Пока нет товаров</p>
          <p style={{fontSize: '13px', marginTop: '8px'}}>Загляни позже или найди другого креатора</p>
        </div>
      ) : (
        <div className="products-grid">
          {products.map(product => (
            <div key={product.id} className="product-card">
              <h3>{product.name}</h3>
              <p>{product.description || 'Цифровой товар'}</p>
              <div className="product-footer">
                <span className="price">💎 {product.price_stars}</span>
                <div style={{display: 'flex', gap: '8px'}}>
                  <button 
                    className="buy-btn" 
                    onClick={() => handleBuy(product)}
                    style={{background: 'var(--tg-theme-button-color, #3390ec)'}}
                  >
                    Купить
                  </button>
                  <button 
                    className="buy-btn" 
                    onClick={() => handleShare(product)}
                    style={{background: 'var(--tg-theme-hint-color, #999)', padding: '8px 12px'}}
                  >
                    ↗️
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
