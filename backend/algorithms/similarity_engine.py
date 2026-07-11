 village_id: int | str,
    top_n: int = 5,
    weight_type: str = "equal",

) -> List[Dict[str, Any]]:
    """匹配目标村庄的相似案例。"""
    try:
@@ -115,7 +114,6 @@ def get_similarity_recommendations(
    village_id: int | str,
    top_n: int = 5,
    weight_type: str = "equal",

    flask_response: bool = True,
) -> List[Dict[str, Any]]:
    """返回相似案例推荐结果。"""
@@ -124,18 +122,18 @@ def get_similarity_recommendations(

def _match_similar_cases(village_id: int | str, top_n: int, weight_type: str) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        indicator_stats = _load_indicator_stats(conn)
        category_medians = _load_category_medians(conn)
        target_vector = _get_village_indicator_vector(conn, village_id, indicator_stats, category_medians)
        if target_vector is None:
            return []


        case_rows = _load_case_library_rows(conn)
        if not case_rows:
            return []

        weights = _build_weights(len(target_vector), weight_type)
        distances: List[Dict[str, Any]] = []


        for row in case_rows:
            row_dict = dict(row)
@@ -146,17 +144,12 @@ def _match_similar_cases(village_id: int | str, top_n: int, weight_type: str) ->
            if str(case_village_id) == str(village_id):
                continue

            case_vector = _get_village_indicator_vector(conn, case_village_id, indicator_stats, category_medians)



            if case_vector is None:
                continue


            distance = weighted_euclidean_distance(target_vector, case_vector, weights)
            similarity_score = distance_to_similarity_score(distance)


            distances.append(
                {
@@ -222,7 +215,12 @@ def _find_column(columns: Iterable[str], desired_names: Sequence[str]) -> Option
    return None


def _get_village_indicator_vector(
    conn: sqlite3.Connection,
    village_id: int | str,
    indicator_stats: Dict[int, tuple[float, float]],
    category_medians: Dict[str, float],
) -> Optional[List[float]]:
    if not _table_exists(conn, "village_indicators"):
        return None

@@ -247,15 +245,19 @@ def _get_village_indicator_vector(conn: sqlite3.Connection, village_id: int | st
        if indicator_id is not None and 1 <= indicator_id <= len(INDICATOR_IDS):
            values[indicator_id] = numeric_value




    result: List[float] = []
    for indicator_id in INDICATOR_IDS:
        if indicator_id in values:
            value = values[indicator_id]
        else:
            category = _find_indicator_category(indicator_id)
            value = category_medians.get(category, 0.0)

        mean, std = indicator_stats.get(indicator_id, (0.0, 0.0))
        if std <= 0:
            result.append(0.0)
        else:
            result.append((value - mean) / std)
    return result


@@ -266,6 +268,47 @@ def _load_case_library_rows(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    return cursor.fetchall()


def _load_indicator_stats(conn: sqlite3.Connection) -> Dict[int, tuple[float, float]]:
    cursor = conn.execute(
        "SELECT indicator_id, AVG(value) AS mean, AVG(value * value) AS sq_mean"
        " FROM village_indicators WHERE value IS NOT NULL"
        " GROUP BY indicator_id"
    )
    stats: Dict[int, tuple[float, float]] = {}
    for row in cursor.fetchall():
        indicator_id = _to_int(row["indicator_id"])
        mean = _normalize_number(row["mean"])
        sq_mean = _normalize_number(row["sq_mean"])
        if indicator_id is not None:
            variance = sq_mean - mean * mean
            std = math.sqrt(variance) if variance > 0 else 0.0
            stats[indicator_id] = (mean, std)
    return stats


def _load_category_medians(conn: sqlite3.Connection) -> Dict[str, float]:
    medians: Dict[str, float] = {}
    for category, indicator_ids in INDICATOR_CATEGORIES.items():
        if not indicator_ids:
            medians[category] = 0.0
            continue

        placeholders = ",".join("?" for _ in indicator_ids)
        cursor = conn.execute(
            f"SELECT value FROM village_indicators WHERE indicator_id IN ({placeholders}) AND value IS NOT NULL",
            tuple(indicator_ids),
        )
        values = [_normalize_number(row["value"]) for row in cursor.fetchall()]
        if not values:
            medians[category] = 0.0
            continue

        values.sort()
        mid = len(values) // 2
        medians[category] = values[mid] if len(values) % 2 == 1 else (values[mid - 1] + values[mid]) / 2.0
    return medians


def _get_category_median(conn: sqlite3.Connection, indicator_id: int) -> float:
    category = _find_indicator_category(indicator_id)
    if category is None:
@@ -291,18 +334,6 @@ def _get_category_median(conn: sqlite3.Connection, indicator_id: int) -> float:
    return (raw_values[mid - 1] + raw_values[mid]) / 2.0














def _find_indicator_category(indicator_id: int) -> Optional[str]:
    for category, ids in INDICATOR_CATEGORIES.items():
        if indicator_id in ids:
