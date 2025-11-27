(function() {
  'use strict';


  const BACKEND_URL = 'http://localhost:8000';
  const WIDGET_ID = 'store-widget-banner';

  const currentScript = document.currentScript;
  const domain = currentScript?.getAttribute('data-domain') || window.location.hostname;
  

  async function fetchWidgetConfig() {
    try {
      console.log('[Widget] Fetching config for domain:', domain);
      
      const query = `
        query {
          getWidgetByDomain(domain: "${domain}") {
            id
            storeId
            domain
            videoUrl
            bannerText
            isActive
          }
        }
      `;

      const response = await fetch(`${BACKEND_URL}/graphql`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();
      
      if (data.errors) {
        console.error('[Widget] GraphQL error:', data.errors);
        return null;
      }

      const config = data.data?.getWidgetByDomain;
      console.log('[Widget] Config fetched:', config);
      return config;
    } catch (error) {
      console.error('[Widget] Error fetching config:', error);
      return null;
    }
  }

  async function trackEvent(storeId, domain, eventType) {
    try {
      console.log('[Widget] Tracking event:', { storeId, domain, eventType });
      
      const mutation = `
        mutation {
          trackEvent(
            storeId: "${storeId}"
            domain: "${domain}"
            eventType: "${eventType}"
            userAgent: "${navigator.userAgent}"
            ipAddress: ""
          )
        }
      `;

      const response = await fetch(`${BACKEND_URL}/graphql`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mutation }),
      });

      const data = await response.json();
      if (data.errors) {
        console.error('[Widget] Track error:', data.errors);
      }
    } catch (error) {
      console.error('[Widget] Error tracking event:', error);
    }
  }

  function injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
      #${WIDGET_ID} {
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: 300px;
        z-index: 9999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }

      .widget-banner {
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        overflow: hidden;
        cursor: pointer;
        transition: transform 0.2s;
      }

      .widget-banner:hover {
        transform: scale(1.05);
      }

      .widget-banner video {
        width: 100%;
        height: 180px;
        object-fit: cover;
        display: block;
      }

      .widget-banner-text {
        padding: 12px;
        text-align: center;
        font-weight: 600;
        font-size: 14px;
        color: #333;
        background: #f9f9f9;
      }

      .widget-close {
        position: absolute;
        top: 8px;
        right: 8px;
        background: rgba(0, 0, 0, 0.6);
        color: white;
        border: none;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
        z-index: 1;
      }

      .widget-close:hover {
        background: rgba(0, 0, 0, 0.8);
      }

      .widget-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.2s ease;
      }

      @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
      }

      .widget-iframe-container {
        position: relative;
        width: 90%;
        height: 90%;
        max-width: 1200px;
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
      }

      .widget-iframe-container iframe {
        width: 100%;
        height: 100%;
        border: none;
      }

      .widget-iframe-close {
        position: absolute;
        top: 12px;
        right: 12px;
        background: white;
        border: 2px solid #e0e0e0;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1;
        transition: all 0.2s;
      }

      .widget-iframe-close:hover {
        background: #f0f0f0;
        border-color: #999;
      }
    `;
    document.head.appendChild(style);
  }

  function renderBanner(config) {
    const container = document.createElement('div');
    container.id = WIDGET_ID;

    container.innerHTML = `
      <div class="widget-banner">
        <button class="widget-close">×</button>
        <video autoplay muted loop>
          <source src="${config.videoUrl}" type="video/mp4">
        </video>
        <div class="widget-banner-text">${config.bannerText || 'Click to learn more'}</div>
      </div>
    `;

    document.body.appendChild(container);

    const banner = container.querySelector('.widget-banner');
    const closeBtn = container.querySelector('.widget-close');
    const video = container.querySelector('video');

    video.addEventListener('loadeddata', () => {
      trackEvent(config.storeId, config.domain, 'video_loaded');
    });

    banner.addEventListener('click', (e) => {
      if (e.target === closeBtn) return;
      trackEvent(config.storeId, config.domain, 'link_clicked');
      showIFrame(config.videoUrl);  
    });

    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      container.remove();
    });
  }
  function showIFrame(url) {
    const overlay = document.createElement('div');
    overlay.className = 'widget-overlay';

    overlay.innerHTML = `
      <div class="widget-iframe-container">
        <button class="widget-iframe-close">×</button>
        <iframe src="${url}" title="Widget Content"></iframe>
      </div>
    `;

    document.body.appendChild(overlay);

    const closeBtn = overlay.querySelector('.widget-iframe-close');
    closeBtn.addEventListener('click', () => {
      overlay.remove();
    });

    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.remove();
      }
    });
  }

  async function init() {
    try {
      injectStyles();

      const config = await fetchWidgetConfig();

      if (!config) {
        console.warn('[Widget] No config returned');
        return;
      }

      if (!config.isActive) {
        console.warn('[Widget] Widget is not active');
        return;
      }

      trackEvent(config.storeId, config.domain, 'page_view');

      renderBanner(config);
    } catch (error) {
      console.error('[Widget] Initialization error:', error);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
