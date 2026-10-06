const menu = document.querySelector('.menu');
// The compact SVG stays readable in browser tabs and on saved mobile shortcuts.
if (!document.querySelector('link[rel="icon"]')) {
  const favicon = document.createElement('link');
  favicon.rel = 'icon';
  favicon.type = 'image/svg+xml';
  favicon.href = 'assets/favicon.svg';
  document.head.append(favicon);
}
const nav = document.querySelector('#nav');
const closeMobileNav = () => {
  if (!menu || !nav) return;
  menu.setAttribute('aria-expanded', 'false');
  nav.classList.remove('open');
};
if (menu && nav) {
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') === 'true';
    menu.setAttribute('aria-expanded', String(!open));
    nav.classList.toggle('open', !open);
  });
}


// Expanded Services navigation: Services itself toggles the menu; the All Services link lives inside it.
const servicesNav = document.querySelector('.navServices');
const servicesToggle = document.querySelector('.servicesNavButton');
if (servicesNav && servicesToggle) {
  const setServicesMenu = open => {
    servicesNav.classList.toggle('menu-open', open);
    servicesToggle.setAttribute('aria-expanded', String(open));
    servicesToggle.setAttribute('aria-label', open ? 'Close services menu' : 'Open services menu');
  };
  servicesToggle.addEventListener('click', event => {
    event.preventDefault();
    event.stopPropagation();
    setServicesMenu(!servicesNav.classList.contains('menu-open'));
  });
  // Close as soon as the visitor starts a click somewhere else. This keeps the
  // panel from feeling sticky on touch devices and desktop alike.
  document.addEventListener('pointerdown', event => {
    if (!servicesNav.contains(event.target)) setServicesMenu(false);
    // On mobile, a tap outside the complete nav is an escape from the entire
    // expanded menu—not only the Services sub-panel.
    if (!nav.contains(event.target) && !menu.contains(event.target)) closeMobileNav();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && servicesNav.classList.contains('menu-open')) {
      setServicesMenu(false);
      servicesToggle.focus();
    }
  });
}

const symptomCopy = {
  start: {label: "Won’t start", copy: "Tell the shop what happens when you turn the key: nothing, clicking, slow cranking, or cranking without starting. If you are in an unsafe location, prioritize getting somewhere safe."},
  light: {label: "Warning light", copy: "Note which warning light appeared and whether the vehicle feels different. A photo of the dashboard can help when you request service."},
  brakes: {label: "Grinding / brakes", copy: "Grinding, squealing, pulling, a soft pedal, or longer stopping distance are useful details. If stopping feels unsafe, do not keep driving just to reach the shop."},
  shake: {label: "Shaking / vibration", copy: "Tell J&T when the vibration happens — at idle, while braking, during acceleration, or at a certain speed. You do not need to know the cause."},
  heat: {label: "Overheating", copy: "If the temperature is climbing or you see steam, stop somewhere safe and shut the vehicle down. Do not open a hot cooling system. Call for the next step."},
  leak: {label: "Leaking fluid", copy: "Note where the fluid appears under the vehicle and, if you can do so safely, its color. A photo is more useful than guessing what the fluid is."},
  noise: {label: "Strange noise", copy: "Describe the sound in your own words and when it happens — turning, braking, accelerating, idling, or hitting bumps. That is enough to start."},
  other: {label: "Something else", copy: "Something feels different but none of these fit? Say exactly that. Describe what changed and when you first noticed it."}
};

