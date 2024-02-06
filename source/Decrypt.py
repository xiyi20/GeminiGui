import base64
from Crypto.Cipher import AES

class Decrypt:
    def paddigits(self,se,lens=0):
        if lens<=0:
            lens=1;
        while len(se)%lens!=0:
            se+='\0'
        return se.encode(encoding='utf-8')
    def decrypt(self,data,key):
        aes=AES.new(self.paddigits(key,16), AES.MODE_ECB)
        #优先逆向解密base64成bytes
        b64=base64.decodebytes(self.paddigits(data,16))
        #执行解密密并转码返回str
        decrypted=str(aes.decrypt(b64),encoding='utf-8').replace('\0','')
        return decrypted