#!/usr/bin/python3
import os
import filecmp
import unittest

from settings import CHUNK_SIZE, TMP_DIR
from sort import sort_with_chunks
from generator import generate_file

MB = 1 * 1024 * 1024


class ChunkTestCase(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(TMP_DIR):
            os.system("mkdir {}".format(TMP_DIR))
        self.removeChunks()

    def checkChunksNumber(self, num):
        self.assertEqual(len(os.listdir(TMP_DIR)), num)

    def removeChunks(self):
        if len(os.listdir(TMP_DIR)) > 0:
            os.system("rm {}*".format(TMP_DIR))

    def tearDown(self):
        self.removeChunks()


class TestBorderConditions(ChunkTestCase):
    def test_empty_file(self):
        """ файл с пустой строкой """
        sort_with_chunks("test_data/empty.txt", CHUNK_SIZE, TMP_DIR, False)
        self.assertTrue(filecmp.cmp("result.txt", "test_data/empty.txt"))
        self.checkChunksNumber(1)

    def test_single_line(self):
        """ файл с одной строкой """
        sort_with_chunks("test_data/single_line.txt", CHUNK_SIZE, TMP_DIR, False)
        self.assertTrue(filecmp.cmp("result.txt", "test_data/single_line.txt"))
        self.checkChunksNumber(1)


class TestSorting(ChunkTestCase):
    def test_default_file(self):
        sort_with_chunks("test_data/default.txt", CHUNK_SIZE, TMP_DIR, False)
        self.assertTrue(filecmp.cmp("result.txt", "test_data/default_res.txt"))
        self.checkChunksNumber(1)

    def test_sorting_with_empty_lines(self):
        sort_with_chunks("test_data/with_empty_lines.txt", CHUNK_SIZE, TMP_DIR, False)
        self.assertTrue(filecmp.cmp("result.txt", "test_data/with_empty_lines_res.txt"))
        self.checkChunksNumber(1)

    def test_second_chunk_border(self):
        sort_with_chunks("test_data/one_chunk_border.txt", CHUNK_SIZE, TMP_DIR, False)
        self.checkChunksNumber(1)
        self.removeChunks()

        sort_with_chunks("test_data/two_chunk_border.txt", CHUNK_SIZE, TMP_DIR, False)
        self.checkChunksNumber(2)

    def test_random_string_length_chunk_border(self):
        """ сортировка файла со случайной длиной строк - граничный случай от 1 к 2 chunks """
        sort_with_chunks("test_data/rnd_border_chunk1.txt", CHUNK_SIZE, TMP_DIR, False)
        self.checkChunksNumber(1)
        self.removeChunks()

        sort_with_chunks("test_data/rnd_border_chunk2.txt", CHUNK_SIZE, TMP_DIR, False)
        self.checkChunksNumber(2)


class TestLongStrings(ChunkTestCase):
    def test_1_long_string_in_file(self):
        """ проверка сортировки файла, где есть 1 строка длиннее чем chunk_size """
        sort_with_chunks("test_data/long_string_1.1mb.txt", CHUNK_SIZE, TMP_DIR, False)
        self.checkChunksNumber(2)

    def test_2_long_strings_in_file(self):
        """ проверка сортировки файла, в котором 2 строки длиннее чем chunk_size """
        sort_with_chunks("test_data/long_string_x2.txt", CHUNK_SIZE, TMP_DIR, False)
        self.checkChunksNumber(3)


class TestGenerator(unittest.TestCase):
    def setUp(self):
        self.emptyTmpDir()

    def tearDown(self):
        self.emptyTmpDir()

    def emptyTmpDir(self):
        if len(os.listdir(TMP_DIR)) > 0:
            os.system("rm {}*".format(TMP_DIR))

    def test_const_length(self):
        self.emptyTmpDir()
        fname = "{}/10x100.txt".format(TMP_DIR)
        generate_file(10, 100, fname=fname, random_length=False)
        with open(fname) as f:
            for st in f:
                self.assertTrue(len(st) == 100)

    def test_random_length(self):
        self.emptyTmpDir()
        fname = "{}/10x100_random.txt".format(TMP_DIR)
        generate_file(10, 100, fname=fname, random_length=True)

        with open(fname) as f:
            for st in f:
                self.assertTrue(len(st) <= 100)


if __name__ == '__main__':
    unittest.main()

"""
# border chunksize for 10x100 file
./joom.py --file sort_10_100_1523474547.txt --chunksize 1088 --tmpfiles --verbose ; ls -la tmp # 1 chunk
./joom.py --file sort_10_100_1523474547.txt --chunksize 1089 --tmpfiles --verbose ; ls -la tmp # 2 chunks


# тесты со строками, превышающими размер chunk 1мб
./joom.py --file long_string_1.1mb.txt --tmpfiles; ls -la tmp 
total 1084
drwxrwxr-x 2 zak zak    4096 апр.  11 22:50 .
drwxrwxr-x 4 zak zak    4096 апр.  11 22:43 ..
-rw-rw-r-- 1 zak zak       0 апр.  11 22:50 chunk_0.txt
-rw-rw-r-- 1 zak zak 1100009 апр.  11 22:50 chunk_1.txt

# 2 строки превышают размер chunk
./joom.py --file long_string_x2.txt --tmpfiles; ls -la tmp 
total 2164
drwxrwxr-x 2 zak zak    4096 апр.  11 22:50 .
drwxrwxr-x 4 zak zak    4096 апр.  11 22:43 ..
-rw-rw-r-- 1 zak zak       2 апр.  11 22:50 chunk_0.txt
-rw-rw-r-- 1 zak zak 1100001 апр.  11 22:50 chunk_1.txt
-rw-rw-r-- 1 zak zak 1100008 апр.  11 22:50 chunk_2.txt
zak@zak-Lenovo:~/work/joom$ 

# тесты генератора
"""
