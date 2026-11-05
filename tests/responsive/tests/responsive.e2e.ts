import { test } from '@e2e-dev/web';
import { expect } from 'e2e';
import { inspectLayout } from './layout.js';

// Каждый тест запускается на всех трёх targets из конфига.
const pages = [
  ['/', 'Новые вопросы'],
  ['/question/1/', 'Вопрос'],
  ['/ask/', 'Новый вопрос'],
  ['/login/', 'Вход'],
  ['/signup/', 'Регистрация'],
  ['/profile/', 'Настройки профиля'],
] as const;

for (const [path, heading] of pages) {
  test(`${path}: шапка, колонки, карточки и поля помещаются на экране`, async ({ app, screen, browser }) => {
    await app.open(path);
    await expect(screen.getByRole('banner')).toBeVisible();
    await expect(screen.getByRole('searchbox', 'Поиск вопросов')).toBeVisible();
    const width = await browser.evaluate(() => window.innerWidth);
    if (width < 992) {
      await expect(screen.getByRole('button', 'Меню пользователя', { exact: true })).toBeVisible();
    } else {
      await expect(screen.getByRole('link', 'Задать вопрос', { exact: true })).toBeVisible();
    }
    await expect(screen.getByRole('complementary', 'Сообщество')).toBeVisible();
    await expect(screen.getByRole('contentinfo')).toBeAttached();
    if (heading) await expect(screen.getByRole('heading', heading, { level: 1, exact: true })).toBeVisible();
    await expect.poll(() => browser.evaluate(inspectLayout), {
      message: `${path}: ошибки адаптивной верстки`,
    }).toEqual([]);
    await app.screenshot(path === '/' ? 'index' : path.split('/').filter(Boolean).join('-'));
  });
}

test('Футер при коротком контенте прижат к низу окна', async ({ app, browser }) => {
  // Увеличиваем высоту, чтобы даже сайдбар целиком поместился в окно.
  await app.open('/login/');
  const width = await browser.evaluate(() => window.innerWidth);
  await browser.setViewport({ width, height: 2400 });
  const footer = await browser.evaluate(() => {
    const rect = document.querySelector('footer')!.getBoundingClientRect();
    return { bottom: rect.bottom, height: window.innerHeight, scroll: document.documentElement.scrollHeight };
  });
  expect(Math.abs(footer.bottom - footer.height)).toBeLessThanOrEqual(1);
  expect(footer.scroll).toBeLessThanOrEqual(footer.height + 1);
});

test('Длинные значения полей не растягивают форму вопроса', async ({ app, screen, browser }) => {
  await app.open('/ask/');
  await screen.getByLabel('Заголовок', { exact: true }).fill('ОченьДлинныйЗаголовок'.repeat(7));
  await screen.getByLabel('Текст вопроса', { exact: true }).fill('ДлинноеСловоБезПробелов'.repeat(100));
  await screen.getByLabel('Теги', { exact: true }).fill('a'.repeat(30) + ', ' + 'b'.repeat(30) + ', ' + 'c'.repeat(30));
  await expect.poll(() => browser.evaluate(inspectLayout)).toEqual([]);
  await app.screenshot('ask-long-values');
});

test('Колонки перестраиваются при изменении размера открытой страницы', async ({ app, browser }) => {
  await app.open('/question/1/');
  for (const width of [1200, 992, 991, 768, 546, 375, 1200]) {
    await browser.setViewport({ width, height: 900 });
    await expect.poll(() => browser.evaluate(inspectLayout), {
      message: `После изменения ширины на ${width}px`,
    }).toEqual([]);
  }
});


test('Меню пользователя открывается и закрывается на узком экране', async ({ app, screen, browser }) => {
  await app.open('/');
  const width = await browser.evaluate(() => window.innerWidth);
  const toggle = screen.getByRole('button', 'Меню пользователя', { exact: true });
  if (width >= 992) {
    await expect(toggle).toBeHidden();
    await expect(screen.getByRole('link', 'Задать вопрос', { exact: true })).toBeVisible();
    return;
  }
  await toggle.tap();
  await expect(toggle).toBeExpanded();
  const menu = browser.locator('header .dropdown-menu');
  for (const name of ['Задать вопрос', 'Войти', 'Регистрация']) {
    await expect(menu.getByRole('link', name, { exact: true })).toBeVisible();
  }
  await expect.poll(() => browser.evaluate(inspectLayout)).toEqual([]);
  await app.screenshot('mobile-user-menu');
  await toggle.press('Escape');
  await expect(toggle).toHaveAttribute('aria-expanded', 'false');
  await toggle.tap();
  await menu.getByRole('link', 'Задать вопрос', { exact: true }).tap();
  await expect(browser).toHaveURL('/ask/');
});

