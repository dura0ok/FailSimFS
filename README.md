# FailSimFS

#### Инструкция эмуляции сбоев файловой системы на которой запущен постгрес


1. Склонировать репозиторий
2. Запустить скрипт exps.sh
    - Ввести пароль
        - Дождаться завершения

3. Проверить что все работает(Поднят постгрес и физическая репликация)
    - psql -x -h localhost -d postgres -p 5432 -c "SELECT * FROM pg_stat_replication;"
    - psql -x -h localhost -d postgres -p 5433

4. Попробовать прогнать тест
    - Меняем example-config.json, вставляем туда какой нибудь config из директории examples
    - Выполним тестовый sql script \i queries/1.sql
    - Наблюдаем логи в /tmp/fuse/pg/bin/logfile или в /tmp/fuse/pglab/fake_postgres/bin/logfile и в самом psql
    - При каждом обновлении конфига файловая система сразу его перечитывает
    - Чтобы очистить все сбои - сделайте значение example config.json `{}`
    - Можно обьединить два конфига из examples, написать свои `custom_module`

***
На текущий момент поднимается сразу кластер с физической репликацией, 
думаю на возможностью настройки этого
