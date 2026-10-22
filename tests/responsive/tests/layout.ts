// Выполняется внутри браузера через browser.evaluate; внешних зависимостей нет.
export function inspectLayout() {
  const errors: string[] = [];
  const tolerance = 1; // Допуск на дробные пиксели Bootstrap-сетки.
  const width = document.documentElement.clientWidth;
  const visible = (element: Element) => {
    const style = getComputedStyle(element);
    return style.display !== 'none' && style.visibility !== 'hidden'
      && element.getBoundingClientRect().width > 0;
  };
  const name = (element: Element) =>
    `${element.tagName.toLowerCase()}${element.id ? `#${element.id}` : ''} ${element.textContent?.trim().slice(0, 55) ?? ''}`;
  const check = (condition: boolean, message: string) => {
    if (!condition) errors.push(message);
  };
  const overlaps = (a: DOMRect, b: DOMRect) =>
    Math.min(a.right, b.right) - Math.max(a.left, b.left) > tolerance
    && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > tolerance;

  check(document.documentElement.scrollWidth <= width + tolerance,
    `Страница шире viewport: ${document.documentElement.scrollWidth} > ${width}`);
  check(document.body.scrollWidth <= width + tolerance, 'Body имеет горизонтальное переполнение');

  // И скрытое overflow:hidden переполнение внутри карточек тоже считается ошибкой.
  for (const element of document.querySelectorAll('.card, .btn-group, form, .alert')) {
    if (visible(element)) {
      check(element.scrollWidth <= element.clientWidth + tolerance,
        `Переполнение внутри ${name(element)}`);
    }
  }
  for (const element of document.querySelectorAll('header a, header button, .form-control, .btn, .page-link, .badge')) {
    if (!visible(element)) continue;
    const rect = element.getBoundingClientRect();
    check(rect.left >= -tolerance && rect.right <= width + tolerance,
      `Элемент выходит за экран: ${name(element)}`);
  }

  // Проверяем реальные прямоугольники, а не наличие Bootstrap-классов.
  for (const selector of ['header > .container', '.search-form']) {
    const container = document.querySelector(selector);
    check(!!container, `Не найден ${selector}`);
    if (!container) continue;
    const children = Array.from(container.children).filter(visible);
    for (let i = 0; i < children.length; i++) {
      for (let j = i + 1; j < children.length; j++) {
        check(!overlaps(children[i].getBoundingClientRect(), children[j].getBoundingClientRect()),
          `Наложение в шапке: ${name(children[i])} / ${name(children[j])}`);
      }
    }
  }

  const column = document.querySelector('main > .row > div');
  const sidebar = document.querySelector('main aside');
  check(!!column && !!sidebar, 'Нет основной колонки или сайдбара');
  if (column && sidebar) {
    const mainRect = column.getBoundingClientRect();
    const sideRect = sidebar.getBoundingClientRect();
    if (width < 768) {
      check(sideRect.top >= mainRect.bottom - tolerance, 'На телефоне сайдбар должен идти под контентом');
    } else {
      check(sideRect.left >= mainRect.right - tolerance, 'Сайдбар должен находиться справа от контента');
      check(Math.abs(sideRect.top - mainRect.top) <= tolerance, 'Верхние края колонок не выровнены');
    }
  }

  for (const control of document.querySelectorAll('main .form-control')) {
    const parent = control.parentElement!;
    const fieldRect = control.getBoundingClientRect();
    const parentRect = parent.getBoundingClientRect();
    check(fieldRect.left >= parentRect.left - tolerance && fieldRect.right <= parentRect.right + tolerance,
      `Поле выходит за контейнер: ${name(control)}`);
    if (width < 768) {
      check(Math.abs(fieldRect.width - parentRect.width) <= tolerance,
        `Поле не занимает ширину контейнера: ${name(control)}`);
    }
  }
  return errors;
}
