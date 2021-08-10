import threading
from urllib.request import urlretrieve

import requests
import os
import datetime
import logging


class DownloadThread(threading.Thread):
    """
    @author jason
    @desc download class inherit from thread for easy show thread name and time
    @date 2020/7/14
    """
    def __init__(self, url, start_pos, end_pos, f):
        """ construct of current class

        :param url: the target url for download
        :param start_pos: start position of current download thread
        :param end_pos: end position of current download thread
        :param f: file handler (IO low level)

        """

        super(DownloadThread, self).__init__()
        self.url = url
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.fd = f

    def download(self):
        """ download part of the target file by using Range attribute of request head

        :return: None
        """
        logging.debug('start thread:%s at %s' % (self.getName(), get_current_time()))
        headers = {'Range': 'bytes=%s-%s' % (self.start_pos, self.end_pos)}
        res = requests.get(self.url, headers=headers)
        self.fd.seek(self.start_pos)
        self.fd.write(res.content)

        logging.debug('Stop thread:%s at%s' % (self.getName(), get_current_time()))
        self.fd.close()

    def run(self):
        """ override run method

        :return: None
        """
        self.download()


def get_current_time():
    """ get current time of system

    :return: current time
    """
    return datetime.datetime.now()


def download_file_multi_thread(url, directory=None):
    """ download the target file with 8 threads

    :param url: target file url
    :param directory: directory where you want to put the downloading file
    :return: 0 if success, other if failed, 1 for download size didn't match
    """

    ret = 0

    #return 1 # test code

    file_name = url.split('/')[-1]
    file_size = int(requests.head(url).headers['Content-Length'])
    logging.debug('%s file size:%s' % (file_name, file_size))

    thread_num = 8
    threading.BoundedSemaphore(thread_num)  # allowed number of thread
    step = file_size // thread_num
    mtd_list = []
    start = 0
    end = -1

    tmp_file_name = file_name + "_tmp"
    if directory is not None:
        tmp_file_name = directory + "/" + tmp_file_name

    # this operation will refresh the temp file if it exists
    tmp_file = open(tmp_file_name, 'w')
    tmp_file.close()
    mtd_list = []

    # open temp file then download with multi thread
    with open(tmp_file_name, 'rb+')as f:
        file_no = f.fileno()
        while end < file_size - 1:
            start = end + 1
            end = start + step - 1
            if (end + thread_num - 1) >= file_size - 1:
                end = file_size - 1
            logging.debug('Start:%s,end:%s' % (start, end))
            dup = os.dup(file_no)
            fd = os.fdopen(dup, 'rb+', -1)
            t = DownloadThread(url, start, end, fd)
            t.start()
            mtd_list.append(t)
        for i in mtd_list:
            i.join()
        f.close()

    # check the size of the file
    current_file_size = os.path.getsize(tmp_file_name)
    if current_file_size != file_size:
        logging.error("download failed,file size not match, original is %d, %d downloaded"
                      % (file_size, current_file_size))
        ret = 1
        return ret

    if directory is not None:
        file_name = directory + "/" + file_name

    # remove the file if exists
    if os.path.exists(file_name):
        os.remove(file_name)

    # rename the temp name to normal
    os.rename(tmp_file_name, file_name)

    ret = 0
    return ret


def download_callback(block_number, block_size, data_size):
    """ callback for urlretrieve

    :param block_number: number of block
    :param block_size: size of one block
    :param data_size: total size of target file
    :return: none
    """
    per = 100 * block_number * block_size / data_size

    if per > 100:
        per = 100

    logging.debug('total size %d, %.2f%% \r' % (data_size, per))


def normal_download(url, directory):
    """ use normal method to download one file

    :param url: url of target file
    :param directory: sub folder at execute path, like download at where this program run
    :return: 0 if success, other if error, 1 for urlretrieve execute error
    """
    original_name = url.split('/')[-1]
    tmp_file_name = directory + "/" + original_name + "_tmp2"
    file_name = directory + "/" + original_name

    file_size = int(requests.head(url).headers['Content-Length'])
    logging.debug('%s file size:%s' % (original_name, file_size))

    try:
        urlretrieve(url, tmp_file_name, download_callback)
    except Exception as e:
        logging.error(e)
        return 1

    current_file_size = os.path.getsize(tmp_file_name)
    if current_file_size != file_size:
        logging.error("download failed,file size not match, original is %d, %d downloaded"
                      % (file_size, current_file_size))
        ret = 1
        return ret

    # remove the file if exists
    if os.path.exists(file_name):
        os.remove(file_name)
u
    # rename the temp name to normal
    os.rename(tmp_file_name, file_name)

    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.NOTSET)
    start_time = datetime.datetime.now()
    # test URL
    test_url = 'https://bulkdata.uspto.gov/data/patent/grant/redbook/fulltext/2020/ipg200107.zip'

    download_file_multi_thread(test_url, "downloaded")
    end_time = datetime.datetime.now()
    time_passed = end_time - start_time
    logging.debug(time_passed)
