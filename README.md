YaMDb
https://github.com/vitalino13/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg

YaMDb - база данных, которая собирает отзывы о различных произведениях. Произведения делятся на категории: «Книги», «Фильмы», «Музыка». При необходимости, список категорий может быть расширен администратором. Пользователи могут оставлять рецензии на произведения и ставить оценки.
Проект реализован на Django и DjangoRestFramework. Доступ к данным реализован через API-интерфейс. Документация к API написана с использованием Redoc.

Особенности реализации

Проект завернут в Docker-контейнеры;
Реализован workflow через GitHubActions: тестирование, обновление образа на DockerHub, автоматический деплой на сервер, отправление сообщения в Telegram об успешном выполнении всех шагов workflow;
Проект развернут на сервере ???



Развертывание проекта

Развертывание на локальном сервере

Установите на сервере docker и docker-dompose.
Создайте файл /infra/.env. Шаблон для заполнения файла нахоится в /infra/.env.example.
Выполните команду docker-compose up -d --buld.
Выполните миграции docker-compose exec web python manage.py migrate.
Создайте суперюзера docker-compose exec web python manage.py createsuperuser.
Соберите статику docker-compose exec web python manage.py collectstatic --no-input.
При необходимости заполните базу docker-compose exec web python manage.py loaddata fixtures.json.
Документация к API находится по адресу: http://localhost/redoc/.


Настройка проекта для развертывания на удаленном сервере

Установите на сервере docker и docker-dompose.
Локально отредактируйте файл infra/nginx.conf, в строке server_name впишите IP-адрес сервера.
Скопируйте файлы docker-compose.yaml и nginx/defult.conf из директории infra на сервер:


    scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yaml
    scp default.conf <username>@<host>:/home/<username>/nginx/default.conf



Добавьте в Secrets GitHub следующие переменные:


    DB_ENGINE=django.db.backends.postgresql
    DB_NAME=имя базы данных postgres
    DB_USER=пользователь бд
    DB_PASSWORD=пароль
    DB_HOST=db
    DB_PORT=5432

    DOCKER_PASSWORD=пароль от DockerHub
    DOCKER_USERNAME=имя пользователя

    SECRET_KEY=секретный ключ проекта django

    USER=username для подключения к серверу
    HOST=IP сервера
    PASSPHRASE=пароль для сервера, если он установлен
    SSH_KEY=ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)

    TELEGRAM_TO=ID чата, в который придет сообщение
    TELEGRAM_TOKEN=токен вашего бота



Выполните команды:


    git add .
    git commit -m 'ваш комментарий'
    git push



После выполнения команды git push и выполнения всех шагов workflow, проект будет развернут на удаленном сервере.
Для окончательной настройки, зайдите на уделенный сервер и выполните миграции, создайте суперюзера, соберите статику и заполните базу (см. шаги 4-7 из описания развертывания проекта на локальном сервере).


Автор
Виталий Асташкевич