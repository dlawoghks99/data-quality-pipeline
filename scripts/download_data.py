import os
from kaggle.api.kaggle_api_extended import KaggleApi


def download_olist_data():
    # Kaggle API 인증
    api = KaggleApi()
    api.authenticate()

    # 데이터셋 식별자와 저장 경로
    dataset = "olistbr/brazilian-ecommerce"
    download_path = "data/raw"

    # 저장 폴더가 없으면 생성
    os.makedirs(download_path, exist_ok=True)

    # 다운로드 + 압축 해제
    print(f"Downloading {dataset} ...")
    api.dataset_download_files(dataset, path=download_path, unzip=True)
    print(f"Done. Files saved to {download_path}/")


if __name__ == "__main__":
    download_olist_data()