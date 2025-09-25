import ftplib
import os


class FtpCore:
    @staticmethod
    def create_ftp():
        """
        创建FTP实例
        """
        ftp_instance = ftplib.FTP()
        ftp_instance.encoding = "gbk"
        return ftp_instance

    @staticmethod
    def ftp_connection(ftp_instance: ftplib.FTP, host: str, port: int):
        """
        连接FTP
        """
        return ftp_instance.connect(host, port)

    @staticmethod
    def ftp_login(ftp_instance: ftplib.FTP, user: str, password: str):
        """
        登陆ftp
        """
        return ftp_instance.login(user, password)

    @staticmethod
    def close_ftp(ftp_instance: ftplib.FTP):
        """
        关闭ftp
        """
        return ftp_instance.close()

    @staticmethod
    def get_working_dir(ftp_instance: ftplib.FTP):
        """
        获取当前工作目录
        """
        return ftp_instance.pwd()

    @staticmethod
    def change_working_dir(ftp_instance: ftplib.FTP, working_dir: str):
        """
        切换工作目录
        """
        return ftp_instance.cwd(working_dir)

    @staticmethod
    def get_list(ftp_instance: ftplib.FTP):
        """
        获取当前工作目录下的全部文件及文件夹
        """
        try:
            raw_data = []

            def callback(line):
                raw_data.append(line)

            ftp_instance.retrlines("LIST", callback)
        except ftplib.error_perm as e:
            raise ValueError("权限错误或命令不支持：{e}")
        except Exception as e:
            raise ValueError("发生错误：{}".format(e))

        return raw_data

    @staticmethod
    def get_nlst(ftp_instance: ftplib.FTP):
        """
        获取当前工作目录下的全部文件及文件夹
        """
        return ftp_instance.nlst()

    @staticmethod
    def ftp_rename(ftp_instance: ftplib.FTP, old_name: str, new_name: str):
        """
        重命名指定文件/文件夹
        """
        return ftp_instance.rename(old_name, new_name)

    @staticmethod
    def ftp_upload_file(ftp_instance: ftplib.FTP, src_path: str, file_name: str):
        """
        向FTP指定目录上传文件
        """
        bufsize = 1024
        fp = open(src_path, "rb")
        ftp_instance.storbinary("STOR " + file_name, fp, bufsize)
        ftp_instance.set_debuglevel(0)
        fp.close()
        return FtpCore.get_path(ftp_instance, file_name)

    @staticmethod
    def ftp_upload_dir(ftp_instance: ftplib.FTP, src: str, folder_name: str):
        """
        向FTP指定目录上传文件夹
        """
        if not os.path.isdir(src):
            raise ValueError("{}非有效目录".format(src))

        if not FtpCore.is_dir(ftp_instance, folder_name):
            res = FtpCore.create_dir(ftp_instance, folder_name)
            if not res:
                raise ValueError("工作目录创建失败，请检查FTP连接")

        ftp_instance.cwd(folder_name)

        upload_name_list = os.listdir(src)
        for name in upload_name_list:
            local_path = os.path.join(src, name)
            if os.path.isdir(local_path):
                FtpCore.ftp_upload_dir(ftp_instance, local_path, name)
            else:
                FtpCore.ftp_upload_file(ftp_instance, local_path, name)

        ftp_instance.cwd("..")
        return FtpCore.get_path(ftp_instance, folder_name)

    @staticmethod
    def ftp_delete_file(ftp_instance: ftplib.FTP, file_name: str):
        """
        删除文件
        """
        return ftp_instance.delete(file_name)

    @staticmethod
    def ftp_delete_dir(ftp_instance: ftplib.FTP, dir_name: str):
        """
        删除文件夹
        """
        ftp_instance.cwd(dir_name)
        name_list = ftp_instance.nlst()
        for name in name_list:
            if FtpCore.is_dir(ftp_instance, name):
                FtpCore.ftp_delete_dir(ftp_instance, name)
            else:
                FtpCore.ftp_delete_file(ftp_instance, name)
        ftp_instance.cwd("..")
        ftp_instance.rmd(dir_name)

    @staticmethod
    def ftp_download_file(ftp_instance: ftplib.FTP, remote_path, local_path: str):
        bufsize = 1024
        fp = open(local_path, "wb")
        ftp_instance.retrbinary(f"RETR {remote_path}", fp.write, bufsize)
        ftp_instance.set_debuglevel(0)
        fp.close()
        return local_path

    @staticmethod
    def ftp_download_dir(ftp_instance: ftplib.FTP, remote_path, local_path: str):
        if not os.path.isdir(local_path):
            os.makedirs(local_path)
        ftp_instance.cwd(remote_path)
        name_list = ftp_instance.nlst()
        for name in name_list:
            local_item_path = os.path.join(local_path, name)
            if not FtpCore.is_dir(ftp_instance, name):
                FtpCore.ftp_download_file(ftp_instance, os.path.join(remote_path, name), local_item_path)
            else:
                FtpCore.ftp_download_dir(ftp_instance, os.path.join(remote_path, name), local_item_path)
        ftp_instance.cwd("..")
        return local_path

    @staticmethod
    def get_path(ftp_instance: ftplib.FTP, name: str):
        """
        获取当前工作目录下的文件/文件夹路径
        """
        pwd = ftp_instance.pwd()
        return os.path.join(pwd, name)

    @staticmethod
    def generate_name(ftp_instance, rename: str):
        """
        为重名文件/文件夹生成副本
        """
        base, extension = os.path.splitext(rename)
        counter = 1
        new_name = f"{base}({counter}){extension}"
        while new_name in FtpCore.get_nlst(ftp_instance):
            counter += 1
            new_name = f"{base}({counter}){extension}"
        return new_name

    @staticmethod
    def is_dir(ftp_instance: ftplib.FTP, dir_name: str):
        """
        判断FTP服务器中的指定路径是否存在
        """
        current_dir = ftp_instance.pwd()
        try:
            ftp_instance.cwd(dir_name)
            ftp_instance.cwd(current_dir)
            return True
        except ftplib.error_perm as e:
            return False

    @staticmethod
    def create_dir(ftp_instance: ftplib.FTP, dir_name: str):
        """
        在FTP当前目录下新建文件夹
        """
        try:
            ftp_instance.mkd(dir_name)
            return FtpCore.get_path(ftp_instance, dir_name)
        except ftplib.error_perm as e:
            raise ValueError(e)
