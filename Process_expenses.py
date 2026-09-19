# %% [markdown]
# # Session 4: From a messy inbox to executive charts
# 
# **Business request:** Combine five months of expense files from four departments, clean their inconsistent labels, take an audit sample, summarize approved spending, and export English and Korean reports.
# 
# > Run this notebook from the repository root. The data is synthetic.

# %% [markdown]
# ## Before we get started
# 
# 1. Add the following python package to your environment (to export notebooks to HTML):
#    - `notebook`
# 
#     In this class, we use UV for Python management, Python packages are installed with uv add xxx
# 
# 2. Download the `inbox.zip` dataset from iCampus and save it in the `data/inbox` directory.
#    - check if your data folder is being ignored by `.gitignore`

# %% [markdown]
# ## 1. Discover and list the files in the messy inbox
# - More information about the pathlib module: https://medium.com/data-science/why-you-should-start-using-pathlib-as-an-alternative-to-the-os-module-d9eccd994745

# %%
## Let's define the location of the data, output, and temporary directories so that we don't need to hardcode and repeat paths throughout the code
from pathlib import Path

data_dir = Path("data/inbox")
output_dir = Path("outputs")
temp_dir = Path("temp")

## Then, let's create the output and temporary directories if they don't already exist

output_dir.mkdir(parents=True, exist_ok=True)
temp_dir.mkdir(parents=True, exist_ok=True)

# %%
## Then, let's list all files in the data directory
## show Path(data_dir).iterdir() first for demonstration

list(data_dir.iterdir())

all_files_glob = [str(path) for path in Path(data_dir).iterdir()]

print(all_files_glob)

# %%
all_files_glob

# %%
# Filter all file paths in the all_files_glob list to include only CSV and Excel files

data_files = [f for f in all_files_glob if f.endswith('.csv') or f.endswith('.xlsx')]

data_files


# %%
## Create DataFrame of Files to get a structured view of all CSV and Excel files
import pandas as pd

files_df = pd.DataFrame({
    'filename': data_files,
    'filetype': ['csv' if f.endswith('.csv') else 'xlsx' for f in data_files]
})

files_df.head(10)

# %%
## Lets create two lists for each filetype 

csv_files = [f for f in data_files if f.endswith('.csv')]
xlsx_files = [f for f in data_files if f.endswith('.xlsx')]

print("CSV Files:", csv_files)
print("Excel Files:", xlsx_files)

# %%
## Let's print a preview of some CSV files. What is the same? What is different?

csv_preview = pd.read_csv(csv_files[8]) # Try some more by changing the index
csv_preview.head()

# %%
## Let's do the same for the Excel files

excel_preview = pd.read_excel(xlsx_files[4])
excel_preview.head()

# %% [markdown]
# ## 2. Merging the DataFrames
# 
# `pandas.concat()` function concatenate two or more pandas objects like DataFrames or Series along a particular axis. It is especially useful when combining datasets either vertically (row-wise) or horizontally (column-wise). Read about using conact to append dataframes in pandas: [Future Replacement of the Append Method in Panda Python](https://www.geeksforgeeks.org/python/future-replacement-of-the-append-method-in-panda-python/)

# %%
## Append all CSV files into a single DataFrame and then inspect it
csv_combined_df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

print(f"Combined shape: {csv_combined_df.shape}")
csv_combined_df.head()

# %%
## Check all the columns in the combined DataFrame
csv_combined_df.columns

# %% [markdown]
# You can find the column mapping for the cell below at https://github.com/pimatskku/BAM5103/blob/main/column_mapping.txt

# %%
## Build a mapping table from each department's column names to the canonical schema
# Canonical fields: transaction_id, expense_date, department, category, vendor, amount_krw, approval_status, employee_id, description

column_mapping = {
    # HR convention
    "ID": "transaction_id",
    "Expense Date": "expense_date",
    "Dept": "department",
    "Cost Category": "category",
    "Merchant": "vendor",
    "Total": "amount_krw",
    "Approved?": "approval_status",
    "Staff ID": "employee_id",
    "Note": "description",
    # Sales convention
    "expense_id": "transaction_id",
    "transaction_date": "expense_date",
    "team": "department",
    "expense_type": "category",
    "supplier": "vendor",
    "amount": "amount_krw",
    "approval": "approval_status",
    "employee": "employee_id",
    "memo": "description",
    # Marketing convention
    "Transaction ID": "transaction_id",
    "Date": "expense_date",
    "Department": "department",
    "Category": "category",
    "Vendor": "vendor",
    "Amount KRW": "amount_krw",
    "Status": "approval_status",
    "Employee ID": "employee_id",
    "Description": "description",
    # Operations convention (Korean)
    "전표번호": "transaction_id",
    "사용일": "expense_date",
    "부서": "department",
    "항목": "category",
    "거래처": "vendor",
    "금액(원)": "amount_krw",
    "승인상태": "approval_status",
    "사번": "employee_id",
    "내역": "description",
}

