# Домашнее задание №3 «Структуры данных в ядре Linux"»

## Цель

Написать коллекцию примеров для работы со структурами данных в ядре Linux.

## Задачи

* Написать Makefile с целями make, clean, format и check.
* Написать исходный код модулей ().
* Собрать модули.
* Загрузить и проверить их работоспособность.

## Технические требования

1. Необходимо написать модули:

* ex_list.ko
* ex_queue.ko
* ex_bitmap.ko
* ex_rb_tree.ko
* ex_bin_search.ko

2. Код в модуле ядра должен демонстрировать работу с соответствующей структурой
данных, наиболее используемое API.

3. Каждое ключевое действие должно быть напечатано в dmesg, например добавление/удаление
элемента из списка или очереди и другие действия.

## Формат сдачи

Ссылка на GitHub репозиторий сс проектом HW_03_collection_of_example в проекте должен
быть Makefile (один общий или несколько) и исходные коды модулей.

## Критерии оценки

1. Makefile содержит цели: make, clean, format и check.
2. Модули ex_list.ko, ex_queue.ko, ex_bitmap.ko, ex_bin_tree.ko, ex_rb_tree.ko, ex_bin_search.ko собираются.
3. Модули загружаются.
4. Модуль выводит сообщение "module_name:init" в dmesg при insmod.
5. Модуль выводит сообщение "module_name:exit" в dmesg при rmmod.
* Корректные ограничения и валидация параметров.
* Удалось записать "Hello, World!".

## Компетенции

Создание и управление модулями ядра:

* знать структуру и формат модулей ядра, их загрузку и выгрузку;
* уметь применять буфер сообщений ядра (dmesg);
* уметь передавать параметры в модуль;
* уметь писать Makefile с указанием пути к исходникам ядра.

# Результат

Реализованы следующие модули:

* ex_list.ko - операции со списком;
* ex_queue.ko - операции с очередью;
* ex_rb_tree.ko - операции с красно-чёрным деревом;
* ex_bitmap.ko - операции с битовой картой;
* ex_bin_search.ko - двоичный поиск в массиве списков;
* ex_bin_tree.ko - реализация двоичного дерева на основе списка;
* ex_stack.ko - реализация стека на основе списка;
* ex_brackets.ko - задача №1 из лайв-кодинга по спискам;
* ex_stack2.ko - задача №2 из лайв-кодинга по спискам.

## Сборка и установка

Для постройки модулей используйте `make` и `sudo make install`. Далее загрузка
может выполняться командой modprobe.

Полный список команд `make`:

```
Available targets:
  all              - Build the kernel module (default)
  clean            - Clean build artifacts
  format           - Format source code with clang-format
  check            - Test all modules
  check-list       - Test list module
  check-queue      - Test queue module
  check-rb_tree    - Test rb_tree module
  check-bitmap     - Test bitmap module
  check-bin_search - Test bin_search module
  check-bin_tree   - Test bin_tree module
  check-stack      - Test stack module
  check-brackets   - Test brackets module
  check-stack2     - Test stack2 module
  install          - Install module to system
  uninstall        - Remove module from system
```

## Интерфейс

Все модули имеют одинаковый интерфейс через параметры в sysfs
(/sys/module/MODULE_NAME/parameters/):

* cmd - строка с командой для модуля;
* value/index - аргумент команды.

В ex_stack2 используется только cmd, аргумент идёт после push: `push N`.

В ex_brackets входная строка подаётся в строковый параметр input.

Для записи параметров требуются root права.

Либо используйте tee: `echo print | sudo tee /sys/module/ex_list/parameters/cmd`.

## Тесты

Для автоматизации проверок модулей написан скрипт в каталоге checker. Вызывается вручную командой `checker/main.py MODULE_TYPE MODULE_NAME`, например `sudo ./checker/main.py stack ex_stack`.

Также можно использовать цели в Makefile'е (`sudo make check-list`).
