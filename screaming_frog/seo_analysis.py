import pandas as pd
import os
import sys

# determine CSV file to read
csv_file = sys.argv[1] if len(sys.argv) > 1 else "internal_all.csv"
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), csv_file)

# read CSV
df = pd.read_csv(csv_path)

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
low_text_ratio = df[df['Text Ratio'] < 10]

# high CO2 pages Might not be applicable in this context, but if CO2 data is available:
#high_co2 = df[df['CO2 (mg)'] > 1000]

# Export to Excel
with pd.ExcelWriter("seo_issues_report.xlsx") as writer:
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

print("SEO report generated: seo_issues_report.xlsx")
