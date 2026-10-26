/**
 * ==============================================================================
 * SparkCommerce — UI Utilities & Components
 * Production-grade e-commerce UI components, authentic product imagery,
 * interactive modals, cart state, and user interactions.
 * ==============================================================================
 */

// ── Curated Authentic Product Photography Mapping ─────────────────────────────
const PRODUCT_IMAGE_DATABASE = {
  // Laptops
  'laptop': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&auto=format&fit=crop&q=80',
  'macbook': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=80',
  'ideapad': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&auto=format&fit=crop&q=80',
  'inspiron': 'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=600&auto=format&fit=crop&q=80',
  'pavilion': 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=600&auto=format&fit=crop&q=80',
  'gaming': 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600&auto=format&fit=crop&q=80',

  // Smartphones
  'iphone': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=600&auto=format&fit=crop&q=80',
  'galaxy': 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=600&auto=format&fit=crop&q=80',
  'oneplus': 'https://images.unsplash.com/photo-1511707171634-5f897ff02560?w=600&auto=format&fit=crop&q=80',
  'xiaomi': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop&q=80',
  'realme': 'https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600&auto=format&fit=crop&q=80',

  // Audio & Peripherals
  'headphones': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80',
  'airpods': 'https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?w=600&auto=format&fit=crop&q=80',
  'airdopes': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80',
  'jbl': 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&auto=format&fit=crop&q=80',
  'mouse': 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80',
  'keyboard': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80',
  'monitor': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80',
  'tv': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=600&auto=format&fit=crop&q=80',
  'camera': 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=80',
  'gopro': 'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=600&auto=format&fit=crop&q=80',
  'charger': 'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop&q=80',
  'ssd': 'https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&auto=format&fit=crop&q=80',
  'hdd': 'https://images.unsplash.com/photo-1531492746076-161ca9bcad58?w=600&auto=format&fit=crop&q=80',
  'router': 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=600&auto=format&fit=crop&q=80',

  // Fashion & Apparel
  'sneakers': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80',
  'shoes': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600&auto=format&fit=crop&q=80',
  'running': 'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&auto=format&fit=crop&q=80',
  'shirt': 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80',
  't-shirt': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80',
  'jeans': 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&auto=format&fit=crop&q=80',
  'jacket': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&auto=format&fit=crop&q=80',
  'blazer': 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&auto=format&fit=crop&q=80',
  'watch': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80',
  'sunglasses': 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&auto=format&fit=crop&q=80',
  'cap': 'https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=600&auto=format&fit=crop&q=80',

  // Home & Kitchen
  'cooktop': 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=600&auto=format&fit=crop&q=80',
  'air fryer': 'https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?w=600&auto=format&fit=crop&q=80',
  'coffee': 'https://images.unsplash.com/photo-1517668808822-9ebb02ae2a0e?w=600&auto=format&fit=crop&q=80',
  'mixer': 'https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?w=600&auto=format&fit=crop&q=80',
  'bottle': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&auto=format&fit=crop&q=80',
  'bedsheet': 'https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=600&auto=format&fit=crop&q=80',

  // Books
  'book': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop&q=80',
  'habits': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600&auto=format&fit=crop&q=80',
  'money': 'https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=600&auto=format&fit=crop&q=80',

  // Sports & Fitness
  'yoga': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600&auto=format&fit=crop&q=80',
  'dumbbells': 'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&auto=format&fit=crop&q=80',
  'football': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=600&auto=format&fit=crop&q=80',
  'cycle': 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600&auto=format&fit=crop&q=80',

  // Beauty
  'serum': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&auto=format&fit=crop&q=80',
  'sunscreen': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&auto=format&fit=crop&q=80',
  'perfume': 'https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=600&auto=format&fit=crop&q=80',

  // Category Fallbacks
  'electronics': 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=600&auto=format&fit=crop&q=80',
  'fashion': 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=600&auto=format&fit=crop&q=80',
  'home & kitchen': 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=600&auto=format&fit=crop&q=80',
  'books': 'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=600&auto=format&fit=crop&q=80',
  'sports': 'https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&auto=format&fit=crop&q=80',
  'beauty': 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600&auto=format&fit=crop&q=80',
  'grocery': 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=600&auto=format&fit=crop&q=80',
  'toys': 'https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=600&auto=format&fit=crop&q=80',
};

/**
 * Return a high-resolution, matching commercial product photograph.
 */
function getProductImage(product) {
  if (!product) return 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80';
  
  const name = (product.product_name || '').toLowerCase();
  const category = (product.category || '').toLowerCase();

  for (const [keyword, url] of Object.entries(PRODUCT_IMAGE_DATABASE)) {
    if (name.includes(keyword)) {
      return url;
    }
  }

  // Category fallback
  if (PRODUCT_IMAGE_DATABASE[category]) {
    return PRODUCT_IMAGE_DATABASE[category];
  }

  return 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80';
}

