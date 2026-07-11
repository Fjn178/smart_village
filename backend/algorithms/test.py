"""
T29 相似案例匹配引擎 - 单元测试

【重要】测试前请确保：
1. 数据库已创建，且包含 indicator_definitions、village_indicators、case_library 表
2. 测试数据已准备（至少1个目标村庄 + 3个以上案例村庄）

运行方式：
    python -m pytest tests/test_similarity_engine.py -v
    或
    python tests/test_similarity_engine.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from similarity_engine import (
    weighted_euclidean_distance,
    distance_to_similarity_score,
    INDICATOR_IDS,
    get_case_count,
    get_village_name,
    match_similar_cases,
)


# ============================================================
# 测试1：指标维度验证
# ============================================================

def test_indicator_ids_length():
    """验证INDICATOR_IDS数量是否为151"""
    print("\n【测试1】指标维度验证")

    expected_ids = set(range(1, 152))  # 1-151
    actual_ids = set(INDICATOR_IDS)
    missing = expected_ids - actual_ids
    extra = actual_ids - expected_ids

    print(f"  INDICATOR_IDS 长度: {len(INDICATOR_IDS)} (期望151)")
    if missing:
        print(f"  ⚠️ 缺少的指标ID: {sorted(missing)}")
    if extra:
        print(f"  ⚠️ 多余的指标ID: {sorted(extra)}")

    assert len(INDICATOR_IDS) == 151, f"实际{len(INDICATOR_IDS)}个，期望151个"
    print("  ✅ 通过")


# ============================================================
# 测试2：核心算法函数（纯数学，不依赖数据库）
# ============================================================

def test_weighted_euclidean_distance():
    """测试加权欧氏距离计算"""
    print("\n【测试2】加权欧氏距离计算")

    target = [0.8, 0.5, 0.3]
    case = [0.7, 0.6, 0.2]
    weights = [1.0, 1.0, 1.0]

    dist = weighted_euclidean_distance(target, case, weights)
    print(f"  目标: {target}")
    print(f"  案例: {case}")
    print(f"  距离: {dist:.4f}")
    print(f"  相似度: {distance_to_similarity_score(dist):.1f}%")

    # 完全相同向量 → 距离应为0
    dist_zero = weighted_euclidean_distance(target, target, weights)
    print(f"  完全相同向量距离: {dist_zero:.4f} (应为0)")
    assert dist_zero == 0.0

    # 距离→相似度映射
    assert distance_to_similarity_score(0.0) == 100.0
    assert distance_to_similarity_score(1.0) == 50.0

    print("  ✅ 通过")


def test_distance_similarity_mapping():
    """测试距离到相似度的映射"""
    print("\n【测试3】距离-相似度映射")

    test_cases = [
        (0.0, 100.0),
        (0.5, 66.67),
        (1.0, 50.0),
        (2.0, 33.33),
        (3.0, 25.0),
    ]

    for dist, expected in test_cases:
        actual = distance_to_similarity_score(dist)
        print(f"  距离 {dist:.1f} → 相似度 {actual:.2f}% (期望 {expected:.2f}%)")
        assert abs(actual - expected) < 0.1

    print("  ✅ 通过")


# ============================================================
# 测试4：完整匹配流程（需要真实数据库）
# ============================================================

def test_match_similar_cases():
    """测试完整匹配流程（需要数据库中有数据）"""
    print("\n【测试4】完整匹配流程")

    case_count = get_case_count()
    if case_count == 0:
        print("  ⚠️ 案例库为空，跳过测试")
        print("  请先导入案例数据后再运行此测试")
        return

    # 尝试使用ID=1的村庄，如不存在则提示
    test_village_id = 1

    try:
        village_name = get_village_name(test_village_id)
        if not village_name or village_name.startswith("ID:"):
            print(f"  ⚠️ 村庄ID {test_village_id} 不存在，跳过测试")
            print("  请修改 test_village_id 为数据库中实际存在的村庄ID")
            return

        print(f"  目标村庄: {village_name} (ID: {test_village_id})")

        results = match_similar_cases(test_village_id, top_n=5)

        if not results:
            print("  ⚠️ 未匹配到任何案例（可能案例库中只有目标村庄自身）")
            return

        print(f"  匹配到 {len(results)} 个相似案例:")
        for i, r in enumerate(results, 1):
            print(f"\n  Top{i}: {r['case_name']}")
            print(f"    产业: {r['industry']}")
            print(f"    距离: {r['distance']:.4f}")
            print(f"    相似度: {r['similarity_score']:.1f}%")
            print(f"    结果: {r['result']}")
            print(f"    关键做法: {r['key_practices']}")
            print(f"    备注: {r['special_notes']}")

        # 验证
        assert len(results) <= 5
        for r in results:
            assert 0 <= r['similarity_score'] <= 100

        print("\n  ✅ 通过")

    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        raise


# ============================================================
# 测试5：get_case_count 函数
# ============================================================

def test_get_case_count():
    """测试获取案例总数"""
    print("\n【测试5】获取案例总数")

    count = get_case_count()
    print(f"  案例总数: {count}")

    # 如果数据库未就绪，count为0，但不报错
    assert count >= 0
    print("  ✅ 通过")


# ============================================================
# 运行所有测试
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("T29 相似案例匹配引擎 - 单元测试")
    print("=" * 60)
    print("\n⚠️ 注意：【测试4】需要数据库中有数据")

    tests = [
        test_indicator_ids_length,
        test_weighted_euclidean_distance,
        test_distance_similarity_mapping,
        test_get_case_count,
        test_match_similar_cases,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ 断言失败: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    if failed == 0:
        print("✅ 所有测试通过！")
    else:
        print("❌ 有测试失败，请检查")