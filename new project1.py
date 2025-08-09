import tkinter as tk
from tkinter import filedialog, Text, Scrollbar, Label, Button
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tkinter import messagebox

main = tk.Tk()
main.title("Startup Funding Analysis")
main.geometry("1300x1200")

font = ('times', 16, 'bold')
title = Label(main, text='Startup Funding Data Analysis GUI')
title.config(bg='greenyellow', fg='dodger blue')
title.config(font=font)
title.config(height=3, width=120)
title.place(x=0, y=5)

font1 = ('times', 12, 'bold')
text = Text(main, height=25, width=90)
scroll = Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=500, y=150)
text.config(font=font1)

# Global dataset
df = None

def uploadDataset():
    global df
    file_path = filedialog.askopenfilename()
    if file_path:
        df = pd.read_csv(file_path, encoding='latin1')
        text.delete('1.0', tk.END)
        text.insert(tk.END, "Dataset uploaded successfully!\n\n")
        text.insert(tk.END, "Initial Columns:\n")
        text.insert(tk.END, f"Raw Columns: {list(df.columns)}\n")
        df.columns = df.columns.str.strip()  # Strip column names immediately
        text.insert(tk.END, f"Cleaned Columns: {list(df.columns)}\n\n")
        text.insert(tk.END, "Data Types and Null Counts:\n")
        info_str = df.dtypes.to_string() + "\n\n" + df.isnull().sum().to_string()
        text.insert(tk.END, info_str + "\n\n")
        text.insert(tk.END, "First few rows:\n")
        text.insert(tk.END, df.head())

def showCleaningSteps():
    global df
    if df is None:
        messagebox.showerror("Error", "Please upload dataset first")
        return

    text.delete('1.0', tk.END)
    text.insert(tk.END, " Dataset Cleaning Report (Before Cleaning):\n\n")

    # Column names before cleaning
    text.insert(tk.END, " Original Column Names:\n")
    text.insert(tk.END, f"{list(df.columns)}\n\n")

    # Detect columns with spaces in names
    spaces_in_columns = [col for col in df.columns if ' ' in col or col != col.strip()]
    if spaces_in_columns:
        text.insert(tk.END, f"Columns with spaces: {spaces_in_columns}\n\n")

    # Null value report
    text.insert(tk.END, "Null Values per Column:\n")
    text.insert(tk.END, f"{df.isnull().sum()}\n\n")

    # Data types
    text.insert(tk.END, " Current Data Types:\n")
    text.insert(tk.END, f"{df.dtypes}\n\n")

    # Check Amount in USD issues
    if 'Amount in USD' in df.columns:
        invalid_amount = df['Amount in USD'].astype(str).str.contains('[^0-9,]', na=False).sum()
        text.insert(tk.END, f"'Amount in USD' entries with non-numeric values: {invalid_amount}\n\n")

    # Check Date issues
    if 'Date' in df.columns:
        invalid_dates = pd.to_datetime(df['Date'], errors='coerce').isnull().sum()
        text.insert(tk.END, f"Invalid date entries: {invalid_dates}\n\n")

    text.insert(tk.END, "These are the issues that will be fixed in cleaning.\n")



def runcleandata():
    global df
    if df is None:
        messagebox.showerror("Error", "Please upload dataset first")
        return

    text.delete('1.0', tk.END)
    text.insert(tk.END, "Cleaning dataset...\n")

    # 1. Standardise column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    # 2. Drop completely empty rows
    df.dropna(how='all', inplace=True)

    # 3. Handle City column
    if 'city_location' not in df.columns:
        df['city_location'] = "Unknown"
    else:
        df['city_location'] = df['city_location'].fillna("Unknown")

    # 4. Handle Date column
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # 5. Clean Amount column
    if 'amount_in_usd' in df.columns:
        df['amount_in_usd'] = (
            df['amount_in_usd']
            .astype(str)
            .str.replace(',', '', regex=False)
            .str.strip()
        )
        df['amount_in_usd'] = pd.to_numeric(
            df['amount_in_usd'].replace("undisclosed", None),
            errors='coerce'
        )
        # Fill missing amounts with 0 instead of dropping
        df['amount_in_usd'] = df['amount_in_usd'].fillna(0)
    else:
        df['amount_in_usd'] = 0

    # 6. Fill other important text columns with "Unknown"
    for col in ['startup_name', 'industry_vertical']:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    # 7. Reset index
    df.reset_index(drop=True, inplace=True)

    text.insert(tk.END, "Data cleaned successfully!\n")
    text.insert(tk.END, f"Rows after cleaning: {len(df)}\n")
    text.insert(tk.END, f"Columns: {list(df.columns)}\n")