test('Регистрация открывается с пустыми email и никнеймом', async ({ app, screen }) => {
  await app.open('/signup/');
  await expect(screen.getByLabel('Электронная почта', { exact: true })).toHaveValue('');
  await expect(screen.getByLabel('Никнейм', { exact: true })).toHaveValue('');
});


test('Django отдаёт локальные стили, JS и favicon', async ({ app }) => {
  for (const [path, contentType] of [
    ['/static/css/bootstrap.min.css', 'text/css'],
    ['/static/css/style.css', 'text/css'],
    ['/static/js/bootstrap.bundle.min.js', /javascript/],
    ['/static/img/favicon.svg', 'image/svg+xml'],
  ] as const) {
    const response = await fetch(new URL(path, app.baseUrl));
    expect(response.status, path).toBe(200);
    const type = response.headers.get('content-type') ?? '';
    if (typeof contentType === 'string') expect(type).toContain(contentType);
    else expect(type).toMatch(contentType);
    expect((await response.text()).length).toBeGreaterThan(0);
  }
});

test('Ссылка из списка открывает выбранный вопрос', async ({ app, screen, browser }) => {
  await app.open('/');
  await screen.getByRole('link', 'Как работает сетка Bootstrap?', { exact: true }).tap();
  await expect(browser).toHaveURL('/question/2/');
  await expect(screen.getByRole('heading', 'Как работает сетка Bootstrap?', { level: 2, exact: true })).toBeVisible();
  await expect(screen.getByRole('heading', 'Ответы (2)', { exact: true })).toBeVisible();
});

test('Пагинатор скрыт при единственной странице', async ({ app, screen }) => {
  await app.open('/');
  await expect(screen.getByRole('navigation', 'Страницы вопросов', { exact: true })).toHaveCount(0);
  await app.open('/question/1/');
  await expect(screen.getByRole('navigation', 'Страницы ответов', { exact: true })).toHaveCount(0);
});

test('Некорректный page открывает допустимую страницу; неизвестный вопрос возвращает 404', async ({ app }) => {
  for (const route of ['/', '/question/1/']) {
    for (const value of ['abc', '0', '-1', '999', '']) {
      const response = await fetch(new URL(`${route}?page=${value}`, app.baseUrl));
      expect(response.status, `${route}?page=${value}`).toBe(200);
      expect(await response.text()).toContain('Как подключить статические файлы в Django?');
    }
  }
  const response = await fetch(new URL('/question/999/', app.baseUrl));
  expect(response.status).toBe(404);
});

test('Гость видит приглашение войти вместо формы ответа', async ({ app, screen }) => {
  await app.open('/question/1/');
  await expect(screen.getByRole('heading', 'Ваш ответ', { exact: true })).toBeVisible();
  await expect(screen.getByLabel('Текст ответа', { exact: true })).toHaveCount(0);
  await expect(screen.getByRole('link', 'войдите', { exact: true })).toBeVisible();
});

test('POST формы вопроса показывает серверные ошибки и сохраняет поля', async ({ app, screen, browser }) => {
  await app.open('/ask/');
  await expect(screen.getByRole('alert')).toHaveCount(0);
  await screen.getByLabel('Заголовок', { exact: true }).fill('Тестовый вопрос');
  await screen.getByLabel('Текст вопроса', { exact: true }).fill('Тестовое описание задачи');
  await screen.getByLabel('Теги', { exact: true }).fill('python, django, css, html');
  await screen.getByRole('button', 'Опубликовать', { exact: true }).tap();
  await expect(screen.getByRole('alert')).toContainText('Вопрос не опубликован');
  await expect(screen.getByText('Можно указать не более 3 тегов.', { exact: true })).toBeVisible();
  await expect(screen.getByLabel('Заголовок', { exact: true })).toHaveValue('Тестовый вопрос');
  await expect.poll(() => browser.evaluate(inspectLayout)).toEqual([]);
  await app.screenshot('ask-server-error');
});

test('Валидный POST проходит CSRF и проверку формы без фиктивной публикации', async ({ app, screen }) => {
  await app.open('/ask/');
  await screen.getByLabel('Заголовок', { exact: true }).fill('Тестовый вопрос');
  await screen.getByLabel('Текст вопроса', { exact: true }).fill('Тестовое описание задачи');
  await screen.getByLabel('Теги', { exact: true }).fill('python, django');
  await screen.getByRole('button', 'Опубликовать', { exact: true }).tap();
  await expect(screen.getByRole('status')).toContainText('Данные проверены.');
  await expect(screen.getByRole('alert')).toHaveCount(0);
});
