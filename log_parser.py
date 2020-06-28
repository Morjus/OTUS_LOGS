import os
import glob
import re
import collections
import itertools


class Parser:
    logs = None
    logs_with_num = None
    cur_log = None

    def __init__(self, path_to):
        self.directory = path_to
        self.logs = self.__get_all_logs()

    def __get_all_logs(self):
        """
        Ищет файлы с расширенмем .log в укзанной директории
        :return: возваращает список с путями до найденных файлов
        """
        if not os.path.isfile(self.directory):
            res = {}
            print("Getting all logs...")
            logs = glob.glob(f"{self.directory}*.log")
            try:
                if logs:
                    # print("Got these logs:")
                    for position, log in enumerate(logs, 1):
                        # print(position, log)
                        res[position] = log
                self.logs_with_num = res
                return logs
            except Exception as error:
                print(error)
        else:
            self.cur_log = self.directory

    def parse_all_logs(self):
        for log in self.logs:
            self.cur_log = log
            self.total_requests()
            self.total_get_req()
            self.total_post_req()
            self.ten_active_ips()
            self.ten_most_long_req()
            self.ten_most_client_err()
            self.ten_most_server_err()

    def parse_log(self):
        self.total_requests()
        self.total_get_req()
        self.total_post_req()
        self.ten_active_ips()
        self.ten_most_long_req()
        self.ten_most_client_err()
        self.ten_most_server_err()

    def __parse(self, log, pattern):
        counter = 0
        pattern = r"{}".format(pattern)
        with open(log, "r") as f:
            for i, l in enumerate(f):
                if re.findall(pattern, l):
                    counter += 1
            return counter

    def __simple_sort(self, sub_li):
        sub_li.sort(key=lambda x: int(x[4]))
        return sub_li

    def ten_most_long_req(self, num=10):
        """
        топ 10 самых долгих запросов, должно быть видно метод, url, ip, время запроса
        :return:
        """
        pattern = r'(\d+\.\d+\.\d+\.\d+) - - (\[.+\]) "(GET|POST) (.+) HTTP/1.1" \d+ (\d+) "(.+)" "'
        info = []
        with open(self.cur_log, "r") as f:
            for i, l in enumerate(f):
                if re.findall(pattern, l):
                    info.append(re.findall(pattern, l)[0])
        res = self.__simple_sort(info)
        top_times = res[-num:]
        print(f"Top of most long requests in {os.path.split(self.cur_log)[1]}:")
        for each in top_times:
            print(each)

    def ten_active_ips(self, num=10):
        """
        топ 10 IP адресов, с которых были сделаны запросы
        :return:
        """
        pattern = r"^(\d+\.\d+\.\d+\.\d+)"
        ips = []
        with open(self.cur_log, "r") as f:
            for i, l in enumerate(f):
                if re.findall(pattern, l):
                    ips.append(re.findall(pattern, l)[0])
        top_ips = collections.Counter(ips)
        if len(top_ips) > num:
            print(f"Top requests IPs: \n{dict(itertools.islice(top_ips.items(), num))}")
        else:
            print(f"Top requests IPs: \n{dict(collections.Counter(ips))}")

    def total_requests(self):
        pattern = r"^(\d+\.\d+\.\d+\.\d+)"  # Ip в начале строки
        counter = self.__parse(self.cur_log, pattern)
        print(f"Total requests in {os.path.split(self.cur_log)[1]}: {counter}")
        return counter

    def total_get_req(self):
        """
        количество запросов по типу: GET - 20, POST - 10 и т.п.
        :return:
        """
        pattern = r'] "GET'
        counter = self.__parse(self.cur_log, pattern)
        print(f"Total GET requests in {os.path.split(self.cur_log)[1]}: {counter}")
        return counter

    def total_post_req(self):
        """
        количество запросов по типу: GET - 20, POST - 10 и т.п.
        :return:
        """
        pattern = r'] "POST'
        counter = self.__parse(self.cur_log, pattern)
        print(f"Total POST requests in {os.path.split(self.cur_log)[1]}: {counter}")
        return counter

    def ten_most_client_err(self, num=10):
        """
        топ 10 запросов, которые завершились клиентской ошибкой, должно быть видно метод, url, статус код, ip адрес
        :return:
        """
        pattern = r'(\d+\.\d+\.\d+\.\d+) - - (\[.+\]) "(GET|POST) (.+) HTTP/1.1" (4\d+) \d+ "(.+)" "'
        info = []
        with open(self.cur_log, "r") as f:
            for i, l in enumerate(f):
                if re.findall(pattern, l):
                    info.append(re.findall(pattern, l)[0])
        res = self.__simple_sort(info)
        top_times = res[-num:]
        print(f"Top of most bad client requests in {os.path.split(self.cur_log)[1]}:")

        count = collections.Counter()
        for ip, time, req, path, code, url in res:
            count[(ip, req, code, path, url)] += 1
        top_failed_req = count
        if len(top_failed_req) > num:
            final = dict(itertools.islice(count.items(), num))
            print(f"Top client fails in {os.path.split(self.cur_log)[1]}: \n")
            for each in final:
                print(each)
        else:
            print(f"Top client fails in {os.path.split(self.cur_log)[1]}: \n")
            for each in dict(count).items():
                print(each)

    def ten_most_server_err(self, num=10):
        """
        топ 10 запросов, которые завершились ошибкой со стороны сервера, должно быть видно метод, url, статус код, ip адрес
        :return:
        """
        pattern = r'(\d+\.\d+\.\d+\.\d+) - - (\[.+\]) "(GET|POST) (.+) HTTP/1.1" (5\d+) \d+ "(.+)" "'
        info = []
        with open(self.cur_log, "r") as f:
            for i, l in enumerate(f):
                if re.findall(pattern, l):
                    info.append(re.findall(pattern, l)[0])
        res = self.__simple_sort(info)
        top_times = res[-num:]
        print(f"Top of most bad client requests in {os.path.split(self.cur_log)[1]}:")

        count = collections.Counter()
        for ip, time, req, path, code, url in res:
            count[(ip, req, code, path, url)] += 1
        top_failed_req = dict(count)
        if len(top_failed_req) > num:
            print(f"Top failed server fails in {os.path.split(self.cur_log)[1]}: \n{dict(itertools.islice(top_failed_req.items(), num))}")
        else:
            print(f"Top failed server fails in {os.path.split(self.cur_log)[1]}: \n{top_failed_req}")


if __name__ == "__main__":
    path = input("Please specify path to directory or file: ")
    logs = Parser(path)
    logs.parse_log()


