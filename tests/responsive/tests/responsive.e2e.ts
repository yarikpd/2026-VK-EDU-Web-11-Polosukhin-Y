import { test } from '@e2e-dev/web';
import { expect } from 'e2e';
import { inspectLayout } from './layout.js';

// Каждый тест запускается на всех трёх targets из конфига.
const pages = [
  ['base.html', null],
  ['index.html', 'Новые вопросы'],
  ['question.html', 'Вопрос'],
  ['ask.html', 'Новый вопрос'],
  ['login.html', 'Вход'],
  ['signup.html', 'Регистрация'],
  ['profile.html', 'Настройки профиля'],
] as const;

for (const [path, heading] of pages) {
  test(`${path}: шапка, колонки, карточки и поля помещаются на экране`, async ({ app, screen, browser }) => {
    await app.open(`/${path}`);
    await expect(screen.getByRole('banner')).toBeVisible();
    await expect(screen.getByRole('searchbox', 'Поиск вопросов')).toBeVisible();
    await expect(screen.getByRole('link', 'Задать вопрос', { exact: true })).toBeVisible();
    await expect(screen.getByRole('complementary', 'Сообщество')).toBeVisible();
    await expect(screen.getByRole('contentinfo')).toBeAttached();
    if (heading) await expect(screen.getByRole('heading', heading, { level: 1, exact: true })).toBeVisible();
    await expect.poll(() => browser.evaluate(inspectLayout), {
      message: `${path}: ошибки адаптивной верстки`,
    }).toEqual([]);
    await app.screenshot(path.replace('.html', ''));
  });
}

test('Футер при коротком контенте прижат к низу окна', async ({ app, browser }) => {
  // Увеличиваем высоту, чтобы даже сайдбар целиком поместился в окно.
  await app.open('/base.html');
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
  await app.open('/ask.html');
  await screen.getByLabel('Заголовок', { exact: true }).fill('ОченьДлинныйЗаголовок'.repeat(7));
  await screen.getByLabel('Текст вопроса', { exact: true }).fill('ДлинноеСловоБезПробелов'.repeat(100));
  await screen.getByLabel('Теги', { exact: true }).fill('a'.repeat(30) + ', ' + 'b'.repeat(30) + ', ' + 'c'.repeat(30));
  await expect.poll(() => browser.evaluate(inspectLayout)).toEqual([]);
  await app.screenshot('ask-long-values');
});

test('Колонки перестраиваются при изменении размера открытой страницы', async ({ app, browser }) => {
  await app.open('/question.html');
  for (const width of [1200, 768, 375, 1200]) {
    await browser.setViewport({ width, height: 900 });
    await expect.poll(() => browser.evaluate(inspectLayout), {
      message: `После изменения ширины на ${width}px`,
    }).toEqual([]);
  }
});