document.querySelectorAll('[data-symptom]').forEach(btn => btn.addEventListener('click', () => {
  document.querySelectorAll('[data-symptom]').forEach(b => b.setAttribute('aria-pressed', 'false'));
  btn.setAttribute('aria-pressed', 'true');
  const selected = symptomCopy[btn.dataset.symptom] || symptomCopy.other;
  const out = document.querySelector('#symptomCopy');
  if (out) out.textContent = selected.copy;
  const link = document.querySelector('#symptomRequest');
  if (link) {
    link.href = 'tel:+14198194069';
    link.textContent = 'Call J&T →';
    link.setAttribute('aria-label', `Call J&T about: ${selected.label}`);
  }

  // On a phone the choices are a vertical list and the response sits below it.
  // Move directly to the useful answer so a tap never appears to do nothing.
  if (window.matchMedia('(max-width: 780px)').matches && out) {
    const result = out.closest('.symptom-result');
    if (result) {
      result.setAttribute('tabindex', '-1');
      result.scrollIntoView({ behavior: reducedMotion.matches ? 'auto' : 'smooth', block: 'start' });
      result.focus({ preventScroll: true });
    }
  }
}));

// Site-wide motion language. It is intentionally quiet: each chapter arrives
// once, real actions get feedback, and image-led heroes have a little depth.
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
if (!reducedMotion.matches) {
  const revealTargets = new Set([
    ...document.querySelectorAll('main > section, main > nav.breadcrumbs'),
    ...document.querySelectorAll('.serviceCards > *, .serviceDirectoryGrid > *, .clueGrid > *, .reviewTicketGrid > *, .faqList > details, .symptomDesk > article')
  ]);
  const revealObserver = 'IntersectionObserver' in window && new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      revealObserver.unobserve(entry.target);
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -36px' });

  revealTargets.forEach((el, index) => {
    if (el.closest('footer') || el.matches('.servicesConceptHero')) return;
    el.classList.add('motion-reveal');
    el.style.setProperty('--motion-order', String(index % 5));
    if (revealObserver) revealObserver.observe(el);
    else el.classList.add('is-visible');
  });

  document.querySelectorAll('main :is(a.cta,a.secondary,.serviceCard,[data-symptom],.contactStartPaths a,.contactMapFallback)').forEach(el => {
    el.classList.add('motion-lift');
  });

  if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    document.querySelectorAll('.servicesHeroPhoto,.diagnosticHeroPhoto,.campusHeroVisual,.contactHeroImage').forEach(el => {
      el.classList.add('motion-depth');
      el.addEventListener('pointermove', event => {
        const box = el.getBoundingClientRect();
        const x = ((event.clientX - box.left) / box.width - .5) * 2;
        const y = ((event.clientY - box.top) / box.height - .5) * 2;
        el.style.setProperty('--depth-x', `${x * .65}deg`);
        el.style.setProperty('--depth-y', `${y * -.65}deg`);
      });
      el.addEventListener('pointerleave', () => {
        el.style.removeProperty('--depth-x');
        el.style.removeProperty('--depth-y');
      });
    });
  }
}

// Keep multi-word local names together in running copy without changing the
// intentional line breaks in display headings.
const noBreakNames = [
  ['Bowling Green State University', 'Bowling\u00a0Green\u00a0State\u00a0University'],
  ['J&T Auto Service of BG', 'J&T\u00a0Auto\u00a0Service\u00a0of\u00a0BG'],
  ['J&T Auto Service', 'J&T\u00a0Auto\u00a0Service'],
  ['Bowling Green', 'Bowling\u00a0Green'],
  ['BGSU Students', 'BGSU\u00a0Students']
];
const copyWalker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
const copyNodes = [];
while (copyWalker.nextNode()) copyNodes.push(copyWalker.currentNode);
copyNodes.forEach(node => {
  const parent = node.parentElement;
  if (!parent || parent.closest('script,style,h1,h2,h3,h4,h5,h6')) return;
  let text = node.nodeValue;
  noBreakNames.forEach(([name, replacement]) => { text = text.split(name).join(replacement); });
  node.nodeValue = text;
});

// Hours belong with the evergreen business details, not in a one-page fact rail.
const footerDetails = document.querySelector('body > footer .footerBrand > div');
if (footerDetails && !footerDetails.querySelector('.footerHours')) {
  const hours = document.createElement('p');
  hours.className = 'footerHours';
  hours.textContent = 'Hours: Mon–Fri 8:00 AM–5:30 PM*';
  footerDetails.append(hours);
}
