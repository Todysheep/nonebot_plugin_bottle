import secrets
import string

def generate_password(length=12):
    # 定义密码字符集
    characters = string.ascii_letters + string.digits + string.punctuation
    # 使用secrets.choice来随机选择字符生成密码
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password