(function() {
  console.log("SatyaCheck Guard content script active.");

  // Regular check interval to catch dynamic scrolls / infinite feeds
  setInterval(scanFeed, 1500);

  function scanFeed() {
    // Targets: Twitter/X tweets, YouTube comments, Telegram web, and our own simulated web dashboard feed posts
    const selectors = [
      '.simulated-post', 
      '[data-testid="tweetText"]', 
      '#content-text', 
      '.tgme_widget_message_text',
      '.post-text'
    ];
    
    selectors.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(element => {
        // Prevent double badging
        if (element.getAttribute('data-satyacheck-scanned') === 'true') {
          return;
        }
        element.setAttribute('data-satyacheck-scanned', 'true');
        
        const text = element.innerText || "";
        const lowerText = text.toLowerCase();
        
        let badgeHtml = null;
        
        if (lowerText.includes("guaranteed") && (lowerText.includes("return") || lowerText.includes("profit") || lowerText.includes("monthly"))) {
          badgeHtml = createBadge("UNAUTHORIZED", "SEBI rules prohibit promising guaranteed or risk-free returns to retail investors.");
        } 
        else if (lowerText.includes("reliance") && lowerText.includes("buyback") && (lowerText.includes("5,000") || lowerText.includes("5000"))) {
          badgeHtml = createBadge("PRICE MISMATCH", "Announced buyback price (Rs. 5,000) does not match official stock exchange filing FIL-2026-001 (Rs. 3,200).");
        }
        else if (lowerText.includes("sebi") && (lowerText.includes("penalty") || lowerText.includes("fee") || lowerText.includes("pay"))) {
          badgeHtml = createBadge("CRITICAL SCAM", "Demanding direct payments under SEBI name. SEBI never accepts fines via UPI or broker account.");
        }
        else if (lowerText.includes("stock tip") || lowerText.includes("telegram group") || lowerText.includes("jackpot")) {
          badgeHtml = createBadge("UNREGISTERED ADVICE", "Promoting advisory services without visible SEBI RIA registration validation.");
        }
        
        if (badgeHtml) {
          // Append the badge to the element
          const badgeContainer = document.createElement('div');
          badgeContainer.style.marginTop = '8px';
          badgeContainer.innerHTML = badgeHtml;
          element.appendChild(badgeContainer);
        }
      });
    });
  }

  function createBadge(type, reason) {
    const isCritical = type === "CRITICAL SCAM" || type === "PRICE MISMATCH";
    const bg = isCritical ? 'rgba(244, 63, 94, 0.12)' : 'rgba(245, 158, 11, 0.12)';
    const textCol = isCritical ? '#f43f5e' : '#f59e0b';
    const borderCol = isCritical ? 'rgba(244, 63, 94, 0.3)' : 'rgba(245, 158, 11, 0.3)';
    
    return `
      <div style="background: ${bg}; color: ${textCol}; border: 1px solid ${borderCol}; padding: 6px 10px; border-radius: 8px; font-size: 11px; font-weight: 500; display: inline-flex; flex-direction: column; gap: 2px; width: calc(100% - 20px); box-sizing: border-box; font-family: sans-serif;">
        <span style="font-weight: 700; uppercase; letter-spacing: 0.05em; font-size: 9px; display: flex; align-items: center; gap: 4px;">
          ⚠️ SatyaCheck Flag: [${type}]
        </span>
        <span style="color: #cbd5e1; font-size: 10px; line-height: 1.3;">
          ${reason}
        </span>
      </div>
    `;
  }
})();