# %%
## Read each CSV, rename its columns to the canonical schema, add a source column then combine them all
renamed_csv_dataframes = []

for f in csv_files:
    df = pd.read_csv(f)
    df = df.rename(columns=column_mapping)
    df['source'] = f.split('/')[-1]
    renamed_csv_dataframes.append(df)

csv_combined_df = pd.concat(renamed_csv_dataframes, ignore_index=True)
print(f"Combined CSV shape: {csv_combined_df.shape}")

# %%
## Let's add the Excel files to the combined DataFrame as well
renamed_excel_dataframes = []

for f in xlsx_files:
    df = pd.read_excel(f)
    df = df.rename(columns=column_mapping)
    df['source'] = f.split('/')[-1]
    renamed_excel_dataframes.append(df)

excel_combined_df = pd.concat(renamed_excel_dataframes, ignore_index=True)

print(f"Combined Excel shape: {excel_combined_df.shape}")

all_combined_df = pd.concat([csv_combined_df, excel_combined_df], ignore_index=True)
print(f"All combined shape: {all_combined_df.shape}")


# %% [markdown]
# ## 3. Get a sample from the DataFrame
# 
# Pandas `DataFrame.sample()` function is used to select randomly rows or columns from a DataFrame. It proves particularly helpful while dealing with huge datasets where we want to test or analyze a small representative subset. We can define the number or proportion of items to sample and manage randomness through parameters such as n, frac and random_state. [Read more...](https://www.geeksforgeeks.org/python/python-pandas-dataframe-sample/)

# %%
## Lets discover the newly merged dataframe by sampling a few rows. What should be fixed next?

all_combined_df.sample(10)

# %% [markdown]
# https://github.com/pimatskku/BAM5103/blob/main/value_mappings.txt

# %%
## Paste value mappings from https://github.com/pimatskku/BAM5103/blob/main/value_mappings.txt below

department_mapping = {
    "Marketing": "Marketing", "MKT": "Marketing", "마케팅": "Marketing",
    "Sales": "Sales", "SLS": "Sales", "영업": "Sales",
    "Operations": "Operations", "OPS": "Operations", "운영": "Operations",
    "HR": "HR", "People": "HR", "인사": "HR",
}

category_mapping = {
    "Advertising": "Advertising", "Ads": "Advertising", "광고비": "Advertising",
    "Software": "Software", "SaaS": "Software", "소프트웨어": "Software",
    "Travel": "Travel", "Business Travel": "Travel", "출장비": "Travel",
    "Meals": "Meals", "Food": "Meals", "식비": "Meals",
    "Client Events": "Client Events", "Events": "Client Events", "고객행사": "Client Events",
    "Office Supplies": "Office Supplies", "Supplies": "Office Supplies", "사무용품": "Office Supplies",
    "Logistics": "Logistics", "Delivery": "Logistics", "물류비": "Logistics",
    "Training": "Training", "L&D": "Training", "교육비": "Training",
    "Recruiting": "Recruiting", "Hiring": "Recruiting", "채용비": "Recruiting",
}

status_mapping = {
    "Approved": "Approved", "Y": "Approved", "승인": "Approved",
    "Pending": "Pending", "Review": "Pending", "검토중": "Pending",
    "Rejected": "Rejected", "N": "Rejected", "반려": "Rejected",
}

# %% [markdown]
# ## 4. Transforming (mapping) the values in the dataset with our mapping dictionaries
# 
# Pandas is a widely used library for manipulating datasets. There are various in-built functions of pandas, one such function is `pandas.map()`, which is used to map values from two series having one similar column. For mapping two series, the last column of the first should be the same as the index column of the second series, also the values should be unique. [Read more...](https://www.geeksforgeeks.org/python/python-pandas-map/)

