# Задача 3 #

Написать клиент-серверную систему, работающую по следующему алгоритму:
  - Сервер держит открытыми порты 8000 и 8001.
  - При запуске клиент выбирает для себя уникальный идентификатор.
  - Клиент подключается к серверу к порту 8000, передает ему свой идентификатор и получает от сервера уникальный код.
  - Клиент подключается к серверу к порту 8001 и передает произвольное текстовое сообщение, свой идентификатор и код, полученный на шаге 2.
  - Если переданный клиентом код не соответствует его уникальному идентификатору, сервер возвращает клиенту сообщение об ошибке.
  - Если код передан правильно, сервер записывает полученное сообщение в лог.

Сервер должен поддерживать возможность одновременной работы с хотя бы 50 клиентами.
Для реализации взаимодействия между сервером и клиентом системы допускается (но не требуется) использование высокоуровнего протокола (например, HTTP).

Запуск:

  ``` python3 server.py ```

  ``` python3 client.py ```