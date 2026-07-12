# Анализ присланного списка каналов

Задача: пользователь прислал 61 ссылку (каналы по handle, один по прямому Channel ID, и ссылки на отдельные видео) — продублировать, свести ссылки на видео к их каналам, убрать повторы, дать статистику.

## Метод
1. `videos.list` (batch) — резолв 23 уникальных video ID → channelId (1 юнит)
2. `channels.list?forHandle=` — резолв 29 уникальных хэндлов → channelId (29 юнитов, по одному, т.к. `forHandle` не поддерживает batch)
3. Склейка всех источников (видео + хэндлы + 1 прямой channel ID) по настоящему channelId → **45 уникальных каналов** (было 61 ссылка). Нашлось 7 скрытых дублей, не видимых по тексту ссылки.
4. `channels.list` (batch, part=snippet,statistics,contentDetails) — подписчики/videoCount/дата создания/uploads playlist (1 юнит)
5. `playlistItems.list` — последние 10 роликов на канал (45 юнитов)
6. `videos.list` (batch) — просмотры этих 435 роликов (9 юнитов)

Квота этого прогона: ~85 юнитов.

## Результат
Полная таблица — `final_table.json`, сырые данные — `video_to_channel.json`, `handle_to_channel.json`, `master_unique_channels.json`, `full_stats.json`, `recent_videos.json`, `video_stats.json`.

## Скрытые дубли (нашлись только через API, не через текст ссылки)
- Chave do Ser — видео `E0j1J6aFmnc` + хэндл `@ChavedoSer`
- Explainer Chris ESP — видео `0pJluEimr68` + прямая ссылка на channel ID
- PLANTANDO RAIZ — видео `XHelCCTv7ZE` + хэндл `@PLANTANDORAIZ`
- Cuerpo sabio — два разных видео (`a1GXCsncLVU`, `RL0WWuuZUAk`)
- Dato Visual — видео `z3t2n-YKqPU` + хэндл `@Dato-Visual`
- Professor Guaxinim — два видео (`b8QSstByfak`, `ddyuxlSfXdg`) + хэндл `@Professor.Guaxinim`
- Comida Explicada — видео `vGE7gEcDbgE` + хэндл `@ComidaExplicada`
