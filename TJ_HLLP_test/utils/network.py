# -*- coding: utf-8 -*-
"""网络请求工具"""
import urllib.request

def create_opener(proxy=None, token=None):
    """创建支持代理+Token 的 opener"""
    handlers = []
    
    if proxy:
        handlers.append(urllib.request.ProxyHandler({
            'http': proxy, 
            'https': proxy
        }))
    
    if token:
        class TokenHandler(urllib.request.BaseHandler):
            def http_request(self, req):
                req.add_header("Authorization", f"token {token}")
                req.add_header("User-Agent", "DuiPai-Tool")
                return req
            https_request = http_request
        handlers.append(TokenHandler(token))
    else:
        class UAHandler(urllib.request.BaseHandler):
            def http_request(self, req):
                req.add_header("User-Agent", "DuiPai-Tool")
                return req
            https_request = http_request
        handlers.append(UAHandler())
    
    return urllib.request.build_opener(*handlers)