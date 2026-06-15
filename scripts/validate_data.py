import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import text
import os
import pandas as pd
import great_expectations as gx
from sqlalchemy import create_engine
from dotenv import load_dotenv

def get_engine():
    load_dotenv()
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_NAME = os.getenv("POSTGRES_DB")
    return create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_NAME}"
    )

def get_orders_dataframe(engine):
    return pd.read_sql("SELECT * FROM olist_orders_dataset", engine);

def log_results_to_db(results, engine, table_name="olist_orders_dataset"):
    run_id = uuid.uuid4().hex                  # ① 이번 실행 전체를 묶는 식별자
    validated_at = datetime.now(timezone.utc)  #    실행 시각(UTC)

    rows = []
    for result in results:
        kwargs = result.expectation_config.kwargs
        r = result.result
        rows.append({
            "run_id": run_id,
            "validated_at": validated_at,
            "table_name": table_name,
            "column_name": kwargs.get("column"),
            "expectation_type": result.expectation_config.expectation_type,
            "success": bool(result.success),
            "unexpected_count": r.get("unexpected_count"),
            "unexpected_percent": r.get("unexpected_percent"),
            # ② 리스트라 JSON 문자열로 직렬화 (SQL에서 ::jsonb로 캐스팅)
            "partial_unexpected_list": json.dumps(
                r.get("partial_unexpected_list", []), ensure_ascii=False
            ),
        })

    insert_sql = text("""
        INSERT INTO validation_results
            (run_id, validated_at, table_name, column_name, expectation_type,
             success, unexpected_count, unexpected_percent, partial_unexpected_list)
        VALUES
            (:run_id, :validated_at, :table_name, :column_name, :expectation_type,
             :success, :unexpected_count, :unexpected_percent,
             CAST(:partial_unexpected_list AS JSONB))
    """)

    with engine.begin() as conn:           # ③ 트랜잭션 (다 성공해야 커밋)
        conn.execute(insert_sql, rows)

    print(f"[LOG] {len(rows)} results saved (run_id={run_id})")

def validate_orders(df):
    ge_df = gx.dataset.PandasDataset(df)
    results = []
    results.append(ge_df.expect_column_values_to_not_be_null("order_id"))
    results.append(ge_df.expect_column_values_to_be_unique("order_id"))
    results.append(ge_df.expect_column_values_to_not_be_null("customer_id"))
    valid_statuses = [
        "delivered", "shipped", "canceled", "unavailable",
        "invoiced", "processing", "created", "approved",
    ]
    results.append(
        ge_df.expect_column_values_to_be_in_set("order_status", valid_statuses)
    )

    # 규칙 5: [마이그레이션 검증] order_id 길이가 TOBE 목표 스키마(VARCHAR(20))에 맞는가
    # ASIS는 32자 해시. TOBE에서 VARCHAR(20)으로 표준화 시 데이터 손실 발생 여부 사전 검증
    TOBE_MAX_LENGTH = 20
    results.append(
        ge_df.expect_column_value_lengths_to_be_between(
            "order_id", min_value=1, max_value=TOBE_MAX_LENGTH
        )
    )

    return results

def print_results(results):
    print("\n" + "=" * 50)
    print("Data Quality Validation Results")
    print("=" * 50)
    all_passed = True
    for result in results:
        expectation = result.expectation_config.expectation_type
        column = result.expectation_config.kwargs.get("column", "")
        success = result.success
        status = "PASS" if success else "FAIL"
        if not success:
            all_passed = False
        print(f"[{status}] {expectation} (column: {column})")

        # FAIL일 때 원인 진단 정보 출력
        if not success:
            stats = result.result
            unexpected_count = stats.get("unexpected_count", "N/A")
            unexpected_percent = stats.get("unexpected_percent", "N/A")
            partial_list = stats.get("partial_unexpected_list", [])
            print(f"       └─ 위반 건수: {unexpected_count}")
            if unexpected_percent != "N/A":
                print(f"       └─ 위반 비율: {unexpected_percent:.2f}%")
            if partial_list:
                print(f"       └─ 위반 값 샘플: {partial_list[:3]}")

    print("=" * 50)
    print(f"Overall: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    print("=" * 50)


if __name__ == "__main__":
    engine = get_engine()
    df = get_orders_dataframe(engine)
    print(f"Loaded {len(df)} rows from olist_orders_dataset")
    results = validate_orders(df)
    print_results(results)
    log_results_to_db(results, engine)