# Домашнее задание №5 «Механизмы отложенного выполнения (Softirq, Tasklets, Workqueue)»

## Цель

Написать примеры работы с механизмами отложенного выполнения в ядре Linux.

## Задачи

* Написать Makefile с целями make, clean, format и check.
* Написать исходный код модулей.
* Собрать модули.
* Загрузить и проверить их работоспособность.

## Технические требования

1. Необходимо написать модули:

* ex_softirq.ko;
* ex_tasklets.ko;
* ex_workqueue.ko.

2. Код в модуле ядра должен демонстрировать работу с соответствующими механизмами,
   наиболее используемое API, возможно какие-то трюки.

3. Каждое ключевое действие должно быть напечатано в dmesg, допустим инициализация
   workqueue, постановка work в очередь и др.

## Формат сдачи

Ссылка на GitHub репозиторий с проектом HW_05_deferred exec_mech в проекте должен
быть Makefile (один общий или несколько) и исходные коды модулей.

## Критерии оценки

1. Makefile содержит цели: make, clean, format и check.
2. Модули ex_softirq.ko, ex_tasklets.ko, ex_workqueue.ko собираются.
3. Модули загружается.
4. В каждом модуле есть наиболее частые сценарии использования механизмов отложенного выполнения.
5. Каждый модуль выводит сообщения в dmesg о своих операциях.

## Компетенции

Работа с устройствами:

* уметь разрабатывать безопасные обработчики прерываний с учётом ограничений атомарного
  контекста и анализа их влияния на производительность;
* уметь анализировать структуру таблицы дескрипторов прерываний и обрабатывать прерывания,
  включая реальный сценарный анализ.

## Сборка и установка

Для корректной сборки модуля `ex_softirq.c` необходимо пропатчить и пересобрать ядро:
`patch -p0 < softirq.patch`.

Для постройки модулей используйте `make` и `sudo make install`. Далее загрузка
может выполняться командой modprobe.

Полный список команд `make`:

```
Available targets:
  all              - Build the kernel module (default)
  clean            - Clean build artifacts
  format           - Format source code with clang-format
  format-python    - Format Python source code with black
  check            - Test all modules
  check-softirq    - Test softirq module
  check-tasklet    - Test tasklet module
  check-workqueue  - Test workqueue module
  install          - Install module to system
  uninstall        - Remove module from system
```

## Тесты

Для автоматизации проверок модулей написан скрипт в каталоге checker. Вызывается вручную командой `checker/main.py MODULE_TYPE MODULE_NAME`, например `sudo ./checker/main.py tasklet tasklet`.

Также можно использовать цели в Makefile'е (`sudo make check`).
