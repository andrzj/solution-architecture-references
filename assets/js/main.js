/* ============================================================
   SA References — Main JavaScript
   ============================================================ */

/* 1. Theme Toggle
   ============================================================ */
const THEME_KEY = 'sa-refs-theme';

function getPreferredTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored) return stored;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  setTheme(current === 'dark' ? 'light' : 'dark');
}

// Apply theme immediately to prevent flash
(function() {
  setTheme(getPreferredTheme());
})();

/* 2. Mobile Sidebar
   ============================================================ */
function initSidebar() {
  const hamburger = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');

  if (!hamburger || !sidebar) return;

  hamburger.addEventListener('click', () => {
    const isOpen = sidebar.classList.contains('open');
    sidebar.classList.toggle('open');
    overlay?.classList.toggle('visible');
    hamburger.setAttribute('aria-expanded', String(!isOpen));
  });

  overlay?.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.classList.remove('visible');
    hamburger.setAttribute('aria-expanded', 'false');
  });

  // Close on ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && sidebar.classList.contains('open')) {
      sidebar.classList.remove('open');
      overlay?.classList.remove('visible');
      hamburger.setAttribute('aria-expanded', 'false');
      hamburger.focus();
    }
  });

  // Close on link click (mobile)
  sidebar.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth <= 900) {
        sidebar.classList.remove('open');
        overlay?.classList.remove('visible');
      }
    });
  });
}

/* 3. Active Sidebar Link
   ============================================================ */
function highlightActiveSidebarLink() {
  const currentPath = window.location.pathname.replace(/\/$/, '') || '/';
  const links = document.querySelectorAll('.sidebar__link');

  links.forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    // Resolve relative URL
    const url = new URL(href, window.location.href);
    const linkPath = url.pathname.replace(/\/$/, '') || '/';

    if (linkPath === currentPath || (currentPath.endsWith('/index.html') && linkPath === currentPath.replace('/index.html', ''))) {
      link.classList.add('active');
      // Scroll into view
      link.scrollIntoView({ block: 'nearest' });
    } else {
      link.classList.remove('active');
    }
  });
}

/* 4. Reading Progress Bar
   ============================================================ */
function initReadingProgress() {
  const bar = document.getElementById('readingProgress');
  if (!bar) return;

  function updateProgress() {
    const docHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    if (docHeight <= 0) return;
    const scrolled = window.scrollY / docHeight;
    bar.style.width = Math.min(100, Math.round(scrolled * 100)) + '%';
  }

  window.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();
}

/* 5. Table of Contents — Active Highlight
   ============================================================ */
function initTocHighlight() {
  const toc = document.querySelector('.toc__list');
  if (!toc) return;

  const headings = document.querySelectorAll('.article-content h2, .article-content h3');
  if (!headings.length) return;

  const tocLinks = toc.querySelectorAll('a');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        tocLinks.forEach(link => link.classList.remove('active'));
        const id = entry.target.id;
        const active = toc.querySelector(`a[href="#${id}"]`);
        if (active) active.classList.add('active');
      }
    });
  }, { rootMargin: '-20px 0px -70% 0px' });

  headings.forEach(h => {
    if (h.id) observer.observe(h);
  });
}

/* 6. Search
   ============================================================ */