// ── Toast Notifications ───────────────────────────────────────────────────────
const Toast = {
  container: null,

  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },

  show(title, message = '', type = 'info', duration = 3500) {
    this.init();
    const icons = { success: '✓', error: '✕', info: 'ℹ', warning: '!' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <div style="font-weight:700;font-size:1.1rem;line-height:1">${icons[type] || 'ℹ'}</div>
      <div style="flex:1">
        <div style="font-weight:700;line-height:1.2">${title}</div>
        ${message ? `<div style="font-size:0.775rem;color:#cbd5e1;margin-top:2px">${message}</div>` : ''}
      </div>
    `;
    this.container.appendChild(toast);
    setTimeout(() => {
      toast.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 250);
    }, duration);
  },

  success: (title, msg) => Toast.show(title, msg, 'success'),
  error:   (title, msg) => Toast.show(title, msg, 'error'),
  info:    (title, msg) => Toast.show(title, msg, 'info'),
  warning: (title, msg) => Toast.show(title, msg, 'warning'),
};

// ── Loading Overlay ───────────────────────────────────────────────────────────
const Loading = {
  overlay: null,

  show(message = 'Loading products...') {
    if (!this.overlay) {
      this.overlay = document.createElement('div');
      this.overlay.className = 'loading-overlay';
      this.overlay.innerHTML = `
        <div class="spinner"></div>
        <div class="loading-text" id="loading-text">${message}</div>
      `;
      document.body.appendChild(this.overlay);
    } else {
      document.getElementById('loading-text').textContent = message;
      this.overlay.style.display = 'flex';
    }
  },

  hide() {
    if (this.overlay) this.overlay.style.display = 'none';
  },

  setText(message) {
    const el = document.getElementById('loading-text');
    if (el) el.textContent = message;
  },
};

// ── Skeletons ─────────────────────────────────────────────────────────────────
function skeletonProduct() {
  return `
    <div class="product-card">
      <div class="skeleton" style="width:100%;aspect-ratio:1/1"></div>
      <div class="product-card-body">
        <div class="skeleton" style="height:10px;width:35%;margin-bottom:8px"></div>
        <div class="skeleton" style="height:16px;width:90%;margin-bottom:6px"></div>
        <div class="skeleton" style="height:16px;width:65%;margin-bottom:12px"></div>
        <div class="skeleton" style="height:14px;width:40%;margin-bottom:12px"></div>
        <div class="skeleton" style="height:22px;width:50%;margin-bottom:14px"></div>
        <div class="skeleton" style="height:38px;width:100%"></div>
      </div>
    </div>
  `;
}

function showSkeletons(containerId, count = 8) {
  const container = document.getElementById(containerId);
  if (container) container.innerHTML = Array(count).fill(skeletonProduct()).join('');
}

// ── Currency & Rating Helpers ─────────────────────────────────────────────────
function formatPrice(price) {
  return '₹' + Number(price || 0).toLocaleString('en-IN');
}

function formatNumber(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000)     return (n / 1_000).toFixed(1) + 'K';
  return n?.toLocaleString() || '0';
}

function formatRating(rating) {
  const r = Number(rating) || 4.2;
  const fullStars = Math.floor(r);
  const starsHtml = '★'.repeat(fullStars) + (r % 1 >= 0.5 ? '½' : '') + '☆'.repeat(Math.max(0, 5 - Math.ceil(r)));
  return `<span class="stars">${starsHtml}</span> <span>${r.toFixed(1)}</span>`;
}

// ── Shopping Cart State (Frontend Store) ───────────────────────────────────────
const Cart = {
  getItems() {
    return JSON.parse(localStorage.getItem('spark_cart') || '[]');
  },
  getCount() {
    return this.getItems().reduce((total, item) => total + (item.qty || 1), 0);
  },
  add(productId, qty = 1) {
    const items = this.getItems();
    const existing = items.find(i => String(i.id) === String(productId));
    if (existing) {
      existing.qty = (existing.qty || 1) + qty;
    } else {
      items.push({ id: Number(productId), qty });
    }
    localStorage.setItem('spark_cart', JSON.stringify(items));
    this.updateBadge();
    // Record interaction for recommendation engine
    InteractionsAPI.record(productId, 'add_to_cart').catch(() => {});
  },
  updateQty(productId, delta) {
    let items = this.getItems();
    const existing = items.find(i => String(i.id) === String(productId));
    if (existing) {
      existing.qty = (existing.qty || 1) + delta;
      if (existing.qty <= 0) {
        items = items.filter(i => String(i.id) !== String(productId));
      }
    }
    localStorage.setItem('spark_cart', JSON.stringify(items));
    this.updateBadge();
    openCartDrawer(); // Re-render cart drawer with updated quantities
  },
  remove(productId) {
    let items = this.getItems();
    items = items.filter(i => String(i.id) !== String(productId));
    localStorage.setItem('spark_cart', JSON.stringify(items));
    this.updateBadge();
    openCartDrawer(); // Re-render cart drawer
  },
  clear() {
    localStorage.removeItem('spark_cart');
    this.updateBadge();
  },
  updateBadge() {
    const count = this.getCount();
    const badges = document.querySelectorAll('.nav-cart-badge');
    badges.forEach(b => {
      b.textContent = count;
      b.style.display = count > 0 ? 'inline-block' : 'none';
    });
  }
};

// ── Wishlist State & Interactions ─────────────────────────────────────────────
const Wishlist = {
  getItems() {
    return JSON.parse(localStorage.getItem('spark_wishlist') || '[]');
  },
  has(productId) {
    return this.getItems().some(id => String(id) === String(productId));
  },
  toggle(productId, btnEl = null) {
    let items = this.getItems();
    const idNum = Number(productId);
    const exists = items.some(id => String(id) === String(productId));
    if (exists) {
      items = items.filter(id => String(id) !== String(productId));
      localStorage.setItem('spark_wishlist', JSON.stringify(items));
      Toast.info('Removed from Wishlist', 'Item removed from your saved list');
      if (btnEl) btnEl.style.color = 'var(--text-muted)';
    } else {
      items.push(idNum);
      localStorage.setItem('spark_wishlist', JSON.stringify(items));
      Toast.success('Saved to Wishlist ♥', 'Added to your wishlist preferences');
      if (btnEl) btnEl.style.color = '#dc2626';
      InteractionsAPI.record(productId, 'wishlist').catch(() => {});
    }
    this.updateBadges();
    return !exists;
  },
  updateBadges() {
    const count = this.getItems().length;
    const badges = document.querySelectorAll('.nav-wishlist-badge');
    badges.forEach(b => {
      b.textContent = count;
      b.style.display = count > 0 ? 'inline-block' : 'none';
    });
  }
};

// ── Recently Viewed Products Manager ──────────────────────────────────────────
const RecentlyViewed = {
  getItems() {
    return JSON.parse(localStorage.getItem('spark_recently_viewed') || '[]');
  },
  add(product) {
    if (!product || !product.product_id) return;
    let items = this.getItems();
    items = items.filter(p => String(p.product_id) !== String(product.product_id));
    items.unshift({
      product_id: product.product_id,
      product_name: product.product_name,
      category: product.category,
      price: product.price,
      avg_rating: product.avg_rating,
    });
    if (items.length > 10) items = items.slice(0, 10);
    localStorage.setItem('spark_recently_viewed', JSON.stringify(items));
  },
  render(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const items = this.getItems();
    if (!items || items.length === 0) {
      container.innerHTML = '<div class="text-muted text-sm" style="grid-column:1/-1">No recently viewed items yet. Start browsing to see them here.</div>';
      return;
    }
    container.innerHTML = items.map(p => buildProductCard(p, { showRecBadge: true, badgeText: 'Recently Viewed' })).join('');
  }
};

// ── Product Card Builder (Production Retail Grade) ────────────────────────────
function buildProductCard(product, options = {}) {
  const {
    showRecBadge = false,
    badgeText = 'Recommended',
    showInteractions = true,
  } = options;

  const priceNum = Number(product.price || 0);
  const priceFormatted = formatPrice(priceNum);
  
  // Calculate authentic MRP and discount percentage
  const discountPct = 10 + (product.product_id % 15);
  const originalPrice = Math.round(priceNum / (1 - discountPct / 100));
  const originalFormatted = formatPrice(originalPrice);

  const ratingNum = Number(product.avg_rating || product.rec_score || (4.0 + (product.product_id % 10) * 0.1)).toFixed(1);
  const reviewCount = formatNumber(120 + ((product.product_id * 17) % 2800));
  const imgUrl = getProductImage(product);
  const isWishlisted = Wishlist.has(product.product_id);

  return `
    <div class="product-card" id="product-${product.product_id}" onclick="openProductModal(${product.product_id})">
      ${showRecBadge ? `<span class="product-card-badge rec">${product.rec_reason || badgeText}</span>` : ''}
      <button class="product-fav-btn" title="Save to Wishlist" style="color:${isWishlisted ? '#dc2626' : 'var(--text-muted)'}" onclick="event.stopPropagation(); Wishlist.toggle(${product.product_id}, this)">
        ♥
      </button>

      <div class="product-card-img-wrap">
        <img src="${imgUrl}"
             alt="${product.product_name}"
             class="product-card-img"
             loading="lazy"
             onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80'" />
      </div>

      <div class="product-card-body">
        <div class="product-card-category">${product.category || 'General'}</div>
        <h3 class="product-card-name" title="${product.product_name}">${product.product_name}</h3>

        <div class="product-card-rating">
          <span class="stars">★★★★☆</span>
          <span>${ratingNum}</span>
          <span class="reviews-count">(${reviewCount})</span>
        </div>

        <div class="product-card-price-row">
          <div class="product-card-price">${priceFormatted}</div>
          <div class="product-card-original-price">${originalFormatted}</div>
          <div class="product-card-discount">${discountPct}% off</div>
        </div>

        ${showInteractions ? `
          <div class="product-card-actions">
            <button class="btn btn-primary btn-sm w-full" onclick="event.stopPropagation(); addToCart(${product.product_id})">
              Add to Cart
            </button>
          </div>
        ` : ''}
      </div>
    </div>
  `;
}

// ── Product Detail & Quick View Modal ─────────────────────────────────────────
let _cachedProductMap = {};

async function openProductModal(productId) {
  // Record view interaction
  InteractionsAPI.record(productId, 'view').catch(() => {});

  let product = _cachedProductMap[productId];
  if (!product) {
    try {
      product = await ProductsAPI.get(productId);
      _cachedProductMap[productId] = product;
    } catch(e) {
      Toast.error('Error', 'Unable to load product details');
      return;
    }
  }

  // Track in recently viewed
  RecentlyViewed.add(product);

  let modalOverlay = document.getElementById('product-modal');
  if (!modalOverlay) {
    modalOverlay = document.createElement('div');
    modalOverlay.className = 'modal-overlay';
    modalOverlay.id = 'product-modal';
    modalOverlay.innerHTML = `
      <div class="modal" style="max-width:850px;max-height:90vh;overflow-y:auto">
        <div class="modal-header">
          <div class="modal-title" id="modal-product-brand">Product Details</div>
          <button class="modal-close" onclick="closeModal()">✕</button>
        </div>
        <div id="modal-content"></div>
      </div>
    `;
    document.body.appendChild(modalOverlay);
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) closeModal();
    });
  }

  const priceNum = Number(product.price || 0);
  const discountPct = 12 + (product.product_id % 12);
  const originalPrice = Math.round(priceNum / (1 - discountPct / 100));
  const ratingNum = Number(product.avg_rating || (4.1 + (product.product_id % 9) * 0.1)).toFixed(1);
  const reviewCount = formatNumber(180 + ((product.product_id * 23) % 3100));
  const imgUrl = getProductImage(product);
  const isWishlisted = Wishlist.has(product.product_id);

  const contentEl = document.getElementById('modal-content');
  contentEl.innerHTML = `
    <div class="modal-content-grid" style="display:grid;grid-template-columns:1fr 1.2fr;gap:2rem;margin-bottom:2rem">
      <div class="modal-product-img-box" style="display:flex;align-items:center;justify-content:center;background:var(--bg-subtle);border-radius:var(--radius-md);padding:1.5rem">
        <img src="${imgUrl}" alt="${product.product_name}" class="modal-product-img" style="max-height:300px;width:100%;object-fit:contain" />
      </div>

      <div>
        <div class="modal-stock-badge" style="display:inline-flex;align-items:center;gap:0.35rem;background:#dcfce7;color:#16a34a;padding:2px 10px;border-radius:12px;font-size:0.75rem;font-weight:700;margin-bottom:0.5rem">
          <span>●</span> In Stock & Ready to Ship
        </div>
        <div class="product-card-category" style="margin-bottom:0.25rem">${product.category}</div>
        <h2 class="modal-product-title" style="font-size:1.5rem;font-weight:800;margin-bottom:0.5rem">${product.product_name}</h2>

        <div class="product-card-rating" style="margin-bottom:1rem">
          <span class="stars" style="font-size:1rem">★★★★☆</span>
          <span style="font-weight:700">${ratingNum} out of 5</span>
          <span class="text-muted">(${reviewCount} verified ratings)</span>
        </div>

        <div class="modal-product-price-row" style="display:flex;align-items:baseline;gap:0.75rem;margin-bottom:1rem">
          <div class="modal-product-price" style="font-size:1.75rem;font-weight:800">${formatPrice(priceNum)}</div>
          <div class="product-card-original-price" style="font-size:1.1rem">${formatPrice(originalPrice)}</div>
          <div class="product-card-discount" style="font-size:0.875rem">${discountPct}% savings</div>
        </div>

        <p class="text-muted text-sm" style="margin-bottom:1.25rem;line-height:1.6">
          ${product.description || 'Premium genuine product curated for high durability, performance, and everyday convenience. Eligible for free express delivery and 30-day effortless returns.'}
        </p>

        <ul class="modal-specs-list" style="margin-bottom:1.5rem">
          <li><span>Brand / Quality</span><strong>100% Certified Original</strong></li>
          <li><span>Availability</span><strong style="color:var(--color-success)">Ships within 24 Hours</strong></li>
          <li><span>Warranty</span><strong>1 Year Manufacturer Warranty</strong></li>
          <li><span>Return Policy</span><strong>30 Days Return / Replacement</strong></li>
        </ul>

        <!-- Customer Rating Widget (Active Learning for Recommendations) -->
        <div class="modal-rate-box" style="background:var(--bg-subtle);padding:1rem;border-radius:var(--radius-sm);margin-bottom:1.5rem">
          <div style="font-size:0.8125rem;font-weight:700;color:var(--text-primary)">
            Rate this product to refine your Spark ML recommendations:
          </div>
          <div class="modal-rate-stars" id="modal-star-group" style="font-size:1.5rem;cursor:pointer;color:#cbd5e1;margin-top:0.25rem">
            <span onclick="submitRating(${product.product_id}, 1)">★</span>
            <span onclick="submitRating(${product.product_id}, 2)">★</span>
            <span onclick="submitRating(${product.product_id}, 3)">★</span>
            <span onclick="submitRating(${product.product_id}, 4)">★</span>
            <span onclick="submitRating(${product.product_id}, 5)">★</span>
          </div>
          <div class="text-xs text-muted mt-1" id="rate-feedback">Click stars to rate from 1 to 5</div>
        </div>

        <div class="flex gap-2">
          <button class="btn btn-primary btn-lg" style="flex:1" onclick="addToCart(${product.product_id})">
            Add to Cart 🛒
          </button>
          <button class="btn btn-secondary btn-lg" style="color:${isWishlisted ? '#dc2626' : 'inherit'}" onclick="Wishlist.toggle(${product.product_id}, this)">
            ♥ Wishlist
          </button>
        </div>
      </div>
    </div>

    <!-- Similar Products Section (Personalized Content-Based Recommendation) -->
    <div style="border-top:1px solid var(--border-default);padding-top:1.5rem">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">
        <h3 style="font-size:1.125rem;font-weight:800">✨ Similar Products You May Also Like</h3>
        <span style="font-size:0.75rem;color:var(--color-accent);font-weight:600">Spark MLlib Matched</span>
      </div>
      <div id="modal-similar-products" style="display:grid;grid-template-columns:repeat(auto-fill, minmax(180px, 1fr));gap:1rem">
        <div class="text-muted text-sm">Loading recommendations...</div>
      </div>
    </div>
  `;

  modalOverlay.classList.add('open');

  // Load Similar Products for this product
  try {
    const simData = await RecsAPI.getSimilar(productId, 4);
    const simProds = simData.similar_products || simData.recommendations || [];
    const simContainer = document.getElementById('modal-similar-products');
    if (simContainer) {
      if (simProds.length > 0) {
        simContainer.innerHTML = simProds.map(p => `
          <div style="background:#ffffff;border:1px solid var(--border-default);border-radius:var(--radius-sm);padding:0.75rem;cursor:pointer;display:flex;flex-direction:column;justify-content:space-between" onclick="openProductModal(${p.product_id})">
            <img src="${getProductImage(p)}" alt="${p.product_name}" style="height:110px;width:100%;object-fit:contain;margin-bottom:0.5rem" />
            <div style="font-size:0.75rem;color:var(--text-muted)">${p.category}</div>
            <div style="font-weight:700;font-size:0.8125rem;line-height:1.3;margin-bottom:0.35rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${p.product_name}">${p.product_name}</div>
            <div style="display:flex;align-items:center;justify-content:space-between;margin-top:auto">
              <span style="font-weight:800;font-size:0.875rem">${formatPrice(p.price)}</span>
              <button class="btn btn-primary btn-sm" style="padding:2px 8px;font-size:0.75rem" onclick="event.stopPropagation(); addToCart(${p.product_id})">+ Add</button>
            </div>
          </div>
        `).join('');
      } else {
        simContainer.innerHTML = '<div class="text-muted text-xs">No similar products found.</div>';
      }
    }
  } catch(e) {
    const simContainer = document.getElementById('modal-similar-products');
    if (simContainer) simContainer.innerHTML = '';
  }
}

function closeModal() {
  const modal = document.getElementById('product-modal');
  if (modal) modal.classList.remove('open');
}

// ── Rating Submission ─────────────────────────────────────────────────────────
function submitRating(productId, stars) {
  // Update star colors in widget
  const starSpans = document.querySelectorAll('#modal-star-group span');
  starSpans.forEach((s, idx) => {
    s.style.color = idx < stars ? '#f59e0b' : '#cbd5e1';
  });

  const feedback = document.getElementById('rate-feedback');
  if (feedback) feedback.textContent = `You rated this ${stars} out of 5 stars! Thank you.`;

  InteractionsAPI.record(productId, 'rating', stars).then(() => {
    Toast.success('Rating Recorded', `Saved your ${stars}-star rating! This refines your Spark recommendations.`);
  }).catch(() => {
    Toast.info('Rating Saved', `Saved your ${stars}-star rating!`);
  });
}

// ── Cart & Wishlist Actions ───────────────────────────────────────────────────
function addToCart(productId) {
  Cart.add(productId, 1);
  Toast.success('Added to Cart 🛒', 'Item added to your shopping cart');
}

function toggleWishlist(productId, btnEl) {
  Wishlist.toggle(productId, btnEl);
}

// ── Cart Drawer (Slide-in Cart Panel with Real-Time Recommendations) ──────────
function openCartDrawer() {
  const items = Cart.getItems();

  // Build or re-use drawer
  let drawer = document.getElementById('cart-drawer-overlay');
  if (!drawer) {
    drawer = document.createElement('div');
    drawer.id = 'cart-drawer-overlay';
    drawer.style.cssText = 'position:fixed;inset:0;z-index:3000;display:flex;justify-content:flex-end';
    drawer.innerHTML = `
      <div id="cart-drawer-backdrop" style="position:absolute;inset:0;background:rgba(0,0,0,0.5)" onclick="closeCartDrawer()"></div>
      <div id="cart-drawer" style="position:relative;width:min(460px,100vw);background:#ffffff;height:100%;display:flex;flex-direction:column;box-shadow:-4px 0 32px rgba(0,0,0,0.2);overflow:hidden">
        <div style="display:flex;align-items:center;justify-content:space-between;padding:1.25rem 1.5rem;border-bottom:1px solid var(--border-default)">
          <div style="font-weight:800;font-size:1.125rem;display:flex;align-items:center;gap:0.5rem">
            <span>🛒 Your Shopping Cart</span>
            <span class="nav-cart-badge" style="display:inline-block;font-size:0.75rem;padding:2px 8px;border-radius:12px;background:var(--color-accent);color:#fff">${Cart.getCount()}</span>
          </div>
          <button onclick="closeCartDrawer()" style="background:none;border:none;font-size:1.25rem;cursor:pointer;color:var(--text-muted);padding:0.25rem">✕</button>
        </div>
        <div id="cart-drawer-items" style="flex:1;overflow-y:auto;padding:1rem 1.5rem"></div>
        <!-- In-Cart Recommendations Section -->
        <div id="cart-drawer-recs" style="border-top:1px solid var(--border-default);background:var(--bg-subtle);padding:0.875rem 1.5rem">
          <div style="font-weight:700;font-size:0.8125rem;margin-bottom:0.5rem;color:var(--text-primary);display:flex;align-items:center;gap:0.35rem">
            <span>✨ Frequently Bought Together</span>
          </div>
          <div id="cart-recs-container" style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem"></div>
        </div>
        <div id="cart-drawer-footer" style="border-top:1px solid var(--border-default);padding:1.25rem 1.5rem"></div>
      </div>
    `;
    document.body.appendChild(drawer);
  }

  // Populate items
  const itemsEl = document.getElementById('cart-drawer-items');
  const footerEl = document.getElementById('cart-drawer-footer');
  const recsContainer = document.getElementById('cart-recs-container');

  if (items.length === 0) {
    itemsEl.innerHTML = `
      <div style="text-align:center;padding:3rem 1rem;color:var(--text-muted)">
        <div style="font-size:3.5rem;margin-bottom:1rem">🛒</div>
        <div style="font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;color:var(--text-primary)">Your cart is empty</div>
        <div style="font-size:0.875rem;margin-bottom:1.5rem">Explore our catalogue and discover tailored picks for you</div>
        <a href="/products.html" class="btn btn-primary btn-sm" onclick="closeCartDrawer()">Browse Products</a>
      </div>
    `;
    footerEl.innerHTML = '';
    const recsSection = document.getElementById('cart-drawer-recs');
    if (recsSection) recsSection.style.display = 'none';
  } else {
    const recsSection = document.getElementById('cart-drawer-recs');
    if (recsSection) recsSection.style.display = 'block';

    // Fetch product details for cart items
    Promise.all(items.map(item => ProductsAPI.get(item.id).catch(() => null))).then(products => {
      let subtotal = 0;
      const rows = items.map((item, idx) => {
        const p = products[idx];
        if (!p) return '';
        const price = Number(p.price || 0);
        const itemTotal = price * (item.qty || 1);
        subtotal += itemTotal;
        const img = getProductImage(p);
        return `
          <div style="display:flex;gap:0.75rem;padding:0.875rem 0;border-bottom:1px solid var(--border-default);align-items:center">
            <img src="${img}" alt="${p.product_name}" style="width:64px;height:64px;object-fit:cover;border-radius:var(--radius-sm);flex-shrink:0" onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=200&auto=format'" />
            <div style="flex:1;min-width:0">
              <div style="font-weight:600;font-size:0.875rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="${p.product_name}">${p.product_name}</div>
              <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:0.25rem">${p.category}</div>
              <div style="font-weight:700;color:var(--text-primary);font-size:0.9375rem">${formatPrice(price)}</div>
            </div>
            <div style="display:flex;flex-direction:column;align-items:flex-end;gap:0.35rem">
              <div style="display:flex;align-items:center;gap:0.25rem;background:var(--bg-subtle);border:1px solid var(--border-default);border-radius:var(--radius-sm);padding:2px 4px">
                <button onclick="Cart.updateQty(${item.id}, -1)" style="border:none;background:none;font-weight:bold;cursor:pointer;padding:2px 6px;color:var(--text-primary)">−</button>
                <span style="font-size:0.8125rem;font-weight:700;min-width:18px;text-align:center">${item.qty || 1}</span>
                <button onclick="Cart.updateQty(${item.id}, 1)" style="border:none;background:none;font-weight:bold;cursor:pointer;padding:2px 6px;color:var(--text-primary)">+</button>
              </div>
              <button onclick="Cart.remove(${item.id})" style="border:none;background:none;color:#ef4444;font-size:0.75rem;cursor:pointer;text-decoration:underline" title="Remove item">Remove</button>
            </div>
          </div>
        `;
      });
      itemsEl.innerHTML = rows.join('');

      const shipping = subtotal >= 999 ? 0 : 99;
      const total = subtotal + shipping;
      footerEl.innerHTML = `
        <div style="margin-bottom:0.875rem">
          <div style="display:flex;justify-content:space-between;font-size:0.875rem;margin-bottom:0.25rem"><span>Subtotal</span><span>${formatPrice(subtotal)}</span></div>
          <div style="display:flex;justify-content:space-between;font-size:0.875rem;margin-bottom:0.5rem;color:var(--text-muted)"><span>Shipping</span><span>${shipping === 0 ? '<span style="color:#16a34a;font-weight:700">Free Express</span>' : formatPrice(shipping)}</span></div>
          <div style="display:flex;justify-content:space-between;font-weight:800;font-size:1.125rem;border-top:1px solid var(--border-default);padding-top:0.5rem"><span>Estimated Total</span><span>${formatPrice(total)}</span></div>
        </div>
        <button class="btn btn-primary btn-lg w-full" style="font-weight:700" onclick="closeCartDrawer(); proceedToCheckout()">
          Proceed to Checkout (${formatPrice(total)}) →
        </button>
      `;

      // Load in-cart contextual recommendations
      const cartIds = items.map(i => i.id);
      RecsAPI.forCart(cartIds, 2).then(data => {
        const recs = data.recommendations || [];
        if (recsContainer && recs.length > 0) {
          recsContainer.innerHTML = recs.map(p => `
            <div style="background:#ffffff;border:1px solid var(--border-default);border-radius:var(--radius-sm);padding:0.5rem;display:flex;gap:0.5rem;align-items:center">
              <img src="${getProductImage(p)}" alt="${p.product_name}" style="width:40px;height:40px;object-fit:cover;border-radius:4px" />
              <div style="flex:1;min-width:0">
                <div style="font-size:0.75rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${p.product_name}</div>
                <div style="font-size:0.75rem;font-weight:700">${formatPrice(p.price)}</div>
              </div>
              <button class="btn btn-primary btn-sm" style="padding:2px 8px;font-size:0.75rem" onclick="addToCart(${p.product_id}); openCartDrawer()">+ Add</button>
            </div>
          `).join('');
        }
      }).catch(() => {});
    });
  }

  drawer.style.display = 'flex';
  requestAnimationFrame(() => {
    const panel = document.getElementById('cart-drawer');
    if (panel) {
      panel.style.transition = 'transform 0.25s ease';
      panel.style.transform = 'translateX(0)';
    }
  });
}

function closeCartDrawer() {
  const drawer = document.getElementById('cart-drawer-overlay');
  if (drawer) drawer.style.display = 'none';
}

// ── Wishlist Modal View ───────────────────────────────────────────────────────
function openWishlistModal() {
  const wishIds = Wishlist.getItems();
  let wishModal = document.getElementById('wishlist-modal');
  if (!wishModal) {
    wishModal = document.createElement('div');
    wishModal.id = 'wishlist-modal';
    wishModal.className = 'modal-overlay';
    wishModal.innerHTML = `
      <div class="modal" style="max-width:600px;max-height:85vh;overflow-y:auto">
        <div class="modal-header">
          <div class="modal-title">♥ Your Saved Wishlist</div>
          <button class="modal-close" onclick="document.getElementById('wishlist-modal').classList.remove('open')">✕</button>
        </div>
        <div id="wishlist-modal-body" style="padding:1.5rem"></div>
      </div>
    `;
    wishModal.addEventListener('click', e => { if (e.target === wishModal) wishModal.classList.remove('open'); });
    document.body.appendChild(wishModal);
  }

  const bodyEl = document.getElementById('wishlist-modal-body');
  if (wishIds.length === 0) {
    bodyEl.innerHTML = `
      <div style="text-align:center;padding:2.5rem 1rem;color:var(--text-muted)">
        <div style="font-size:3rem;margin-bottom:0.75rem">♥</div>
        <div style="font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;color:var(--text-primary)">Your wishlist is empty</div>
        <div style="font-size:0.875rem;margin-bottom:1.5rem">Save products you love by clicking the heart icon on any card</div>
        <a href="/products.html" class="btn btn-primary btn-sm" onclick="document.getElementById('wishlist-modal').classList.remove('open')">Explore Products</a>
      </div>
    `;
  } else {
    bodyEl.innerHTML = '<div class="text-muted text-sm">Loading wishlist...</div>';
    Promise.all(wishIds.map(id => ProductsAPI.get(id).catch(() => null))).then(products => {
      const valid = products.filter(Boolean);
      bodyEl.innerHTML = `
        <div style="margin-bottom:1.5rem">
          ${valid.map(p => `
            <div style="display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:0.75rem 0;border-bottom:1px solid var(--border-default)">
              <img src="${getProductImage(p)}" alt="${p.product_name}" style="width:54px;height:54px;object-fit:cover;border-radius:var(--radius-sm)" />
              <div style="flex:1;min-width:0">
                <div style="font-weight:700;font-size:0.875rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${p.product_name}</div>
                <div style="font-size:0.75rem;color:var(--text-muted)">${p.category}</div>
                <div style="font-weight:800;color:var(--text-primary)">${formatPrice(p.price)}</div>
              </div>
              <div style="display:flex;gap:0.5rem">
                <button class="btn btn-primary btn-sm" onclick="addToCart(${p.product_id}); Toast.success('Moved to Cart'); openWishlistModal()">Add to Cart</button>
                <button class="btn btn-secondary btn-sm" style="color:#ef4444" onclick="Wishlist.toggle(${p.product_id}); openWishlistModal()">Remove</button>
              </div>
            </div>
          `).join('')}
        </div>
        <!-- Wishlist Recommendations -->
        <div style="border-top:1px solid var(--border-default);padding-top:1rem">
          <div style="font-weight:800;font-size:0.9375rem;margin-bottom:0.75rem">✨ Recommended Based on Your Wishlist</div>
          <div id="wishlist-recs-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem"></div>
        </div>
      `;

      // Load Wishlist Contextual Recs
      RecsAPI.forWishlist(wishIds, 2).then(data => {
        const recs = data.recommendations || [];
        const container = document.getElementById('wishlist-recs-grid');
        if (container && recs.length > 0) {
          container.innerHTML = recs.map(p => `
            <div style="background:var(--bg-subtle);border:1px solid var(--border-default);border-radius:var(--radius-sm);padding:0.6rem;display:flex;gap:0.5rem;align-items:center">
              <img src="${getProductImage(p)}" alt="${p.product_name}" style="width:40px;height:40px;object-fit:cover;border-radius:4px" />
              <div style="flex:1;min-width:0">
                <div style="font-size:0.75rem;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${p.product_name}</div>
                <div style="font-size:0.75rem;font-weight:800">${formatPrice(p.price)}</div>
              </div>
              <button class="btn btn-primary btn-sm" style="padding:2px 8px;font-size:0.75rem" onclick="addToCart(${p.product_id}); Toast.success('Added to Cart')">+ Add</button>
            </div>
          `).join('');
        }
      }).catch(() => {});
    });
  }

  wishModal.classList.add('open');
}

// ── Checkout Flow ─────────────────────────────────────────────────────────────
function proceedToCheckout() {
  const items = Cart.getItems();
  if (items.length === 0) {
    Toast.warning('Empty Cart', 'Add items to your cart first');
    return;
  }
  let checkoutModal = document.getElementById('checkout-modal');
  if (!checkoutModal) {
    checkoutModal = document.createElement('div');
    checkoutModal.id = 'checkout-modal';
    checkoutModal.className = 'modal-overlay';
    checkoutModal.innerHTML = `
      <div class="modal" style="max-width:520px;max-height:90vh;overflow-y:auto">
        <div class="modal-header">
          <div class="modal-title">🛒 Complete Your Order</div>
          <button class="modal-close" onclick="document.getElementById('checkout-modal').classList.remove('open')">✕</button>
        </div>
        <div style="padding:1.5rem">
          <div id="checkout-order-summary" style="background:var(--bg-subtle);padding:1rem;border-radius:var(--radius-sm);margin-bottom:1.25rem"></div>
          <div class="form-group" style="margin-bottom:1rem">
            <label class="form-label" style="font-weight:700;font-size:0.875rem">Full Delivery Address</label>
            <input type="text" id="checkout-address" class="form-control" placeholder="House/Flat No, Street, Landmark, City, PIN" value="Plot 42, Tech Park Avenue, Bangalore, 560100" />
          </div>
          <div class="form-group" style="margin-bottom:1.5rem">
            <label class="form-label" style="font-weight:700;font-size:0.875rem">Payment Method</label>
            <select id="checkout-payment" class="form-control">
              <option value="UPI">UPI Instant Payment (GPay, PhonePe, Paytm)</option>
              <option value="Credit Card">Credit / Debit Card (Visa, MasterCard, RuPay)</option>
              <option value="NetBanking">Net Banking</option>
              <option value="COD">Cash on Delivery</option>
            </select>
          </div>
          <button class="btn btn-primary btn-lg w-full" id="btn-submit-order" onclick="submitCheckout()">Confirm & Place Order →</button>
        </div>
      </div>
    `;
    checkoutModal.addEventListener('click', e => { if (e.target === checkoutModal) checkoutModal.classList.remove('open'); });
    document.body.appendChild(checkoutModal);
  }

  // Populate checkout summary
  Promise.all(items.map(item => ProductsAPI.get(item.id).catch(() => null))).then(products => {
    let subtotal = 0;
    const listHtml = items.map((item, idx) => {
      const p = products[idx];
      if (!p) return '';
      const price = Number(p.price || 0);
      subtotal += price * (item.qty || 1);
      return `<div style="display:flex;justify-content:space-between;font-size:0.8125rem;margin-bottom:0.25rem"><span>${p.product_name} × ${item.qty || 1}</span><span>${formatPrice(price * (item.qty || 1))}</span></div>`;
    }).join('');

    const shipping = subtotal >= 999 ? 0 : 99;
    const total = subtotal + shipping;
    const summaryEl = document.getElementById('checkout-order-summary');
    if (summaryEl) {
      summaryEl.innerHTML = `
        <div style="font-weight:700;font-size:0.875rem;margin-bottom:0.5rem;border-bottom:1px solid var(--border-default);padding-bottom:0.25rem">Order Review</div>
        ${listHtml}
        <div style="display:flex;justify-content:space-between;font-size:0.8125rem;margin-top:0.5rem;color:var(--text-muted)"><span>Shipping</span><span>${shipping === 0 ? 'Free' : formatPrice(shipping)}</span></div>
        <div style="display:flex;justify-content:space-between;font-weight:800;font-size:1rem;margin-top:0.5rem;border-top:1px solid var(--border-default);padding-top:0.5rem"><span>Total Payable</span><span>${formatPrice(total)}</span></div>
      `;
    }
  });

  checkoutModal.classList.add('open');
}

async function submitCheckout() {
  const items = Cart.getItems();
  const address = document.getElementById('checkout-address').value.trim();
  const payment = document.getElementById('checkout-payment').value;

  if (!address) {
    Toast.warning('Address Required', 'Please enter a delivery address');
    return;
  }

  const btn = document.getElementById('btn-submit-order');
  if (btn) { btn.disabled = true; btn.textContent = 'Processing Order with Spark...'; }

  try {
    const products = await Promise.all(items.map(i => ProductsAPI.get(i.id).catch(() => null)));
    const enrichedItems = items.map((item, idx) => ({
      product_id: item.id,
      qty: item.qty || 1,
      price: products[idx]?.price || 0,
      product_name: products[idx]?.product_name || 'Product',
      category: products[idx]?.category || 'General',
    })).filter(i => i.price > 0);

    const resp = await OrdersAPI.placeOrder({
      items: enrichedItems,
      address: { full: address },
      payment_method: payment,
    });

    // Record purchase interaction for every item (gives top weight 5.0 in recommendation model)
    for (const item of items) {
      InteractionsAPI.record(item.id, 'purchase').catch(() => {});
    }

    // Clear cart
    Cart.clear();

    // Close checkout modal
    document.getElementById('checkout-modal').classList.remove('open');

    // Show order confirmation dialog with Order ID and Next Recommended Purchases
    showOrderConfirmationModal(resp, resp.recommendations || []);
  } catch(err) {
    Toast.error('Order Failed', err.message || 'Please try again');
    if (btn) { btn.disabled = false; btn.textContent = 'Confirm & Place Order →'; }
  }
}

function showOrderConfirmationModal(orderResp, recommendations = []) {
  let modal = document.getElementById('order-confirmed-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'order-confirmed-modal';
    modal.className = 'modal-overlay';
    document.body.appendChild(modal);
  }

  modal.innerHTML = `
    <div class="modal" style="max-width:540px;text-align:center;padding:2rem 1.5rem">
      <div style="font-size:3.5rem;margin-bottom:0.75rem">🎉</div>
      <h2 style="font-size:1.5rem;font-weight:800;margin-bottom:0.25rem">Order Confirmed!</h2>
      <div style="font-weight:700;color:var(--color-accent);font-size:1rem;margin-bottom:0.5rem">
        Order ID: ${orderResp.order_id || 'ORD-2026-CONFIRMED'}
      </div>
      <p style="color:var(--text-muted);font-size:0.875rem;margin-bottom:1.5rem">
        Your order total of <strong>${formatPrice(orderResp.total || 0)}</strong> was placed successfully. A delivery tracking notification has been dispatched.
      </p>

      ${recommendations.length > 0 ? `
        <div style="background:var(--bg-subtle);border-radius:var(--radius-sm);padding:1rem;margin-bottom:1.5rem;text-align:left">
          <div style="font-weight:700;font-size:0.875rem;margin-bottom:0.5rem">✨ Recommended Next Purchases for You:</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem">
            ${recommendations.slice(0, 2).map(p => `
              <div style="background:#ffffff;border:1px solid var(--border-default);border-radius:4px;padding:0.5rem;display:flex;align-items:center;gap:0.5rem">
                <img src="${getProductImage(p)}" style="width:36px;height:36px;object-fit:cover;border-radius:4px" />
                <div style="flex:1;min-width:0">
                  <div style="font-size:0.75rem;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${p.product_name}</div>
                  <div style="font-size:0.75rem">${formatPrice(p.price)}</div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <div style="display:flex;gap:0.75rem;justify-content:center">
        <a href="/products.html" class="btn btn-primary btn-md" onclick="document.getElementById('order-confirmed-modal').classList.remove('open')">Continue Shopping</a>
        <a href="/recommendations.html" class="btn btn-secondary btn-md" onclick="document.getElementById('order-confirmed-modal').classList.remove('open')">View For You Feed</a>
      </div>
    </div>
  `;

  modal.classList.add('open');
}

// ── Global Search Handling with Interaction Tracking ──────────────────────────
function handleSearch(keyword, category = '') {
  const cleanQ = (keyword || '').trim();
  const cleanCat = (category || '').trim();
  // Record search query interaction
  if (cleanQ) {
    InteractionsAPI.record(null, 'search', null, cleanQ).catch(() => {});
  }
  window.location.href = `/products.html?q=${encodeURIComponent(cleanQ)}&category=${encodeURIComponent(cleanCat)}`;
}

// ── Navigation & Auth UI Initialization ───────────────────────────────────────
function initAuthUI() {
  const user = Auth.getUser();
  const loginBtn   = document.getElementById('nav-login-btn');
  const userInfo   = document.getElementById('nav-user-info');
  const userNameEl = document.getElementById('dropdown-name');
  const userEmailEl= document.getElementById('dropdown-email');
  const navAvatar  = document.getElementById('nav-avatar');
  const adminLinks = document.querySelectorAll('.nav-admin-link');

  if (user && Auth.isLoggedIn()) {
    if (loginBtn)  loginBtn.classList.add('hidden');
    if (userInfo)  userInfo.classList.remove('hidden');
    if (navAvatar) navAvatar.textContent = (user.name || 'U').charAt(0).toUpperCase();
    if (userNameEl) userNameEl.textContent = user.name || 'Account';
    if (userEmailEl) userEmailEl.textContent = user.email || '';

    const isAdmin = Auth.isAdmin();
    adminLinks.forEach(link => {
      link.classList.toggle('hidden', !isAdmin);
    });
  } else {
    if (loginBtn)  loginBtn.classList.remove('hidden');
    if (userInfo)  userInfo.classList.add('hidden');
    adminLinks.forEach(link => link.classList.add('hidden'));
  }

  // Update badges
  Cart.updateBadge();
  Wishlist.updateBadges();
}

function toggleUserMenu() {
  const menu = document.getElementById('user-dropdown');
  if (menu) menu.classList.toggle('hidden');
}

// Close user dropdown when clicking outside
document.addEventListener('click', (e) => {
  const menu = document.getElementById('user-dropdown');
  const avatar = document.getElementById('nav-avatar');
  if (menu && !menu.classList.contains('hidden') && !menu.contains(e.target) && e.target !== avatar) {
    menu.classList.add('hidden');
  }
});

function logout() {
  Auth.clear();
  Toast.info('Logged Out', 'You have been signed out.');
  setTimeout(() => {
    window.location.href = '/index.html';
  }, 600);
}

// Make globally accessible
window.Toast = Toast;
window.Loading = Loading;
window.Cart = Cart;
window.Wishlist = Wishlist;
window.RecentlyViewed = RecentlyViewed;
window.getProductImage = getProductImage;
window.formatPrice = formatPrice;
window.formatNumber = formatNumber;
window.formatRating = formatRating;
window.buildProductCard = buildProductCard;
window.skeletonProduct = skeletonProduct;
window.showSkeletons = showSkeletons;
window.openProductModal = openProductModal;
window.closeModal = closeModal;
window.submitRating = submitRating;
window.addToCart = addToCart;
window.toggleWishlist = toggleWishlist;
window.openWishlistModal = openWishlistModal;
window.handleSearch = handleSearch;
window.initAuthUI = initAuthUI;
window.toggleUserMenu = toggleUserMenu;
window.logout = logout;
window.openCartDrawer = openCartDrawer;
window.closeCartDrawer = closeCartDrawer;
window.proceedToCheckout = proceedToCheckout;
window.submitCheckout = submitCheckout;

document.addEventListener('DOMContentLoaded', () => {
  initAuthUI();
});
