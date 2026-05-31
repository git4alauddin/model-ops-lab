"""Tests for V1 dataset loading controls."""

from app.train import DataError, load_dataset


def test_load_dataset_missing_file():
    try:
        load_dataset("data/does_not_exist.csv")
    except DataError as exc:
        assert "not found" in str(exc)
    else:
        raise AssertionError("Expected DataError for missing dataset.")


def test_load_dataset_empty_csv_header_only(tmp_path):
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("feature,target\n", encoding="utf-8")

    try:
        load_dataset(csv_file)
    except DataError as exc:
        assert "empty" in str(exc).lower()
    else:
        raise AssertionError("Expected DataError for empty dataset.")


def test_load_dataset_success(tmp_path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "\n".join(
            [
                "feature,target",
                "1,0",
                "2,1",
            ]
        ),
        encoding="utf-8",
    )

    dataframe = load_dataset(csv_file)

    assert dataframe.shape == (2, 2)
