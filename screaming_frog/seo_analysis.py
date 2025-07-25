import argparse
import os
import sys

import pandas as pd

# determine CSV file to read
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyse Screaming Frog crawl data")
    parser.add_argument(
        "csv_file",
        nargs="?",
        default="internal_all.csv",
        help="CSV exported from Screaming Frog",
    )
    return parser.parse_args()


def load_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        print(f"CSV file not found: {path}", file=sys.stderr)
        sys.exit(1)
    return pd.read_csv(path, encoding="utf-8-sig")


def main() -> None:
    args = parse_args()

    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.csv_file)
    base_name = os.path.splitext(args.csv_file)[0]
    output_excel = f"{base_name}_seo_issues_report.xlsx"

    df = load_csv(csv_path)

    # --- SEO Checks ---

    # broken pages (status codes 4xx and 5xx)
    broken_pages = df[df['Status Code'].astype(str).str.startswith(('4', '5'))]

    # missing titles
    missing_titles = df[df['Title 1'].isnull() | (df['Title 1'].str.strip() == '')]

    # too short/long titles
    short_titles = df[(df['Title 1 Length'] > 0) & (df['Title 1 Length'] < 30)]
    long_titles = df[df['Title 1 Length'] > 60]

    # meta descriptions
    missing_meta = df[df['Meta Description 1'].isnull() | (df['Meta Description 1'].str.strip() == '')]

    # too short/long meta descriptions
    short_meta = df[(df['Meta Description 1 Length'] > 0) & (df['Meta Description 1 Length'] < 70)]
    long_meta = df[df['Meta Description 1 Length'] > 160]

    # missing H1s
    missing_h1 = df[df['H1-1'].isnull() | (df['H1-1'].str.strip() == '')]

    # multiple H1s
    multiple_h1 = df[df['H1-2'].notnull() & (df['H1-2'].str.strip() != '')]

    # non-indexable pages
    non_indexable = df[df['Indexability'] != 'Indexable']

    # Missing canonical tag
    missing_canonical = df[df['Canonical Link Element 1'].isnull() | (df['Canonical Link Element 1'].str.strip() == '')]

    # Low readability (Flesch score < 60) / not implemented in this version of the code
    #low_readability = df[df['Flesch Reading Ease Score'] < 60]

    # low text ratio (< 10%)
    text_ratio = pd.to_numeric(df.get('Text Ratio'), errors='coerce')
    low_text_ratio = df[text_ratio < 10]

    # high CO2 pages Might not be applicable in this context, but if CO2 data is available:
    #high_co2 = df[df['CO2 (mg)'] > 1000]

    # Export to Excel
    with pd.ExcelWriter(output_excel) as writer:
        broken_pages.to_excel(writer, sheet_name="Broken Pages", index=False)
        missing_titles.to_excel(writer, sheet_name="Missing Titles", index=False)
        short_titles.to_excel(writer, sheet_name="Short Titles", index=False)
        long_titles.to_excel(writer, sheet_name="Long Titles", index=False)
        missing_meta.to_excel(writer, sheet_name="Missing Meta", index=False)
        short_meta.to_excel(writer, sheet_name="Short Meta", index=False)
        long_meta.to_excel(writer, sheet_name="Long Meta", index=False)
        missing_h1.to_excel(writer, sheet_name="Missing H1", index=False)
        multiple_h1.to_excel(writer, sheet_name="Multiple H1", index=False)
        non_indexable.to_excel(writer, sheet_name="Non-Indexable", index=False)
        missing_canonical.to_excel(writer, sheet_name="Missing Canonical", index=False)
        #low_readability.to_excel(writer, sheet_name="Low Readability", index=False)
        low_text_ratio.to_excel(writer, sheet_name="Low Text Ratio", index=False)
        #high_co2.to_excel(writer, sheet_name="High CO2", index=False)

    print(f"SEO report generated: {output_excel}")


if __name__ == "__main__":
    main()