def visualizeinsights():
    global df
    if df is None or df.empty:
        messagebox.showerror("Error", "Please upload and clean dataset first")
        return

    try:
        # Funding trends over time
        if 'date' in df.columns:
            trend_data = df.groupby(df['date'].dt.year)['amount_in_usd'].sum().reset_index()
            plt.figure(figsize=(8, 5))
            sns.lineplot(data=trend_data, x='date', y='amount_in_usd', marker='o')
            plt.title("Funding Trends Over Time")
            plt.xlabel("Year")
            plt.ylabel("Total Funding (USD)")
            plt.tight_layout()
            plt.show(block=False)
            plt.pause(0.1)

        # Top sectors
        if 'industry_vertical' in df.columns:
            plt.figure(figsize=(8, 5))
            top_sectors = df['industry_vertical'].value_counts().head(5)
            sns.barplot(x=top_sectors.values, y=top_sectors.index)
            plt.title("Top 5 Sectors by Startup Count")
            plt.xlabel("Number of Startups")
            plt.ylabel("Sector")
            plt.tight_layout()
            plt.show(block=False)
            plt.pause(0.1)

        # Top cities
        if 'city_location' in df.columns:
            plt.figure(figsize=(8, 5))
            top_cities = df['city_location'].value_counts().head(5)
            sns.barplot(x=top_cities.values, y=top_cities.index)
            plt.title("Top 5 Cities by Startup Count")
            plt.xlabel("Number of Startups")
            plt.ylabel("City")
            plt.tight_layout()
            plt.show(block=False)
            plt.pause(0.1)

        # Top startups
        if 'startup_name' in df.columns:
            plt.figure(figsize=(8, 5))
            top_startups = df['startup_name'].value_counts().head(5)
            sns.barplot(x=top_startups.values, y=top_startups.index)
            plt.title("Top 5 Startups by Funding Count")
            plt.xlabel("Number of Fundings")
            plt.ylabel("Startup")
            plt.tight_layout()
            plt.show(block=False)
            plt.pause(0.1)

        # Active investors
        if 'investors_name' in df.columns:
            plt.figure(figsize=(8, 5))
            top_investors = df['investors_name'].value_counts().head(5)
            sns.barplot(x=top_investors.values, y=top_investors.index)
            plt.title("Top 5 Active Investors")
            plt.xlabel("Number of Investments")
            plt.ylabel("Investor")
            plt.tight_layout()
            plt.show(block=False)
            plt.pause(0.1)

        # Investment type distributions
        if 'investment_type' in df.columns:
            plt.figure(figsize=(8, 5))
            sns.countplot(data=df, y='investment_type', order=df['investment_type'].value_counts().index)
            plt.title("Investment Type Distribution")
            plt.xlabel("Count")
            plt.ylabel("Investment Type")
            plt.tight_layout()
            plt.show(block=False)
            plt.pause(0.1)

    except Exception as e:
        messagebox.showerror("Error", f"Visualization failed: {str(e)}")


def Dataanalyse():
    global df
    if df is None or df.empty:
        messagebox.showerror("Error", "Please upload and clean dataset first")
        return

    text.delete('1.0', tk.END)
    text.insert(tk.END, "Startup Funding Analysis\n")
    text.insert(tk.END, "-" * 40 + "\n")

    try:
        # Funding trends over time
        if 'date' in df.columns:
            funding_trend = df.groupby(df['date'].dt.year)['amount_in_usd'].sum()
            text.insert(tk.END, "\nFunding Trends (by Year):\n")
            text.insert(tk.END, f"{funding_trend}\n")

        # Top sectors
        if 'industry_vertical' in df.columns:
            top_sectors = df['industry_vertical'].value_counts().head(5)
            text.insert(tk.END, "\nTop 5 Sectors:\n")
            text.insert(tk.END, f"{top_sectors}\n")

        # Top cities
        if 'city_location' in df.columns:
            top_cities = df['city_location'].value_counts().head(5)
            text.insert(tk.END, "\nTop 5 Cities:\n")
            text.insert(tk.END, f"{top_cities}\n")

        # Top startups
        if 'startup_name' in df.columns:
            top_startups = df['startup_name'].value_counts().head(5)
            text.insert(tk.END, "\nTop 5 Startups:\n")
            text.insert(tk.END, f"{top_startups}\n")

        # Active investors
        if 'investors_name' in df.columns:
            active_investors = df['investors_name'].value_counts().head(5)
            text.insert(tk.END, "\nTop 5 Active Investors:\n")
            text.insert(tk.END, f"{active_investors}\n")

        # Investment type distributions
        if 'investment_type' in df.columns:
            inv_type_dist = df['investment_type'].value_counts()
            text.insert(tk.END, "\nInvestment Type Distribution:\n")
            text.insert(tk.END, f"{inv_type_dist}\n")

        text.insert(tk.END, "\n Analysis Completed!\n")

    except Exception as e:
        messagebox.showerror("Error", f"Analysis failed: {str(e)}")




def showinsights():
    global df
    if df is None:
        messagebox.showerror("Error", "Please upload and clean dataset first")
        return

    summary = f"""
Recommendations:

1. Focus on top funding sectors like Tech, Finance, and Healthcare.
2. Mumbai, Bangalore, and Delhi NCR are major hubs for startups.
3. Encourage repeat investments from top investors like Sequoia, Accel, and Tiger Global.
4. Series A and Seed Funding dominate; early-stage funding is strong.
5. Consider funding trends over time to predict peak investment periods.
    """
    text.delete('1.0', tk.END)
    text.insert(tk.END, summary)



font1 = ('times', 13, 'bold')

uploadButton = Button(main, text="Upload Kaggle Dataset", command=uploadDataset)
uploadButton.place(x=50, y=150)
uploadButton.config(font=font1)

cleanStepsButton = Button(main, text="Show Cleaning Steps", command=showCleaningSteps)
cleanStepsButton.place(x=50, y=250)
cleanStepsButton.config(font=font1)

cleanDataButton = Button(main, text="Clean Data", command=runcleandata)
cleanDataButton.place(x=50, y=350)
cleanDataButton.config(font=font1)

analyseButton = Button(main, text="Analyze Data", command=Dataanalyse)
analyseButton.place(x=50, y=450)
analyseButton.config(font=font1)

visualizeButton = Button(main, text="Visualize Insights", command=visualizeinsights)
visualizeButton.place(x=50, y=550)
visualizeButton.config(font=font1)

recommendButton = Button(main, text="Recommendations", command=showinsights)
recommendButton.place(x=50, y=650)
recommendButton.config(font=font1)

main.config(bg='LightSkyBlue')
main.mainloop()
