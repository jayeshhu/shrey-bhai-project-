/**
 * MediScan AI - Main JavaScript
 * Demonstrates: DOM manipulation, event handling, AJAX, async/await,
 *               animations, drag-and-drop, form validation
 */

// ─────────────────────────────────────────────────────────────
// Flash Message Auto-dismiss
// ─────────────────────────────────────────────────────────────
function initFlashMessages() {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach((flash, index) => {
    // Stagger auto-dismiss
    setTimeout(() => {
      dismissFlash(flash);
    }, 5000 + index * 500);

    const closeBtn = flash.querySelector('.flash-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => dismissFlash(flash));
    }
  });
}

function dismissFlash(el) {
  el.style.opacity = '0';
  el.style.transform = 'translateX(20px)';
  el.style.transition = 'all 0.3s ease';
  setTimeout(() => el.remove(), 300);
}

// ─────────────────────────────────────────────────────────────
// Toast Notification System
// ─────────────────────────────────────────────────────────────
function showToast(message, type = 'info', duration = 3500) {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
  const colors = {
    success: 'var(--success)',
    error: 'var(--danger)',
    warning: 'var(--warning)',
    info: 'var(--accent)',
  };

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.style.borderLeft = `3px solid ${colors[type] || colors.info}`;
  toast.innerHTML = `
    <span style="font-size:18px">${icons[type] || icons.info}</span>
    <span style="flex:1;font-size:14px">${message}</span>
    <button onclick="this.parentElement.remove()"
            style="background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:16px">✕</button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ─────────────────────────────────────────────────────────────
// Sidebar Mobile Toggle
// ─────────────────────────────────────────────────────────────
function initSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');
  const hamburger = document.querySelector('.hamburger');

  if (!sidebar) return;

  function openSidebar() {
    sidebar.classList.add('open');
    if (overlay) overlay.classList.add('visible');
  }

  function closeSidebar() {
    sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('visible');
  }

  if (hamburger) {
    hamburger.addEventListener('click', () => {
      sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
    });
  }

  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  // Close on nav item click (mobile)
  const navItems = sidebar.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      if (window.innerWidth <= 768) closeSidebar();
    });
  });
}

// ─────────────────────────────────────────────────────────────
// File Upload with Drag & Drop
// ─────────────────────────────────────────────────────────────
function initFileUpload() {
  const zone = document.getElementById('uploadZone');
  const fileInput = document.getElementById('fileInput');
  const preview = document.getElementById('filePreview');
  const previewName = document.getElementById('previewName');
  const previewSize = document.getElementById('previewSize');
  const previewIcon = document.getElementById('previewIcon');
  const submitBtn = document.getElementById('submitBtn');

  if (!zone || !fileInput) return;

  const ALLOWED = ['application/pdf', 'image/png', 'image/jpeg'];
  const ALLOWED_EXT = ['.pdf', '.png', '.jpg', '.jpeg'];
  const MAX_MB = 10;

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  }

  function getFileIcon(type) {
    if (type === 'application/pdf') return '📄';
    if (type.startsWith('image/')) return '🖼️';
    return '📁';
  }

  function handleFile(file) {
    if (!file) return;

    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXT.includes(ext)) {
      showToast('Invalid file type. Please upload PDF, PNG, JPG, or JPEG.', 'error');
      fileInput.value = '';
      return;
    }

    const sizeMB = file.size / (1024 * 1024);
    if (sizeMB > MAX_MB) {
      showToast(`File too large (${sizeMB.toFixed(1)} MB). Maximum is 10 MB.`, 'error');
      fileInput.value = '';
      return;
    }

    if (previewName) previewName.textContent = file.name;
    if (previewSize) previewSize.textContent = formatSize(file.size);
    if (previewIcon) previewIcon.textContent = getFileIcon(file.type);
    if (preview) preview.classList.add('visible');
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Analyze Report';
    }

    showToast(`File ready: ${file.name}`, 'success', 2000);
  }

  // Click to select
  zone.addEventListener('click', () => fileInput.click());

  fileInput.addEventListener('change', (e) => {
    handleFile(e.target.files[0]);
  });

  // Drag and Drop
  zone.addEventListener('dragover', (e) => {
    e.preventDefault();
    zone.classList.add('drag-over');
  });

  zone.addEventListener('dragleave', () => {
    zone.classList.remove('drag-over');
  });

  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) {
      // Set the file to the input
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      fileInput.files = dataTransfer.files;
      handleFile(file);
    }
  });

  // Prevent default drag behaviors on page
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
    document.addEventListener(evt, (e) => {
      if (!zone.contains(e.target)) e.preventDefault();
    });
  });

  // Form submission with progress
  const form = document.getElementById('uploadForm');
  if (form) {
    form.addEventListener('submit', (e) => {
      if (!fileInput.files || fileInput.files.length === 0) {
        e.preventDefault();
        showToast('Please select a file first.', 'error');
        return;
      }

      // Show processing overlay
      const overlay = document.getElementById('processingOverlay');
      if (overlay) {
        overlay.classList.add('visible');
        overlay.style.display = 'flex';
      }

      // Update button
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> Uploading & Analyzing...';
      }
    });
  }
}

// ─────────────────────────────────────────────────────────────
// Report Q&A (Ask AI)
// ─────────────────────────────────────────────────────────────
function initQA() {
  const qaForm = document.getElementById('qaForm');
  const qaInput = document.getElementById('qaInput');
  const qaMessages = document.getElementById('qaMessages');
  const qaBtn = document.getElementById('qaBtn');
  const reportId = document.getElementById('reportId')?.value;

  if (!qaForm || !reportId) return;

  // Pre-load existing history (already rendered by server)
  // Scroll to bottom
  if (qaMessages) {
    qaMessages.scrollTop = qaMessages.scrollHeight;
  }

  // Question pill click
  document.querySelectorAll('.question-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      if (qaInput) qaInput.value = pill.dataset.question;
      qaInput?.focus();
    });
  });

  // Form submit
  qaForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = qaInput?.value.trim();
    if (!question) return;

    if (question.length > 500) {
      showToast('Question too long (max 500 characters).', 'warning');
      return;
    }

    // Add user message to chat
    appendMessage(question, 'user');
    qaInput.value = '';

    // Show typing indicator
    const typingId = showTyping();

    if (qaBtn) {
      qaBtn.disabled = true;
      qaBtn.innerHTML = '<span class="spinner"></span>';
    }

    try {
      const resp = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ report_id: parseInt(reportId), question }),
      });

      const data = await resp.json();
      removeTyping(typingId);

      if (resp.ok) {
        appendMessage(data.answer, 'ai');
        if (!data.ai_configured) {
          showToast('AI not configured — showing informational response.', 'warning', 4000);
        }
      } else {
        appendMessage(
          data.error || 'Unable to process your question. Please try again.',
          'ai',
          true
        );
      }
    } catch (err) {
      removeTyping(typingId);
      appendMessage('Network error. Please check your connection and try again.', 'ai', true);
    } finally {
      if (qaBtn) {
        qaBtn.disabled = false;
        qaBtn.innerHTML = '↵ Send';
      }
    }
  });

  function appendMessage(text, sender, isError = false) {
    if (!qaMessages) return;

    const isUser = sender === 'user';
    const avatarText = isUser ? '👤' : '🤖';
    const color = isError ? 'var(--danger)' : '';

    const div = document.createElement('div');
    div.className = `message ${isUser ? 'user' : 'ai'}`;
    div.style.animation = 'fadeIn 0.3s ease';
    div.innerHTML = `
      <div class="message-avatar">${avatarText}</div>
      <div class="message-bubble" ${color ? `style="color:${color}"` : ''}>
        ${escapeHtml(text)}
      </div>
    `;
    qaMessages.appendChild(div);
    qaMessages.scrollTop = qaMessages.scrollHeight;
  }

  function showTyping() {
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.className = 'message ai';
    div.id = id;
    div.innerHTML = `
      <div class="message-avatar">🤖</div>
      <div class="message-bubble" style="display:flex;gap:5px;align-items:center">
        <span class="typing-dot" style="width:7px;height:7px;border-radius:50%;background:var(--text-muted);animation:pulse 1s infinite 0s"></span>
        <span class="typing-dot" style="width:7px;height:7px;border-radius:50%;background:var(--text-muted);animation:pulse 1s infinite 0.2s"></span>
        <span class="typing-dot" style="width:7px;height:7px;border-radius:50%;background:var(--text-muted);animation:pulse 1s infinite 0.4s"></span>
      </div>
    `;
    if (qaMessages) qaMessages.appendChild(div);
    if (qaMessages) qaMessages.scrollTop = qaMessages.scrollHeight;
    return id;
  }

  function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }
}

// ─────────────────────────────────────────────────────────────
// Report Search & Filter
// ─────────────────────────────────────────────────────────────
function initReportSearch() {
  const searchInput = document.getElementById('reportSearch');
  const filterSelect = document.getElementById('filterStatus');
  const rows = document.querySelectorAll('.report-row');

  if (!searchInput && !filterSelect) return;

  function filterReports() {
    const query = searchInput?.value.toLowerCase() || '';
    const status = filterSelect?.value || '';

    rows.forEach(row => {
      const name = (row.dataset.name || '').toLowerCase();
      const rowStatus = (row.dataset.status || '').toLowerCase();

      const matchName = !query || name.includes(query);
      const matchStatus = !status || rowStatus === status.toLowerCase();

      row.style.display = (matchName && matchStatus) ? '' : 'none';
    });

    // Show empty state if no results
    const visibleRows = [...rows].filter(r => r.style.display !== 'none');
    const emptyState = document.getElementById('noResults');
    if (emptyState) {
      emptyState.style.display = visibleRows.length === 0 ? 'block' : 'none';
    }
  }

  searchInput?.addEventListener('input', filterReports);
  filterSelect?.addEventListener('change', filterReports);
}

// ─────────────────────────────────────────────────────────────
// Delete Confirmation Modal
// ─────────────────────────────────────────────────────────────
function initDeleteModal() {
  const modal = document.getElementById('deleteModal');
  const deleteForm = document.getElementById('deleteForm');
  const reportNameEl = document.getElementById('deleteReportName');

  window.confirmDelete = function(reportId, reportName) {
    if (!modal) {
      // Fallback: simple confirm
      if (confirm(`Delete "${reportName}"? This cannot be undone.`)) {
        document.getElementById(`delete-form-${reportId}`)?.submit();
      }
      return;
    }
    if (reportNameEl) reportNameEl.textContent = `"${reportName}"`;
    if (deleteForm) deleteForm.action = `/reports/${reportId}/delete`;
    modal.classList.add('visible');
  };

  window.closeDeleteModal = function() {
    modal?.classList.remove('visible');
  };

  modal?.addEventListener('click', (e) => {
    if (e.target === modal) closeDeleteModal();
  });
}

// ─────────────────────────────────────────────────────────────
// Utility: Escape HTML
// ─────────────────────────────────────────────────────────────
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ─────────────────────────────────────────────────────────────
// Smooth scroll for anchor links
// ─────────────────────────────────────────────────────────────
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

// ─────────────────────────────────────────────────────────────
// Character counter for Q&A input
// ─────────────────────────────────────────────────────────────
function initCharCounter() {
  const input = document.getElementById('qaInput');
  const counter = document.getElementById('charCounter');
  if (!input || !counter) return;

  input.addEventListener('input', () => {
    const len = input.value.length;
    counter.textContent = `${len}/500`;
    counter.style.color = len > 450 ? 'var(--danger)' : 'var(--text-muted)';
  });
}

// ─────────────────────────────────────────────────────────────
// Initialize everything when DOM is ready
// ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initFlashMessages();
  initSidebar();
  initFileUpload();
  initQA();
  initReportSearch();
  initDeleteModal();
  initSmoothScroll();
  initCharCounter();
});
