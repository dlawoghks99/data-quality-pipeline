# Data Quality Pipeline

커머스 주문 데이터를 대상으로 한 데이터 품질 검증 파이프라인.
배치로 적재된 데이터의 이상치·정합성을 자동으로 검증하고,
문제 발생 시 감지 → 알람 → 원인 로깅 흐름을 처리한다.

## 배경

(왜 이 프로젝트를 만드는지 — 추후 작성)

## 아키텍처

(전체 흐름 다이어그램 — 추후 작성)

## 기술 스택

- **오케스트레이션**: Apache Airflow
- **데이터 변환**: dbt
- **품질 검증**: Great Expectations
- **저장소**: PostgreSQL
- **인프라**: Docker / Docker Compose

## 데이터

- Olist Brazilian E-Commerce 공개 데이터셋
- (데이터는 git에 포함하지 않음 — scripts/ 의 다운로드 스크립트 참고)

## 실행 방법

(추후 작성)

## 프로젝트 구조

```
data-quality-pipeline/
├── dags/                # Airflow DAG
├── dbt/                 # dbt 프로젝트
├── great_expectations/  # 품질 검증 규칙
├── data/                # 데이터셋 (git 제외)
├── scripts/             # 유틸 스크립트
├── docker/              # Docker 관련
└── docs/                # 문서
```
