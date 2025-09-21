# Домашнее задание №6 «API таймеров в ядре Linux»

## Цель

Написать модуль ядра с использованием с использованием "timer_list".

## Задачи

* Написать Makefile с целями make, clean, load, unload, format и check.
* Написать исходный код модуля.
* Собрать модуль.
* Загрузить и проверить его работоспособность

## Технические требования

Необходимо написать модуль ядра, с использованием API таймеров. Каждые 30 секунд
должен вызваться callback таймера, который будет выводить сообщение
"min=%d: Hello, timer!\n". После 5 минуты ничего выводить не нужно.

## Формат сдачи

Ссылка на GitHub репозиторий с проектом HW_06_timer в проекте должен быть Makefile
и исходный код модуля.

## Критерии оценки

1. Makefile содержит цели: make, clean, load, unload, format и check.
2. Модуль собирается.
3. Модуль загружается.
4. Модуль выводит сообщение "min=%d: Hello, timer!" в dmesg каждые пол минуты,
   но не более 5 минут.

## Компетенции

1. Создание и управление модулями ядра:
   * уметь разрабатывать модули с использованием API таймеров для периодических
     или отложенных задач.

2. Управление процессами и потоками:
   * уметь связывать работу прерываний таймера с планировщиком задач.

3. Работа с устройствами:
   * понимать принципы работы таймеров в ядре Linux, включая выбор подходящего
     таймера в зависимости от требований к точности и контексту выполнения.

## Сборка и установка

Для постройки модулей используйте `make` и `sudo make install`. Далее загрузка
может выполняться командой modprobe (или `sudo make load`/`sudo make unload`).

Полный список команд `make`:

```
Available targets:
  all              - Build the kernel module (default)
  clean            - Clean build artifacts
  format           - Format source code with clang-format
  format-python    - Format Python source code with black
  check            - Test all modules
  check-timer      - Test timer module
  install          - Install module to system
  uninstall        - Remove module from system
  load             - Build and load module

```

## Тесты

Для автоматизации проверок модулей написан скрипт в каталоге checker. Вызывается вручную командой `checker/main.py MODULE_TYPE MODULE_NAME`, например `sudo ./checker/main.py timer timer`.

Также можно использовать цели в Makefile'е (`sudo make check`).
