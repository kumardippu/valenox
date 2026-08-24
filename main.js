// Scroll reveals + a border on the nav once the page has scrolled.

document.querySelectorAll('.feature, .trio__item, .card, .split__text, .split__shot, .section__head, .get__cta')
  .forEach(el => el.classList.add('reveal'));

const io = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-in');
      io.unobserve(entry.target);
    }
  });
}, { rootMargin: '0px 0px -12% 0px' });

document.querySelectorAll('.reveal').forEach(el => io.observe(el));

const nav = document.querySelector('.nav');
const onScroll = () => nav.classList.toggle('is-stuck', window.scrollY > 12);
onScroll();
window.addEventListener('scroll', onScroll, { passive: true });

// Side-by-side phones twist through 3D as they cross the viewport: turned away
// at the edges, square-on and fully legible once centred. TWIST is the turn at
// the extremes — raise it for more drama, drop it for less.
const TWIST = 34;

const phones = Array.from(document.querySelectorAll('.feature__shot .phone, .split__shot .phone'))
  .map(el => ({
    el,
    // Rows alternate sides, so mirror the hinge and every phone turns towards
    // the middle of the page instead of all leaning the same way.
    hinge: el.closest('.feature--flip') ? -1 : 1,
  }));

const stillness = window.matchMedia('(prefers-reduced-motion: reduce)');

if (phones.length && !stillness.matches) {
  let queued = false;

  const turn = () => {
    queued = false;
    const mid = window.innerHeight / 2;
    phones.forEach(({ el, hinge }) => {
      const box = el.getBoundingClientRect();
      if (box.bottom < 0 || box.top > window.innerHeight) return;
      // -1 while the phone sits above the viewport's middle, +1 below it.
      const travel = Math.max(-1, Math.min(1, (box.top + box.height / 2 - mid) / mid));
      el.style.setProperty('--twist', `${(travel * TWIST * hinge).toFixed(2)}deg`);
      el.style.setProperty('--drift', `${(travel * 18).toFixed(2)}px`);
      el.style.setProperty('--tilt', `${(travel * -1.6).toFixed(2)}deg`);
    });
  };

  const queueTurn = () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(turn);
  };

  turn();
  window.addEventListener('scroll', queueTurn, { passive: true });
  window.addEventListener('resize', queueTurn, { passive: true });
}
