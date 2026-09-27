/* Progressive enhancement: the complete register is readable without JavaScript. */
const form = document.querySelector('#dynamoFilters');
const group = document.querySelector('#dynamoGroup');
const search = document.querySelector('#dynamoSearch');
const cards = [...document.querySelectorAll('.dynamo-card')];
const index = cards.map(card => ({card, text: card.textContent.toLocaleLowerCase('en')}));
const count = document.querySelector('#dynamoCount');
const sourceDrawer = document.querySelector('#dynamoSources');

function filter() {
  const term = search.value.trim().toLocaleLowerCase('en');
  let visible = 0;
  for (const {card, text} of index) {
    card.hidden = Boolean((group.value && card.dataset.group !== group.value) || (term && !text.includes(term)));
    if (!card.hidden) visible++;
  }
  count.textContent = `${visible} of ${cards.length} proposals · all discriminating tests are planned`;
  document.querySelector('#dynamoEmpty').hidden = visible !== 0;
}

function revealHash() {
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  const target = document.getElementById(id);
  if (!target) return;
  if (target.classList.contains('dynamo-card')) {
    group.value = target.dataset.group;
    search.value = '';
    filter();
    target.open = true;
  } else if (target.id.startsWith('source-')) {
    sourceDrawer.open = true;
  } else return;
  target.scrollIntoView({block: 'start'});
}

form.hidden = false;
group.value = 'chronology';
group.addEventListener('change', filter);
search.addEventListener('input', () => {
  // Search spans the whole register, as the label promises.
  group.value = '';
  filter();
});
form.addEventListener('submit', event => event.preventDefault());
form.addEventListener('reset', event => {
  event.preventDefault();
  search.value = '';
  group.value = 'chronology';
  filter();
});
window.addEventListener('hashchange', revealHash);
// Also reopen a source or proposal if its existing fragment is clicked again.
document.addEventListener('click', event => {
  const link = event.target.closest('a[href]');
  if (link && new URL(link.href).hash === location.hash && new URL(link.href).pathname === location.pathname) {
    requestAnimationFrame(revealHash);
  }
});
filter();
revealHash();
