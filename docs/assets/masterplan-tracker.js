(() => {
  const root = document.querySelector('.uah-tracker');
  if (!root) return;

  const controls = root.querySelector('.tracker-controls');
  const query = controls.querySelector('[name="query"]');
  const status = controls.querySelector('[name="status"]');
  const repository = controls.querySelector('[name="repo"]');
  const cards = [...root.querySelectorAll('.tracker-card')];
  const count = root.querySelector('.tracker-count');
  const empty = root.querySelector('.tracker-empty');

  const update = () => {
    const term = query.value.trim().toLocaleLowerCase();
    let visible = 0;
    cards.forEach((card) => {
      const matches = (status.value === 'all' || card.dataset.status === status.value)
        && (repository.value === 'all' || card.dataset.repo === repository.value)
        && (!term || card.textContent.toLocaleLowerCase().includes(term));
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    count.textContent = visible + ' of ' + cards.length + ' records shown';
    empty.hidden = visible !== 0;
  };

  controls.hidden = false;
  query.addEventListener('input', update);
  status.addEventListener('change', update);
  repository.addEventListener('change', update);
  controls.querySelector('.tracker-clear').addEventListener('click', () => {
    query.value = '';
    status.value = 'all';
    repository.value = 'all';
    update();
    query.focus();
  });
  update();
})();
