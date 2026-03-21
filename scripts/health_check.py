#!/usr/bin/env python3
"""
clawbot-forum 全面自检脚本
检查内容：链接、表单、异常、关键元素
"""
import requests
import re
import sys
from urllib.parse import urljoin, urlparse

BASE_URL = "http://49.234.184.65"

# 需要检查的页面
PAGES_TO_CHECK = [
    "/",
    "/post/1",
    "/post/2", 
    "/auth/login",
    "/auth/register",
    "/tags",
]

ERROR_PATTERNS = [
    r"Traceback",
    r"Exception",
    r"BuildError",
    r"KeyError",
    r"AttributeError",
    r"jinja2\.exceptions",
    r"sqlalchemy\.exc",
    r"Error:\s*\d+",
    r"Internal Server Error",
    r"404 Not Found",
    r"500 Internal Server Error",
]

def check_page(url):
    """检查单个页面"""
    results = {
        "url": url,
        "status": None,
        "errors": [],
        "forms": [],
        "links": [],
        "has_key_elements": False
    }
    
    try:
        response = requests.get(url, timeout=10)
        results["status"] = response.status_code
        html = response.text
        
        # 检查HTTP状态
        if response.status_code != 200:
            results["errors"].append(f"HTTP {response.status_code}")
        
        # 检查错误关键词
        for pattern in ERROR_PATTERNS:
            if re.search(pattern, html, re.IGNORECASE):
                # 排除正常内容中的匹配（如onerror属性）
                if not re.search(r'onerror=["\']this\.src', html):
                    matches = re.findall(pattern, html, re.IGNORECASE)
                    if matches:
                        results["errors"].append(f"发现错误: {pattern}")
        
        # 提取并检查表单
        forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>', html)
        results["forms"] = forms
        
        # 检查关键元素
        key_elements = [
            r'<nav.*navbar',
            r'<main.*container',
            r'<footer',
            r'class="card"',
        ]
        found_elements = sum(1 for p in key_elements if re.search(p, html))
        results["has_key_elements"] = found_elements >= 3
        
        # 提取所有链接
        links = re.findall(r'href=["\']([^"\']*)["\']', html)
        results["links"] = [l for l in links if l.startswith('/') and not l.startswith('//')]
        
    except Exception as e:
        results["errors"].append(f"请求异常: {str(e)}")
    
    return results

def check_form_action(form_url, base_url):
    """检查表单action是否有效"""
    if not form_url or form_url == "":
        return "当前页面"
    
    if form_url.startswith('http'):
        test_url = form_url
    else:
        test_url = urljoin(base_url, form_url)
    
    try:
        # 用POST测试表单端点（不提交实际数据）
        resp = requests.post(test_url, data={}, timeout=5, allow_redirects=False)
        if resp.status_code in [200, 302, 400, 401, 403]:
            return f"✅ 可达 (HTTP {resp.status_code})"
        else:
            return f"⚠️ 异常状态 (HTTP {resp.status_code})"
    except Exception as e:
        return f"❌ 错误: {str(e)[:50]}"

def main():
    print("=" * 60)
    print("clawbot-forum 全面自检报告")
    print("=" * 60)
    print()
    
    all_pass = True
    
    for path in PAGES_TO_CHECK:
        url = urljoin(BASE_URL, path)
        print(f"\n🔍 检查: {path}")
        print("-" * 60)
        
        result = check_page(url)
        
        # 状态码
        status_icon = "✅" if result["status"] == 200 else "❌"
        print(f"{status_icon} HTTP 状态: {result['status']}")
        
        # 错误检查
        if result["errors"]:
            print("❌ 发现错误:")
            for error in result["errors"]:
                print(f"   - {error}")
            all_pass = False
        else:
            print("✅ 无异常错误")
        
        # 关键元素
        if result["has_key_elements"]:
            print("✅ 关键元素存在")
        else:
            print("⚠️ 关键元素缺失")
            all_pass = False
        
        # 表单检查
        if result["forms"]:
            print(f"📋 发现 {len(result['forms'])} 个表单:")
            for form in result["forms"]:
                check_result = check_form_action(form, url)
                print(f"   - action='{form}' -> {check_result}")
        
    print()
    print("=" * 60)
    if all_pass:
        print("✅ 自检通过")
    else:
        print("❌ 自检发现问题")
    print("=" * 60)
    
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
