import argparse
import glob
import os
import pandas as pd


def find_latest(pattern: str):
    files = glob.glob(pattern)
    if not files:
        return None
    files.sort(key=os.path.getmtime)
    return files[-1]


def perform_analysis(df: pd.DataFrame):
    """Run SEO checks over the scraped dataframe."""
    issue_dfs = {}
    # Broken pages
    issue_dfs["Broken Pages"] = df[df['Status Code'].astype(str).str.startswith(('4', '5'))]
    # Title issues
    issue_dfs["Missing Titles"] = df[df['Title'].fillna('').str.strip() == '']
    issue_dfs["Short Titles"] = df[(df['Title Length'] > 0) & (df['Title Length'] < 30)]
    issue_dfs["Long Titles"] = df[df['Title Length'] > 60]
    # Meta description issues
    issue_dfs["Missing Meta"] = df[df['Meta Description'].fillna('').str.strip() == '']
    issue_dfs["Short Meta"] = df[(df['Meta Description Length'] > 0) & (df['Meta Description Length'] < 70)]
    issue_dfs["Long Meta"] = df[df['Meta Description Length'] > 160]
    # H1 issues
    issue_dfs["Missing H1"] = df[df['H1 Count'] == 0]
    issue_dfs["Multiple H1"] = df[df['H1 Count'] > 1]
    return issue_dfs


def build_summary(issue_dfs, images_df=None):
    summary = {issue: len(data) for issue, data in issue_dfs.items()}
    if images_df is not None:
        summary['Images Missing Alt'] = images_df['Alt Missing'].sum()
        summary['Total Images'] = len(images_df)
    return summary


def write_summary_csv(summary_dict, path):
    df_summary = pd.DataFrame(list(summary_dict.items()), columns=['Issue', 'Count'])
    df_summary.to_csv(path, index=False)


def write_overview_txt(summary_csv, images_csv, output_path):
    df = pd.read_csv(summary_csv)
    lines = [f"{row['Issue']}: {row['Count']}" for _, row in df.iterrows()]

    if images_csv and os.path.exists(images_csv):
        img_df = pd.read_csv(images_csv)
        total_images = len(img_df)
        missing_alt = img_df['Alt Missing'].sum()
        lines.append(f"Total images: {total_images}")
        lines.append(f"Images missing alt text: {missing_alt}")

    with open(output_path, 'w') as f:
        f.write("\n".join(lines))


def main(scrapy_csv=None, images_csv=None):
    # Determine input files if not provided
    if not scrapy_csv:
        scrapy_csv = find_latest('webcrawler_reports/*_scrapy_report.csv')
        if not scrapy_csv:
            raise FileNotFoundError('No scrapy report CSV found in webcrawler_reports/')

    if not images_csv:
        guessed = scrapy_csv.replace('_scrapy_report.csv', '_images.csv')
        images_csv = guessed if os.path.exists(guessed) else find_latest('webcrawler_reports/*_images.csv')

    df = pd.read_csv(scrapy_csv)
    issues = perform_analysis(df)
    summary = build_summary(issues, pd.read_csv(images_csv) if images_csv else None)

    domain = os.path.basename(scrapy_csv).replace('_scrapy_report.csv', '')
    summary_csv = os.path.join('webcrawler_reports', f'{domain}_analysis_summary.csv')
    overview_txt = os.path.join('webcrawler_reports', f'{domain}_analysis_overview.txt')

    write_summary_csv(summary, summary_csv)
    write_overview_txt(summary_csv, images_csv, overview_txt)

    print(f'Analysis summary CSV saved to: {summary_csv}')
    print(f'Overview TXT saved to: {overview_txt}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyse Scrapy crawler output')
    parser.add_argument('--scrapy-csv', help='Path to _scrapy_report.csv file')
    parser.add_argument('--images-csv', help='Path to images CSV file')
    args = parser.parse_args()

    main(scrapy_csv=args.scrapy_csv, images_csv=args.images_csv)
