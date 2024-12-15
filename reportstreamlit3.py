import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from docx import Document
import io

def analyze_csv(file_name):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_name)
    
    # Rename the columns
    df.rename(columns={
        'pH': 'pH F/D',
        'COD': 'COD F/D',
        'SS': 'SS F/D',
        'Zn': 'Zn F/D'
    }, inplace=True)
    
    # Convert 'Date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Calculate average values for each parameter
    avg_ph = df['pH F/D'].mean()
    avg_cod = df['COD F/D'].mean()
    avg_ss = df['SS F/D'].mean()
    avg_zn = df['Zn F/D'].mean()
    
    # Identify non-compliance dates
    non_compliance_dates = []
    for index, row in df.iterrows():
        exceeded_params = []
        if row['COD F/D'] > 100:
            exceeded_params.append(f"COD F/D: {row['COD F/D']}")
        if row['SS F/D'] > 100:
            exceeded_params.append(f"SS F/D: {row['SS F/D']}")
        if row['Zn F/D'] > 1.0:
            exceeded_params.append(f"Zn F/D: {row['Zn F/D']}")
        if not (5.5 <= row['pH F/D'] <= 9.0):
            exceeded_params.append(f"pH F/D: {row['pH F/D']}")
        
        if exceeded_params:
            non_compliance_dates.append({
                'Date': row['Date'],
                'Parameters Exceeded': ', '.join(exceeded_params)
            })
    
    # Calculate percentage of passing and failing discharge standards
    total_days = len(df)
    passing_days = total_days - len(non_compliance_dates)
    passing_percentage = (passing_days / total_days) * 100
    failing_percentage = 100 - passing_percentage
    
    return df, avg_ph, avg_cod, avg_ss, avg_zn, non_compliance_dates, passing_percentage, failing_percentage

def generate_report_text(df, avg_ph, avg_cod, avg_ss, avg_zn, non_compliance_dates, passing_percentage, failing_percentage):
    report_text = f"**IETS BIG Data Analysis Report USING A.I ANALYTICS:**\n\n"
    report_text += f"**Report Date and Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report_text += f"**Reference Number:** [Insert Reference Number]\n"
    report_text += f"**Logsheets Referral:** [Insert Logsheets Referral]\n\n"
    
    report_text += "### 1. TOWS Analysis:\n"
    report_text += "- **Threats:** Equipment malfunctions, sensor inaccuracies, high incoming flowrate, low chemicals in tank.\n"
    report_text += "- **Opportunities:** Implementing regular maintenance schedules, improving sensor calibration, optimizing chemical dosing.\n"
    report_text += "- **Weaknesses:** Fluctuations in key parameters, non-compliance with discharge standards on specific dates.\n"
    report_text += "- **Strengths:** Availability of detailed logsheets data, ability to analyze and identify patterns.\n\n"
    
    report_text += "### 2. Data Analytics:\n"
    report_text += f"- The data covers various dates from {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}.\n"
    report_text += "- The data is collected from the monitoring systems of the facility.\n"
    report_text += "- The purpose of this report is to provide insights into the behavior of key parameters (pH F/D, COD F/D, SS F/D, Zn F/D), identify dates of non-compliance with discharge standards, and offer recommendations for improvement.\n\n"
    
    report_text += "### Average Behavior:\n"
    report_text += f"- **Average pH F/D:** {avg_ph:.2f}\n"
    report_text += f"- **Average COD F/D:** {avg_cod:.2f}\n"
    report_text += f"- **Average SS F/D:** {avg_ss:.2f}\n"
    report_text += f"- **Average Zn F/D:** {avg_zn:.2f}\n\n"
    
    report_text += "### Non-Compliance Dates and Reasons:\n"
    for entry in non_compliance_dates:
        report_text += f"- **Date:** {entry['Date'].strftime('%Y-%m-%d')}\n"
        report_text += f"  - **Parameter(s) Exceeded:** {entry['Parameters Exceeded']}\n\n"
    
    report_text += "### Percentage of Passing and Failing Discharge Standards:\n"
    report_text += f"- **Percentage of Passing Discharge Standards:** {passing_percentage:.2f}%\n"
    report_text += f"- **Percentage of Failing Discharge Standards:** {failing_percentage:.2f}%\n\n"
    
    report_text += "### Overall Conclusion:\n"
    report_text += "- The analysis indicates that there are fluctuations in the key parameters over time. Specific dates show significant deviations which need to be addressed.\n\n"
    
    report_text += "### Recommendations:\n"
    report_text += "1. **Regularly calibrate sensors** to ensure accurate readings.\n"
    report_text += "2. **Investigate and address the causes** of high COD and SS levels on specific dates.\n"
    report_text += "3. **Implement a maintenance schedule** to prevent equipment malfunctions.\n"
    report_text += "4. **Ensure proper chemical dosing** to maintain optimal pH levels.\n"
    report_text += "5. **Review and adjust operational procedures** to prevent future non-compliance.\n\n"
    
    return report_text

def main():
    st.title("Wastewater Treatment, IETS    Report + Analysis © ")

    # File uploader
    uploaded_file = st.file_uploader("Upload  CSV file", type="csv")
    
    if uploaded_file is not None:
        # Analyze the CSV file
        df, avg_ph, avg_cod, avg_ss, avg_zn, non_compliance_dates, passing_percentage, failing_percentage = analyze_csv(uploaded_file)

        # Generate report text
        report_text = generate_report_text(df, avg_ph, avg_cod, avg_ss, avg_zn, non_compliance_dates, passing_percentage, failing_percentage)

        # Display report
        st.write(report_text)

        # Graphical Representation of Data Trends
        st.subheader("Trends of Key Parameters Over Time")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df['Date'], df['pH F/D'], label='pH F/D')
        ax.plot(df['Date'], df['COD F/D'], label='COD F/D')
        ax.plot(df['Date'], df['SS F/D'], label='SS F/D')
        ax.plot(df['Date'], df['Zn F/D'], label='Zn F/D')
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.set_title('Trends of Key Parameters Over Time')
        ax.legend()
        st.pyplot(fig)

        # Download button for the report
        doc = Document()
        doc.add_paragraph(report_text)
        docx_file = io.BytesIO()
        doc.save(docx_file)
        docx_file.seek(0)
        
        st.download_button(
            label="Download Report as .docx",
            data=docx_file,
            file_name="IETS_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

if __name__ == "__main__":
    main()
