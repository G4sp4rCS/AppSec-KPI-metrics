#!/usr/bin/env python3

import argparse
import sys
import pandas as pd
from colorama import Fore, Style
import matplotlib.pyplot as plt

# Define closed statuses
CLOSED_STATUSES = ['done', 'cancelled', 'resolved']
def print_banner():
    banner = f"""
{Fore.CYAN}    ___               _____              __  ___     __       _{Style.RESET_ALL}
{Fore.CYAN}   /   |  ____  ____ / ___/___  _____   /  |/  /__  / /______(_)_________{Style.RESET_ALL}
{Fore.CYAN}  / /| | / __ \\/ __ \\\\__ \\/ _ \\/ ___/  / /|_/ / _ \\/ __/ ___/ / ___/ ___/{Style.RESET_ALL}
{Fore.CYAN} / ___ |/ /_/ / /_/ /__/ /  __/ /__   / /  / /  __/ /_/ /  / / /__(__  ){Style.RESET_ALL}
{Fore.CYAN}/_/  |_/ .___/ .___/____/\\___/\\___/  /_/  /_/\\___/\\__/_/  /_/\\___/____/{Style.RESET_ALL}
{Fore.CYAN}      /_/   /_/                                              {Style.RESET_ALL}
                                              
{Fore.YELLOW}Made by grunt.ar{Style.RESET_ALL}
"""
    print(banner)

def load_data(csv_path: str) -> pd.DataFrame:
    """Load CSV data from the specified path."""
    try:
        data = pd.read_csv(csv_path)
        # Strip any leading/trailing spaces from column names
        data.columns = data.columns.str.strip()
    except Exception as e:
        print(f"Error loading the file: {e}")
        sys.exit(1)
    return data

def check_columns(data: pd.DataFrame, required_cols: list) -> None:
    """Check if the required columns are present in the data."""
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        print(f"Error: missing required columns: {', '.join(missing)}")
        sys.exit(1)

def calc_nacv(data: pd.DataFrame, priority_col: str, status_col: str) -> None:
    """Calculate the Number of Active Critical Vulnerabilities (NACV)."""
    check_columns(data, [priority_col, status_col])
    critical_open = data[(data[priority_col].str.contains("Critical", case=False, na=False)) &
                         (~data[status_col].str.lower().isin(CLOSED_STATUSES))]
    print(f"Number of active critical vulnerabilities (NACV): {len(critical_open)}")

def calc_ttr(data: pd.DataFrame, created_col: str, resolved_col: str) -> None:
    """Calculate the average Time to Remedy (TTR)."""
    check_columns(data, [created_col, resolved_col])
    data[created_col] = pd.to_datetime(data[created_col], errors='coerce')
    data[resolved_col] = pd.to_datetime(data[resolved_col], errors='coerce')
    # Filter rows where both dates are not NaT
    valid_dates = data.dropna(subset=[created_col, resolved_col])
    if valid_dates.empty:
        print("No vulnerabilities with valid remediation times.")
        return
    valid_dates['Remediation Time'] = (valid_dates[resolved_col] - valid_dates[created_col]).dt.days
    average_ttr = valid_dates['Remediation Time'].mean()
    print(f"Average remediation time (TTR): {round(average_ttr, 2)} days")

def calc_nvt(data: pd.DataFrame, team_col: str, exclude_teams: list) -> None:
    """Calculate the Number of Vulnerabilities per Team (NVT)."""
    check_columns(data, [team_col])
    teams_data = data[~data[team_col].isin(exclude_teams)]
    counts = teams_data[team_col].value_counts()
    # Plot
    plt.figure(figsize=(10, 10))
    counts.plot(kind='pie', autopct='%1.1f%%', startangle=90)
    plt.title("Distribution of Vulnerabilities by Team")
    plt.ylabel('')
    plt.tight_layout()
    plt.show()
    print("Number of vulnerabilities per team:")
    print(counts.sort_values(ascending=False))

def calc_ttrc(data: pd.DataFrame, created_col: str, resolved_col: str, severity_col: str) -> None:
    """Calculate the average Time to Remedy per Criticity (TTRC)."""
    check_columns(data, [created_col, resolved_col, severity_col])
    data[created_col] = pd.to_datetime(data[created_col], errors='coerce')
    data[resolved_col] = pd.to_datetime(data[resolved_col], errors='coerce')
    # Filter rows where both dates are not NaT
    valid_dates = data.dropna(subset=[created_col, resolved_col])
    if valid_dates.empty:
        print("No vulnerabilities with valid remediation times.")
        return
    valid_dates['Remediation Time'] = (valid_dates[resolved_col] - valid_dates[created_col]).dt.days
    ttr_by_sev = valid_dates.groupby(severity_col)['Remediation Time'].mean().sort_values()
    # Plot
    plt.rcParams.update({'font.size': 14})
    plt.figure(figsize=(12, 6))
    ttr_by_sev.plot(kind='bar', color='orange', edgecolor='black')
    plt.xlabel('Severity Level', fontsize=16)
    plt.ylabel('Average TTR (days)', fontsize=16)
    plt.title('Average Remediation Time by Severity Level', fontsize=18)
    plt.xticks(rotation=0, fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()
    print("\nAverage remediation time by severity:")
    print(ttr_by_sev.round(2))

if __name__ == '__main__':
    print_banner()  # Mostrar el banner al inicio
    parser = argparse.ArgumentParser(
        description="Calculate AppSec KPIs from a CSV file.",
        epilog="""
Examples:
  python3 kpi.py NACV all-issues.csv
  python3 kpi.py TTR all-issues.csv --created-col "Created" --resolved-col "Resolved"
  python3 kpi.py NVT all-issues.csv --team-col "Custom field (Squad Plataforma)" --exclude-teams "None" "Dev Ops"
  python3 kpi.py TTRC all-issues.csv --severity-col "Custom field (Severity)"
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('kpi', choices=['NACV', 'TTR', 'NVT', 'TTRC'], help="The KPI to calculate.")
    parser.add_argument('csv_file', help="Path to the CSV file.")
    parser.add_argument('--priority-col', default='Priority', help="Name of the priority column.")
    parser.add_argument('--status-col', default='Status', help="Name of the status column.")
    parser.add_argument('--created-col', default='Created', help="Name of the created date column.")
    parser.add_argument('--resolved-col', default='Resolved', help="Name of the resolved date column.")
    parser.add_argument('--severity-col', default='Custom field (Severity)', help="Name of the severity column.")
    parser.add_argument('--team-col', default='Custom field (Squad Plataforma)', help="Name of the team column.")
    parser.add_argument('--exclude-teams', nargs='*', default=['None', 'Dev Ops', 'Sistema de Diseño'], help="Teams to exclude from NVT calculation.")
    args = parser.parse_args()
    data = load_data(args.csv_file)
    if args.kpi == "NACV":
        calc_nacv(data, args.priority_col, args.status_col)
    elif args.kpi == "TTR":
        calc_ttr(data, args.created_col, args.resolved_col)
    elif args.kpi == "NVT":
        calc_nvt(data, args.team_col, args.exclude_teams)
    elif args.kpi == "TTRC":
        calc_ttrc(data, args.created_col, args.resolved_col, args.severity_col)