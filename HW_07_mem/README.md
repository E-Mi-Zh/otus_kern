# Домашнее задание №7 «Сравнение различных функций выделения памяти»

## Цель

* Написать модули ядра, использующие механизмы управления памятью (kmem_cache, mempool, kmalloc/vmalloc);
* Написать демонстрационные модули, сравнивающий kmalloc, vmalloc и kmem_cache, mempool, get_page.

## Задачи

* Написать Makefile с целями make, clean, load, unload, format и check.
* Написать модули ядра.
* Собрать модули ядра
* Загрузить и проверить их работоспособность

## Технические требования

1. Необходимо написать модули:

* ex_kmalloc.ko
* ex_vmalloc.ko
* ex_kmem_cache.ko
* ex_mempool.ko
* ex_get_page.ko

2. При работе с памятью в ядре linux, необходимо следить за тем чтобы не было
   утечек, поэтому вся выделенная память должна быть освобождена.

3. Сравнить аллокаторы требуется по нескольким критериям:

    * Максимальное количество выделенной памяти за раз
    * Время аллокации
    * Тип возвращаемой памяти (физическая или виртуальная)

4. Каждый модуль должен перед аллокацией выводить сообщение в dmesg в формате:

```
"kmalloc: %d byte\n",

"kmalloc: SUCCSESS\n" или "kmalloc: FAIL , err_msg = %s\n"
```

Если удалось выделить, то

```
"kmalloc: %d byte, %d ms, type: %s\n"
```

5. На основе полученных результатов надо сравнить все аллокаторы между собой по переменым из 3 пункта. Результаты сравнения записать в файл `diff_aloc.pdf`, результаты аллокаций можно прикреплять картинками сообщений из dmesg.

## Формат сдачи

Ссылка на GitHub репозиторий с проектом HW_07_mem в проекте должен
быть Makefile (один общий или несколько) и исходные коды модулей.

## Критерии оценки

1. Makefile содержит цели: make, clean, format и check.
2. Модули ex_kmalloc.ko, ex_vmalloc.ko, ex_kmem_cache.ko, ex_mempool.ko, ex_get_page.ko собираются
3. Модули загружается
4. В репозитории содержится не пустой файл diff_aloc.pdf сравнения аллокаторов памяти
5. В коде есть обработка ошибок.
6. Устранены все утечки памяти.


## Компетенции

1. Использование структур данных и алгоритмов
   * знать и применять методы оптимизации работы со структурами данных, включая подходы к минимизации времени выполнения и использования памяти
2. Работа с памятью
   * уметь применять ""mempool"" и оптимизировать размеры пулов

## Сборка и установка

Для постройки модулей используйте `make` и `sudo make install`. Далее загрузка
может выполняться командой modprobe.

Полный список команд `make`:

```
Available targets:
  all               - Build the kernel module (default)
  clean             - Clean build artifacts
  format            - Format source code with clang-format
  format-python     - Format Python source code with black
  check             - Test all modules
  check-kmalloc     - Test kmalloc module
  check-vmalloc     - Test vmalloc module
  check-kmem_cache  - Test kmem_cache module
  check-mempool     - Test mempool module
  check-get_page    - Test get_page module
  install           - Install module to system
  uninstall         - Remove module from system
  load-kmalloc      - Build and load kmalloc module
  unload-kmalloc    - Unload kmalloc module
  load-vmalloc      - Build and load vmalloc module
  unload-vmalloc    - Unload vmalloc module
  load-kmem_cache   - Build and load kmem_cache module
  unload-kmem_cache - Unload kmem_cache module
  load-mempool      - Build and load mempool module
  unload-mempool    - Unload mempool module
  load-get_page     - Build and load get_page module
  unload-get_page   - Unload get_page module
```

## Тесты

Для автоматизации проверок модулей написан скрипт в каталоге checker. Вызывается вручную командой `checker/main.py MODULE_TYPE MODULE_NAME`, например `sudo ./checker/main.py tasklet tasklet`.

Также можно использовать цели в Makefile'е (`sudo make check`).
