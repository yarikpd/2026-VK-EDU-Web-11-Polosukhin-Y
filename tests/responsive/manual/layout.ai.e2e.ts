import { test } from '@e2e-dev/web';
import { expect } from 'e2e';

// Только явный запуск: npx e2e run --config e2e.ai.config.ts
// Один сценарий на каждом из трёх размеров; agent.* обращается к ChatGPT.
test('ИИ: навигация и визуальная проверка адаптивной верстки', {
  tags: ['manual', 'ai'],
}, async ({ app, screen, agent }) => {
  await app.open('/index.html');
  await expect(screen.getByRole('heading', 'Новые вопросы', { level: 1, exact: true })).toBeVisible();
  await agent.assert(
    'Шапка помещается в видимую ширину экрана: логотип, поиск, кнопки и ссылки читаются, не накладываются друг на друга и не обрезаются по горизонтали.',
    { vision: 'only' },
  );
  await app.screenshot('ai-index');

  await agent.act('Открой вопрос «Как подключить статические файлы в Django?»');
  await expect(screen.getByRole('heading', 'Вопрос', { level: 1, exact: true })).toBeVisible();
  await agent.assert(
    'Видимая часть карточки вопроса читается: заголовок, текст и элементы карточки не накладываются друг на друга и не обрезаются по горизонтали.',
    { vision: 'only' },
  );
  await app.screenshot('ai-question');

  await agent.act('Открой форму через ссылку «Задать вопрос»');
  await expect(screen.getByRole('heading', 'Новый вопрос', { level: 1, exact: true })).toBeVisible();
  await expect(screen.getByLabel('Заголовок', { exact: true })).toBeVisible();
  await agent.assert(
    'Видимая часть формы «Новый вопрос» читается: поля, подписи и подсказки не перекрывают друг друга и помещаются по горизонтали. Красное сообщение об ошибке является примером оформления и само по себе не означает поломку верстки.',
    { vision: 'only' },
  );
  await app.screenshot('ai-ask');
});
