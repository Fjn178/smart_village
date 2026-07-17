from database.db import Village, VillageIndicator, IndicatorDefinition
from algorithms.industry_engine import recommend_industries


def get_top5_case_matches(village_id=None, top_n=5):
    if not village_id:
        raise ValueError('请提供 village_id 参数。')

    village = Village.query.filter_by(village_id=village_id).first()
    if not village:
        raise ValueError('未找到匹配的村庄。')

    indicator_rows = VillageIndicator.query.filter_by(village_id=village.village_id).all()
    if not indicator_rows:
        raise ValueError('该村庄尚无指标数据，无法进行案例匹配。')

    indicator_values = {
        row.indicator_id: row.indicator_value
        for row in indicator_rows
        if row.indicator_value is not None
    }
    if not indicator_values:
        raise ValueError('该村庄没有可用于匹配的数值指标。')

    definitions = IndicatorDefinition.query.filter(
        IndicatorDefinition.indicator_id.in_(list(indicator_values.keys()))
    ).all()
    definition_map = {definition.indicator_id: definition for definition in definitions}

    requested_top_n = int(top_n or 5)
    safe_top_n = max(1, min(requested_top_n, 5))
    recommendations = recommend_industries(indicator_values, definition_map, top_n=safe_top_n)

    return {
        'village_id': village.village_id,
        'village_name': village.village_name,
        'town': getattr(village, 'town', ''),
        'recommendations': recommendations,
        'cases': recommendations
    }
