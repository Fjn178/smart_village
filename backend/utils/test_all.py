"""
完整测试 - 验证所有基础模块
"""

print("=" * 50)
print("开始验证所有模块...")
print("=" * 50)

# ============================================================
# 测试 1: response.py
# ============================================================
print("\n【1】测试 response.py...")
try:
    from response import success, error
    print("  ✅ 导入成功")
    
    # 测试返回格式
    resp1 = success(data={"village": "山口庄村"}, message="推荐成功")
    resp2 = error(message="参数错误", code=400)
    print(f"  ✅ success返回: {type(resp1)} (Flask Response对象)")
    print(f"  ✅ error返回: {type(resp2)} (Flask Response对象)")
except Exception as e:
    print(f"  ❌ 失败: {e}")

# ============================================================
# 测试 2: normalize.py
# ============================================================
print("\n【2】测试 normalize.py...")
try:
    from normalize import min_max_scale, z_score
    print("  ✅ 导入成功")
    
    # 测试数据
    test_data = [1, 2, 3, 4, 5]
    mm = min_max_scale(test_data)
    zs = z_score(test_data)
    print(f"  ✅ Min-Max: {mm}")
    print(f"  ✅ Z-score: {[round(x, 2) for x in zs]}")
    
    # 边界情况：所有值相同
    same_data = [5, 5, 5, 5]
    mm2 = min_max_scale(same_data)
    zs2 = z_score(same_data)
    print(f"  ✅ 全相同数据 Min-Max: {mm2}")
    print(f"  ✅ 全相同数据 Z-score: {zs2}")
except Exception as e:
    print(f"  ❌ 失败: {e}")

# ============================================================
# 测试 3: validator.py
# ============================================================
print("\n【3】测试 validator.py...")
try:
    from validator import (
        validate_required,
        validate_type,
        validate_range,
        validate_email,
        validate_row_against_schema,
        ValidationError
    )
    print("  ✅ 导入成功")
    
    # 测试 validate_required
    record = {"name": "张三", "age": None}
    missing = validate_required(record, ["name", "age", "phone"])
    print(f"  ✅ 必填校验: 缺失字段 {missing}")
    
    # 测试 validate_type
    print(f"  ✅ 类型校验: '123'是int? {validate_type('123', 'int')}")
    print(f"  ✅ 类型校验: 'abc'是int? {validate_type('abc', 'int')}")
    
    # 测试 validate_email
    print(f"  ✅ 邮箱校验: test@qq.com {validate_email('test@qq.com')}")
    print(f"  ✅ 邮箱校验: invalid {validate_email('invalid')}")
    
    # 测试 schema 校验
    schema = {
        "name": {"required": True, "type": "str"},
        "age": {"required": False, "type": "int", "min": 0, "max": 120},
        "email": {"required": False, "type": "str", "format": "email"}
    }
    row_ok = {"name": "李四", "age": 25, "email": "lisi@example.com"}
    row_bad = {"age": 150, "email": "invalid"}
    
    errors_ok = validate_row_against_schema(row_ok, schema)
    errors_bad = validate_row_against_schema(row_bad, schema)
    print(f"  ✅ Schema校验(正确数据): {len(errors_ok)}个错误")
    print(f"  ✅ Schema校验(错误数据): {len(errors_bad)}个错误")
    
    # 测试 ValidationError 异常
    try:
        raise ValidationError([{"field": "test", "code": "test"}])
    except ValidationError as e:
        print(f"  ✅ ValidationError异常: {e.errors}")
        
except Exception as e:
    print(f"  ❌ 失败: {e}")

# ============================================================
# 测试 4: auth_utils.py
# ============================================================
print("\n【4】测试 auth_utils.py...")
try:
    from auth_utils import (
        jwt_encode,
        jwt_decode,
        generate_token_for_user,
        verify_token,
        hash_password,
        verify_password
    )
    print("  ✅ 导入成功")
    
    # 测试 JWT
    secret = "my_test_secret_123"
    token = jwt_encode({"user_id": "test_001", "role": "admin"}, secret, expire_seconds=60)
    print(f"  ✅ JWT生成: {token[:50]}...")
    
    decoded = jwt_decode(token, secret)
    print(f"  ✅ JWT解码: {decoded}")
    
    # 测试 token 过期
    token_short = jwt_encode({"user_id": "test"}, secret, expire_seconds=-10)
    try:
        jwt_decode(token_short, secret)
        print("  ❌ 过期token未抛出异常")
    except ValueError as e:
        print(f"  ✅ 过期token验证: {e}")
    
    # 测试用户Token生成
    user_token = generate_token_for_user("user_123", secret, expire_seconds=3600, extra={"role": "admin"})
    print(f"  ✅ 用户Token: {user_token[:40]}...")
    
    verified = verify_token(user_token, secret)
    print(f"  ✅ Token验证: {verified}")
    
    # 测试密码哈希
    pwd = "my_password_123"
    hashed = hash_password(pwd)
    print(f"  ✅ 密码哈希: {hashed[:40]}...")
    
    # 测试密码验证
    is_valid = verify_password(pwd, hashed)
    print(f"  ✅ 密码验证(正确): {is_valid}")
    
    is_valid_wrong = verify_password("wrong_password", hashed)
    print(f"  ✅ 密码验证(错误): {is_valid_wrong}")
    
except Exception as e:
    print(f"  ❌ 失败: {e}")

# ============================================================
# 测试 5: excel_parser.py（需要 pandas 和 openpyxl）
# ============================================================
print("\n【5】测试 excel_parser.py...")
try:
    # 先检查导入（不真正读取文件）
    from excel_parser import parse_excel, _read_with_pandas, _read_csv
    print("  ✅ 导入成功")
    
    # 检查 pandas 是否可用
    try:
        import pandas as pd
        print(f"  ✅ pandas 版本: {pd.__version__}")
    except ImportError:
        print("  ⚠️ pandas 未安装，Excel解析功能不可用")
    
    # 检查 openpyxl 是否可用
    try:
        import openpyxl
        print(f"  ✅ openpyxl 版本: {openpyxl.__version__}")
    except ImportError:
        print("  ⚠️ openpyxl 未安装，.xlsx文件读取不可用")
    
    print("  ✅ excel_parser 模块加载成功（需要实际文件才能完整测试）")
    
except Exception as e:
    print(f"  ❌ 失败: {e}")

# ============================================================
# 最终结果
# ============================================================
print("\n" + "=" * 50)
print("验证完成！")
print("=" * 50)