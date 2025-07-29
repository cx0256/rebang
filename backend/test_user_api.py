import requests

def test_user_apis():
    # 首先登录获取token
    login_url = 'http://127.0.0.1:8000/api/v1/auth/login'
    login_data = {
        'username': 'admin@example.com',
        'password': 'admin123'
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    print('1. 测试登录...')
    try:
        response = requests.post(login_url, data=login_data, headers=headers)
        print(f'登录状态码: {response.status_code}')
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            print(f'获取到token: {access_token[:50]}...')
            
            # 测试获取用户信息
            print('\n2. 测试获取用户信息...')
            user_info_url = 'http://127.0.0.1:8000/api/v1/auth/me'
            auth_headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            user_response = requests.get(user_info_url, headers=auth_headers)
            print(f'用户信息状态码: {user_response.status_code}')
            print(f'用户信息响应: {user_response.text}')
            
            # 测试获取权限代码
            print('\n3. 测试获取权限代码...')
            codes_url = 'http://127.0.0.1:8000/api/v1/auth/codes'
            
            codes_response = requests.get(codes_url, headers=auth_headers)
            print(f'权限代码状态码: {codes_response.status_code}')
            print(f'权限代码响应: {codes_response.text}')
            
        else:
            print(f'登录失败: {response.text}')
            
    except Exception as e:
        print(f'请求错误: {e}')

if __name__ == '__main__':
    test_user_apis()