// Search index — all articles
const SEARCH_INDEX = [
  // Foundations
  { title: 'Architecture Principles', path: 'foundations/architecture-principles.html', section: 'Foundations' },
  { title: 'Quality Attributes & NFRs', path: 'foundations/quality-attributes.html', section: 'Foundations' },
  { title: 'Trade-off Analysis', path: 'foundations/tradeoff-analysis.html', section: 'Foundations' },
  { title: 'Architecture Decision Records (ADR)', path: 'foundations/architecture-decision-records.html', section: 'Foundations' },
  { title: 'Reference Architectures', path: 'foundations/reference-architectures.html', section: 'Foundations' },
  { title: 'Bounded Contexts', path: 'foundations/bounded-contexts.html', section: 'Foundations' },
  { title: 'Domain Modeling', path: 'foundations/domain-modeling.html', section: 'Foundations' },
  { title: 'CAP Theorem', path: 'foundations/cap-theorem.html', section: 'Foundations' },
  { title: 'PACELC Theorem', path: 'foundations/pacelc-theorem.html', section: 'Foundations' },
  { title: 'Eventual Consistency', path: 'foundations/eventual-consistency.html', section: 'Foundations' },
  { title: 'Idempotency', path: 'foundations/idempotency.html', section: 'Foundations' },
  { title: 'Backward Compatibility', path: 'foundations/backward-compatibility.html', section: 'Foundations' },
  // Architecture Styles
  { title: 'Monolith Architecture', path: 'architecture-styles/monolith.html', section: 'Architecture Styles' },
  { title: 'Modular Monolith', path: 'architecture-styles/modular-monolith.html', section: 'Architecture Styles' },
  { title: 'Microservices Architecture', path: 'architecture-styles/microservices.html', section: 'Architecture Styles' },
  { title: 'Service-Oriented Architecture (SOA)', path: 'architecture-styles/soa.html', section: 'Architecture Styles' },
  { title: 'Event-Driven Architecture', path: 'architecture-styles/event-driven-architecture.html', section: 'Architecture Styles' },
  { title: 'Hexagonal Architecture', path: 'architecture-styles/hexagonal-architecture.html', section: 'Architecture Styles' },
  { title: 'Clean Architecture', path: 'architecture-styles/clean-architecture.html', section: 'Architecture Styles' },
  { title: 'CQRS Pattern', path: 'architecture-styles/cqrs.html', section: 'Architecture Styles' },
  { title: 'Event Sourcing', path: 'architecture-styles/event-sourcing.html', section: 'Architecture Styles' },
  { title: 'Serverless Architecture', path: 'architecture-styles/serverless.html', section: 'Architecture Styles' },
  // Distributed Systems
  { title: 'Distributed Transactions', path: 'distributed-systems/distributed-transactions.html', section: 'Distributed Systems' },
  { title: 'Saga Pattern', path: 'distributed-systems/saga-pattern.html', section: 'Distributed Systems' },
  { title: 'Compensating Transactions', path: 'distributed-systems/compensating-transactions.html', section: 'Distributed Systems' },
  { title: 'Consensus Algorithms', path: 'distributed-systems/consensus-algorithms.html', section: 'Distributed Systems' },
  { title: 'Leader Election', path: 'distributed-systems/leader-election.html', section: 'Distributed Systems' },
  { title: 'Distributed Locking', path: 'distributed-systems/distributed-locking.html', section: 'Distributed Systems' },
  // Communication Patterns
  { title: 'Request-Response', path: 'communication-patterns/request-response.html', section: 'Communication Patterns' },
  { title: 'Pub/Sub', path: 'communication-patterns/pub-sub.html', section: 'Communication Patterns' },
  { title: 'Message Queues', path: 'communication-patterns/message-queues.html', section: 'Communication Patterns' },
  { title: 'Event Streaming', path: 'communication-patterns/event-streaming.html', section: 'Communication Patterns' },
  { title: 'Webhooks', path: 'communication-patterns/webhooks.html', section: 'Communication Patterns' },
  { title: 'Transactional Outbox', path: 'communication-patterns/transactional-outbox.html', section: 'Communication Patterns' },
  // Reliability
  { title: 'Retry Pattern', path: 'reliability/retry-pattern.html', section: 'Reliability & Resilience' },
  { title: 'Circuit Breaker', path: 'reliability/circuit-breaker.html', section: 'Reliability & Resilience' },
  { title: 'Bulkhead Pattern', path: 'reliability/bulkhead-pattern.html', section: 'Reliability & Resilience' },
  { title: 'Fallback Pattern', path: 'reliability/fallback-pattern.html', section: 'Reliability & Resilience' },
  { title: 'Graceful Degradation', path: 'reliability/graceful-degradation.html', section: 'Reliability & Resilience' },
  { title: 'Dead Letter Queues', path: 'reliability/dead-letter-queues.html', section: 'Reliability & Resilience' },
  // Scalability
  { title: 'Horizontal Scaling', path: 'scalability/horizontal-scaling.html', section: 'Scalability & Performance' },
  { title: 'Caching Strategies', path: 'scalability/caching-strategies.html', section: 'Scalability & Performance' },
  { title: 'Sharding Strategies', path: 'scalability/sharding-strategies.html', section: 'Scalability & Performance' },
  { title: 'Rate Limiting', path: 'scalability/rate-limiting.html', section: 'Scalability & Performance' },
  { title: 'Cache Invalidation', path: 'scalability/cache-invalidation.html', section: 'Scalability & Performance' },
  // API Design
  { title: 'REST API Design', path: 'api-design/rest-api-design.html', section: 'API Design' },
  { title: 'GraphQL Architecture', path: 'api-design/graphql.html', section: 'API Design' },
  { title: 'gRPC Architecture', path: 'api-design/grpc.html', section: 'API Design' },
  { title: 'API Gateway Pattern', path: 'api-design/api-gateway.html', section: 'API Design' },
  { title: 'API Versioning', path: 'api-design/api-versioning.html', section: 'API Design' },
  // Security
  { title: 'Authentication Fundamentals', path: 'security/authentication.html', section: 'Security' },
  { title: 'Authorization Models', path: 'security/authorization-models.html', section: 'Security' },
  { title: 'Zero Trust Architecture', path: 'security/zero-trust.html', section: 'Security' },
  { title: 'OAuth2 & OpenID Connect', path: 'security/oauth2-openid-connect.html', section: 'Security' },
  { title: 'Secrets Management', path: 'security/secrets-management.html', section: 'Security' },
  // Observability
  { title: 'Distributed Tracing', path: 'observability/distributed-tracing.html', section: 'Observability' },
  { title: 'Logging Architecture', path: 'observability/logging-architecture.html', section: 'Observability' },
  { title: 'SLI/SLO/SLA', path: 'observability/sli-slo-sla.html', section: 'Observability' },
  // Deployment
  { title: 'CI/CD Pipelines', path: 'deployment/ci-cd-pipelines.html', section: 'Deployment & Delivery' },
  { title: 'Blue-Green Deployment', path: 'deployment/blue-green-deployment.html', section: 'Deployment & Delivery' },
  { title: 'Canary Releases', path: 'deployment/canary-releases.html', section: 'Deployment & Delivery' },
  // Cloud
  { title: 'Cloud-Native Architecture', path: 'cloud/cloud-native.html', section: 'Cloud Architecture' },
  { title: 'Landing Zones', path: 'cloud/landing-zones.html', section: 'Cloud Architecture' },
  { title: 'Multi-Region Architectures', path: 'cloud/multi-region.html', section: 'Cloud Architecture' },
  // Anti-Patterns
  { title: 'Distributed Monolith', path: 'anti-patterns/distributed-monolith.html', section: 'Anti-Patterns' },
  { title: 'Big Ball of Mud', path: 'anti-patterns/big-ball-of-mud.html', section: 'Anti-Patterns' },
  { title: 'Chatty Services', path: 'anti-patterns/chatty-services.html', section: 'Anti-Patterns' },
  // Decision Guides
  { title: 'SQL vs NoSQL', path: 'decision-guides/sql-vs-nosql.html', section: 'Decision Guides' },
  { title: 'REST vs GraphQL vs gRPC', path: 'decision-guides/rest-vs-graphql-vs-grpc.html', section: 'Decision Guides' },
  { title: 'Monolith vs Microservices', path: 'decision-guides/monolith-vs-microservices.html', section: 'Decision Guides' },
];

