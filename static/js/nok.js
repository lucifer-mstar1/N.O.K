(function(){
  const root = document.documentElement;
  const key = 'nok_theme';

  function applyTheme(theme){
    root.setAttribute('data-theme', theme);
    // Also set Bootstrap 5.3 theme attribute so native components match.
    root.setAttribute('data-bs-theme', theme);
    localStorage.setItem(key, theme);
  }

  // Initial theme: storage -> OS preference -> light
  const stored = localStorage.getItem(key);
  if(stored){
    applyTheme(stored);
  } else {
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(prefersDark ? 'dark' : 'light');
  }

  const toggle = document.getElementById('themeToggle');
  if(toggle){
    toggle.addEventListener('click', ()=>{
      const current = root.getAttribute('data-theme') || 'light';
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  // Navbar shadow on scroll
  const navbar = document.getElementById('nokNavbar');
  const onScroll = ()=>{
    if(!navbar) return;
    navbar.classList.toggle('is-scrolled', window.scrollY > 6);
  };
  window.addEventListener('scroll', onScroll, {passive:true});
  onScroll();

  // Soft reveal for sections
  const items = document.querySelectorAll('.nok-reveal');
  if('IntersectionObserver' in window && items.length){
    const io = new IntersectionObserver((entries)=>{
      entries.forEach(e=>{
        if(e.isIntersecting){
          e.target.classList.add('is-visible');
          io.unobserve(e.target);
        }
      });
    }, {threshold: 0.15});
    items.forEach(el=>io.observe(el));
  } else {
    items.forEach(el=>el.classList.add('is-visible'));
  }

  // Copy referral code if present
  const copyBtn = document.querySelector('[data-copy-ref]');
  if(copyBtn){
    copyBtn.addEventListener('click', async ()=>{
      const code = copyBtn.getAttribute('data-copy-ref') || '';
      if(!code) return;
      try{
        await navigator.clipboard.writeText(code);
      }catch(_){
        const input = document.createElement('input');
        input.value = code;
        document.body.appendChild(input);
        input.select();
        document.execCommand('copy');
        document.body.removeChild(input);
      }
      copyBtn.textContent = 'Copied!';
      setTimeout(()=>copyBtn.textContent='Copy', 1200);
    });
  }
})();
