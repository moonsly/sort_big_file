# sort_big_file #

Сортировка большого файла со строками, который не помещается в ОЗУ

### Реализация ###

Для сортировки входной файл за один проход разбивается на chunks (размера chunksize, по умолчанию 1 Мб),
каждый chunk сортируется с помощью heapsort и записывается во временный файл.
Строки из входного файла добавляются по одной в кучу для chunk, сложность O(logN).
После завершения прохода по входному файлу, отсортированные chunks объединяются в общий список за один проход O(N),
с помощью heapq.merge.

Генератор generator.py позволяет сгенерировать входной файл с постоянной или переменной (случайной len <= size) длиной строк.

### Установка и запуск ###

Для работы скрипта необходим Python 3.5.
Файл для сортировки по умолчанию - default.txt, результат сортировки будет записан в result.txt.

Пример запуска сортировки из командной строки:

$ python3 ./sort.py --file test_data/rnd_border_chunk2.txt --verbose

Свободный объем ОЗУ: 4796649472 байт, размер chunk: 1048576 байт
Обработано 1 chunks, осталось времени ~ 0.00 c
Всего 2 chunks создано за 0.05 c. Начинаем merge
Merge занял 0.01 c
Сортировка 18742 строк завершена за 0.07 с

### Тестирование ###

python3 ./tests.py 
..........
----------------------------------------------------------------------
Ran 10 tests in 0.274s

OK

### Контакты автора ###

moonsly@gmail.com