function getBasePath() {
  // Determine the root path relative to current page
  const depth = (window.location.pathname.match(/\//g) || []).length - 1;
  return '../'.repeat(Math.max(0, depth));
}

function initSearch(inputSelector, resultsSelector) {
  const input = document.querySelector(inputSelector);
  const results = document.querySelector(resultsSelector);
  if (!input || !results) return;

  const base = getBasePath();

  function renderResults(query) {
    if (!query || query.length < 2) {
      results.classList.remove('visible');
      return;
    }

    const q = query.toLowerCase();
    const matches = SEARCH_INDEX.filter(item =>
      item.title.toLowerCase().includes(q) ||
      item.section.toLowerCase().includes(q)
    ).slice(0, 8);

    results.innerHTML = '';
    if (matches.length === 0) {
      results.innerHTML = '<div class="search-empty">No results found</div>';
    } else {
      matches.forEach(item => {
        const a = document.createElement('a');
        a.className = 'search-result';
        a.href = base + item.path;
        a.innerHTML = `
          <div class="search-result__title">${item.title}</div>
          <div class="search-result__path">${item.section}</div>
        `;
        results.appendChild(a);
      });
    }
    results.classList.add('visible');
  }

  let debounceTimer;
  input.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => renderResults(input.value.trim()), 200);
  });

  input.addEventListener('focus', () => {
    if (input.value.trim().length >= 2) renderResults(input.value.trim());
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest(resultsSelector) && !e.target.closest(inputSelector)) {
      results.classList.remove('visible');
    }
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      results.classList.remove('visible');
      input.blur();
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      const first = results.querySelector('.search-result');
      first?.focus();
    }
  });

  // Keyboard nav within results
  results.addEventListener('keydown', (e) => {
    const items = results.querySelectorAll('.search-result');
    const current = document.activeElement;
    const idx = Array.from(items).indexOf(current);

    if (e.key === 'ArrowDown' && idx < items.length - 1) {
      e.preventDefault();
      items[idx + 1].focus();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (idx > 0) items[idx - 1].focus();
      else input.focus();
    } else if (e.key === 'Escape') {
      results.classList.remove('visible');
      input.focus();
    }
  });
}

