import hashlib


def md5_encrypt_32(plaintext: str) -> str:
    """
    MD5加密函数,生成32位十六进制字符串
    
    Args:
        plaintext: 明文字符串
        
    Returns:
        32位MD5加密后的十六进制字符串
    """
    if not plaintext or not plaintext.strip():
        return ""
    md5 = hashlib.md5()
    md5.update(plaintext.encode('utf-8'))
    return md5.hexdigest()


md5_encrypt32 = md5_encrypt_32