# %%
## Before we map the values in the dataframe, we create a copy to preserve the original dataframe
transformed_df = all_combined_df.copy()

# %%
## Let's transform the values in the dataframe using the mapping dictionaries we created
transformed_df['department'] = transformed_df['department'].map(department_mapping)
transformed_df['category'] = transformed_df['category'].map(category_mapping)
transformed_df['approval_status'] = transformed_df['approval_status'].map(status_mapping)

# %%
## Let's check the first few rows of the transformed dataframe to ensure the mappings were applied correctly
transformed_df.sample(10)

# %%
transformed_df['category'].unique()

# %%
## Export to Excel to have a easier view of the data

transformed_df.to_excel(temp_dir / "combined_data.xlsx")

# %%
## A little trick to save Excel files with a timestamp

## Use the timestamp in the filename when exporting to Excel
import datetime
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
transformed_df.to_excel(temp_dir / f"data_{timestamp}.xlsx", index=False)

## Add your temp folder to .gitignore to avoid committing temporary files

# %% [markdown]
# ### Converting Columns to Datetime
# 
# `pandas.to_datetime()` converts argument(s) to datetime. This function is essential for working with date and time data, especially when parsing strings or timestamps into Python's datetime64 format used in Pandas. [Read more](https://www.geeksforgeeks.org/pandas/python-pandas-to_datetime/)

# %%
## Let's convert the expense_date column to datetime format
# The "mixed" format allows pandas to infer the datetime format for each entry individually. This is useful when the column contains multiple date formats.
# If a date cannot be parsed, it will be set to NaT (Not a Time) due to errors="coerce".

transformed_df["expense_date"] = pd.to_datetime(transformed_df["expense_date"], format="mixed", errors="coerce")

# %%
transformed_df.info()

# %%
## And add at 'month' column to transformed_df 
transformed_df['month'] = transformed_df['expense_date'].dt.month

# %%
## Let's convert the amount_krw column to numeric values
transformed_df['amount_krw'] = pd.to_numeric(
    transformed_df["amount_krw"].astype("string").str.replace(",", "", regex=False),
    errors="coerce",
)

# %%
transformed_df.head(4)

# %%
# Less find out if there are duplicates in the transaction_id column

transformed_df.sample(10)

# %%
transformed_df.info()
transformed_df.duplicated("transaction_id").sum()

# %% [markdown]
# ## 5. Quality checks

# %%
print("Date range:", transformed_df["expense_date"].min(), "to", transformed_df["expense_date"].max())
print("Duplicate IDs:", transformed_df["transaction_id"].duplicated().sum())
print("\nMissing values:")
(transformed_df.isna().sum().sort_values(ascending=False))

for column in ["department", "category", "approval_status"]:
    print(column, sorted(transformed_df[column].dropna().unique()))

transformed_df.loc[transformed_df["amount_krw"].isna()]

# %%
## Create an excel file with all the records that contain a missing value so that this can be sent back to the data provider
transformed_df[transformed_df.isnull().any(axis=1)].to_excel("outputs/missing_values.xlsx", index=False)

# %% [markdown]
# ## 6. Create a reproducable audit sample

# %%
audit_sample = transformed_df.sample(n=100, random_state=50)
transformed_df.sort_values(by='amount_krw',ascending=False)

#print(audit_sample.head())
print(largest_expenses[["transaction_id", "department", "category", "amount_krw"]])

audit_sample.to_excel(temp_dir / "audit_sample.xlsx", index=False)

# %% [markdown]
# ## 7. Filter, group, and aggregate
# 
# Create two summaries:
# - One monthy summary (total approved spending per month, sorted by month)
# - One summary of spendings grouped by department and category, sorted by total amount spent

# %%
## Create a copy of the dataframe with only approved transactions
approved = transformed_df[transformed_df['approval_status'] == "Approved"].copy()

monthly_summary = (
    approved.groupby("month", as_index=False)["amount_krw"]
    .sum()
    .sort_values("month")
)

department_summary = (
    approved.groupby(["department", "category"], as_index=False)["amount_krw"]
    .sum()
    .sort_values("amount_krw", ascending=False)
)

print(monthly_summary)
print(department_summary.head(10))

# %% [markdown]
# ## 8. Make presentation-ready English charts

# %% [markdown]
# Seaborn is a Python data visualization library based on matplotlib. It provides a high-level interface for drawing attractive and informative statistical graphics. The overall package not only has a nice aesthetic quality, but it provides meaningful insights to us as well. [Read more](https://www.geeksforgeeks.org/python/seaborn-lineplot-method-in-python/)