/* 7. Copy Code Blocks
   ============================================================ */
function initCopyCode() {
  document.querySelectorAll('pre').forEach(pre => {
    const btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.textContent = 'Copy';
    btn.style.cssText = `
      position: absolute;
      top: 0.75rem;
      right: 0.75rem;
      padding: 0.25rem 0.75rem;
      font-size: 0.75rem;
      font-family: inherit;
      font-weight: 600;
      border-radius: var(--radius-sm);
      background: var(--bg-alt);
      color: var(--text-muted);
      border: 1px solid var(--border);
      cursor: pointer;
      transition: background 150ms, color 150ms;
    `;

    pre.style.position = 'relative';
    pre.appendChild(btn);

    btn.addEventListener('click', async () => {
      const code = pre.querySelector('code')?.textContent || pre.textContent;
      try {
        await navigator.clipboard.writeText(code);
        btn.textContent = 'Copied!';
        btn.style.color = 'var(--success)';
        setTimeout(() => {
          btn.textContent = 'Copy';
          btn.style.color = 'var(--text-muted)';
        }, 2000);
      } catch {
        btn.textContent = 'Error';
      }
    });
  });
}

/* 8. Auto-generate IDs for headings
   ============================================================ */
function slugify(text) {
  return text.toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim();
}

function initHeadingIds() {
  document.querySelectorAll('.article-content h2, .article-content h3').forEach(h => {
    if (!h.id) {
      h.id = slugify(h.textContent);
    }
  });
}

/* 9. Init all
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  // Theme button
  const themeBtn = document.getElementById('themeToggle');
  if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

  initSidebar();
  highlightActiveSidebarLink();
  initReadingProgress();
  initHeadingIds();
  initTocHighlight();
  initCopyCode();

  // Search in topnav
  initSearch('#topSearch', '#topSearchResults');
  // Search in hero
  initSearch('#heroSearch', '#heroSearchResults');
});
