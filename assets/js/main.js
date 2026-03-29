/* ============================================================
   TDLI Muon Physics Group — Scripts v2.0
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {

  /* Active nav on scroll */
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-links a:not(.nav-cta)');
  const navEl = document.querySelector('nav');

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY + 120;
    sections.forEach(section => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      const id = section.getAttribute('id');
      if (scrollY >= top && scrollY < top + height) {
        navLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === '#' + id) link.classList.add('active');
        });
      }
    });
    navEl.classList.toggle('scrolled', window.scrollY > 50);
  });

  /* Mobile menu */
  const toggle = document.querySelector('.mobile-toggle');
  const navMenu = document.querySelector('.nav-links');
  if (toggle && navMenu) {
    toggle.addEventListener('click', () => navMenu.classList.toggle('show'));
    navMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => navMenu.classList.remove('show'));
    });
  }

  /* Fade-in on scroll */
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll(
    '.research-card, .team-card, .team-pi, .timeline-item, .edu-feature-item, .news-card, .joinus-card, .collab-card'
  ).forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
  });

  /* Contact form → Formspree */
  const form = document.getElementById('contact-form');
  const status = document.getElementById('form-status');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      status.className = 'form-status sending';
      status.textContent = '正在发送...';
      try {
        const res = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: { 'Accept': 'application/json' }
        });
        if (res.ok) {
          status.className = 'form-status success';
          status.textContent = '✓ 感谢您的留言！我们会尽快回复。Thank you!';
          form.reset();
        } else {
          const json = await res.json();
          status.className = 'form-status error';
          status.textContent = '✗ ' + ((json.errors && json.errors.map(e => e.message).join(', ')) || '提交失败，请稍后重试。');
        }
      } catch (err) {
        status.className = 'form-status error';
        status.textContent = '✗ 网络错误，请检查网络后重试。';
      }
    });
  }
});