# %%
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

fig, ax = plt.subplots(figsize=(9, 4.5))
sns.lineplot(data=monthly_summary, x="month", y="amount_krw", marker="o", linewidth=2.5, ax=ax)
ax.set_xticks(monthly_summary["month"])
ax.set(title="Approved expenses by month", xlabel="Month", ylabel="KRW millions")
ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value / 1_000_000:.0f}"))
sns.despine()
fig.tight_layout()
fig.savefig("outputs/monthly_spend_en.png", dpi=180, bbox_inches="tight")
plt.show()

# %%
department_totals = (
    approved.groupby("department", as_index=False)["amount_krw"]
    .sum()
    .sort_values("amount_krw", ascending=True)
)

fig, ax = plt.subplots(figsize=(8, 4.5))
sns.barplot(data=department_totals, x="amount_krw", y="department", color="#3978A8", ax=ax)
ax.set(title="Approved expenses by department", xlabel="KRW millions", ylabel="")
ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value / 1_000_000:.0f}"))
sns.despine()
fig.tight_layout()
fig.savefig("outputs/department_spend_en.png", dpi=180, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 9. Reuse results for Korean output

# %%
DEPARTMENT_KR = {"Marketing": "마케팅", "Sales": "영업", "Operations": "운영", "HR": "인사"}
CATEGORY_KR = {
    "Advertising": "광고비", "Software": "소프트웨어", "Travel": "출장비",
    "Meals": "식비", "Client Events": "고객행사", "Office Supplies": "사무용품",
    "Logistics": "물류비", "Training": "교육비", "Recruiting": "채용비",
}

department_summary_kr = department_summary.copy()
department_summary_kr["department"] = department_summary_kr["department"].replace(DEPARTMENT_KR)
department_summary_kr["category"] = department_summary_kr["category"].replace(CATEGORY_KR)
department_summary_kr = department_summary_kr.rename(columns={
    "department": "부서", "category": "항목", "amount_krw": "금액(원)"
})

print(department_summary_kr.head())

# %%
department_totals_kr = department_totals.copy()
department_totals_kr["department"] = department_totals_kr["department"].replace(DEPARTMENT_KR)

plt.rc('font', family=['Malgun Gothic'])


fig, ax = plt.subplots(figsize=(8, 4.5))
sns.barplot(data=department_totals_kr, x="amount_krw", y="department", color="#3978A8", ax=ax)
ax.set(title="부서별 승인 비용", xlabel="금액(백만원)", ylabel="")
ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value / 1_000_000:.0f}"))
sns.despine()
fig.tight_layout()
fig.savefig("outputs/department_spend_kr.png", dpi=180, bbox_inches="tight")
plt.show()

# %%
## Save the cleaned and transformed expenses to one Excel
transformed_df.to_excel(output_dir / "clean_expenses.xlsx", index=False)

## Then save the summary of expenses to separate Excel files for English and Korean versions

with pd.ExcelWriter(output_dir / "expense_summary_en.xlsx") as writer:
    monthly_summary.to_excel(writer, sheet_name="Monthly", index=False)
    department_summary.to_excel(writer, sheet_name="Department category", index=False)

with pd.ExcelWriter(output_dir / "expense_summary_kr.xlsx") as writer:
    monthly_summary.rename(columns={"month": "월", "amount_krw": "금액(원)"}).to_excel(
        writer, sheet_name="월별", index=False
    )
    department_summary_kr.to_excel(writer, sheet_name="부서_항목", index=False)

# %% [markdown]
# ## 10. Export this script to a Python file
# 
# Now that your Notebook is tested and working correctly, you can export it to a Python file for further use or deployment.
# 
# - Open the VS Code command palette (Ctrl+Shift+P or Cmd+Shift+P on Mac).
# - Search for "Jupyter: Export to Python Script"
# - A new editor tab will open with the exported Python script.
# - Save the file to your desired location, for example `process_spendings.py`
# 
# Now delete all the output in the outputs folder and run the exported Python script to regenerate the outputs.

# %% [markdown]
# ## Doom scenario
# 
# It's Friday 5:30pm and your manager walks into your office, pretty excited that he just received the monthly expense reports of June...
# 
# How long will it take you to add these numbers to the reports and charts?

# %% [markdown]
# 


