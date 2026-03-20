import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json
import os

# Set page configuration
st.set_page_config(
    page_title="Srashtikasoftware Employee Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling with more colors and interactive elements
st.markdown("""
<style>
    .main-header {
        font-size: 36px;
        font-weight: bold;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
        animation: gradient 3s ease infinite;
        background-size: 300% 300%;
    }
    
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    
    .sub-header {
        font-size: 28px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 10px;
        background: linear-gradient(45deg, #FF9AA2, #FFB7B2, #FFDAC1, #E2F0CB, #B5EAD7);
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        text-align: center;
        margin: 15px 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        color: white;
        border: 2px solid #fff;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.3);
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-label {
        font-size: 18px;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .footer {
        text-align: center;
        padding: 20px;
        color: #6c757d;
        font-size: 16px;
        background: linear-gradient(90deg, #f8f9fa, #e9ecef, #dee2e6);
        border-radius: 10px;
        margin-top: 20px;
    }
    
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stSelectbox>div>div>select {
        background: linear-gradient(45deg, #6C5CE7, #A29BFE);
        color: white;
        border-radius: 10px;
    }
    
    .stSlider>div>div>div {
        background: linear-gradient(90deg, #FD79A8, #FDCB6E);
    }
</style>
""", unsafe_allow_html=True)

# Title with animation
st.markdown('<div class="main-header">Srashtikasoftware Employee Dashboard</div>', unsafe_allow_html=True)
st.markdown("---")

# Initialize session state for attendance
if 'attendance_data' not in st.session_state:
    st.session_state.attendance_data = []

# Initialize session state for leave requests
if 'leave_requests' not in st.session_state:
    st.session_state.leave_requests = []

# Sidebar with colorful sections
st.sidebar.markdown("<h2 style='color: #FF6B6B;'>🧭 Navigation</h2>", unsafe_allow_html=True)
page = st.sidebar.radio("Go to", [
    "📊 Dashboard Overview", 
    "🏆 Employee Performance", 
    "🏢 Department Analytics", 
    "📅 Attendance Tracker", 
    "⏰ Mark Attendance",
    "🌴 Leave Management",
    "🚀 Project Management",
    "📦 Resource Allocation",
    "🎮 Interactive Tools"
])

st.sidebar.markdown("---")
st.sidebar.markdown("<h2 style='color: #4ECDC4;'>⚡ Quick Filters</h2>", unsafe_allow_html=True)
department_filter = st.sidebar.selectbox("🏢 Filter by Department", 
                                        ["All", "Engineering", "Marketing", "Sales", "HR", "Finance"])
date_range = st.sidebar.date_input("📅 Select Date Range", 
                                  [datetime.today() - timedelta(days=30), datetime.today()])

# Add a colorful sidebar button
if st.sidebar.button("🔄 Refresh Data"):
    st.experimental_rerun()

# Generate sample data
@st.cache_data
def generate_sample_data():
    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance"]
    employees = []
    for i in range(150):
        emp = {
            "Employee ID": f"EMP{i+1:04d}",
            "Name": f"Employee {i+1}",
            "Department": random.choice(departments),
            "Position": random.choice(["Manager", "Senior", "Mid-level", "Junior"]),
            "Salary": random.randint(40000, 150000),
            "Performance Score": round(random.uniform(2.0, 5.0), 1),
            "Projects Completed": random.randint(0, 20),
            "Attendance Rate": round(random.uniform(80, 100), 1),
            "Years at Company": random.randint(0, 15),
            "Satisfaction": round(random.uniform(1.0, 10.0), 1)
        }
        employees.append(emp)
    return pd.DataFrame(employees)

# Load data
df = generate_sample_data()

# Apply filters
if department_filter != "All":
    df = df[df["Department"] == department_filter]

# Dashboard Overview Page
if page == "📊 Dashboard Overview":
    st.markdown('<div class="sub-header">Dashboard Overview</div>', unsafe_allow_html=True)
    
    # Key Metrics with colorful cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">👥 Total Employees</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(df)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">⭐ Avg Performance</div>', unsafe_allow_html=True)
        avg_perf = df["Performance Score"].mean()
        st.markdown(f'<div class="metric-value">{avg_perf:.1f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">💰 Avg Salary</div>', unsafe_allow_html=True)
        avg_salary = df["Salary"].mean()
        st.markdown(f'<div class="metric-value">${avg_salary:,.0f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">📋 Attendance Rate</div>', unsafe_allow_html=True)
        avg_attendance = df["Attendance Rate"].mean()
        st.markdown(f'<div class="metric-value">{avg_attendance:.1f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts with vibrant colors
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Employees by Department")
        dept_counts = df["Department"].value_counts()
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        fig1 = px.pie(values=dept_counts.values, names=dept_counts.index, 
                     color_discrete_sequence=colors)
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("⭐ Performance Distribution")
        colors = ['#6C5CE7', '#A29BFE', '#FD79A8', '#FDCB6E', '#6A89CC']
        fig2 = px.histogram(df, x="Performance Score", nbins=20, 
                           color_discrete_sequence=colors)
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    # Interactive data table
    st.subheader("📋 Employee Data")
    st.dataframe(df.style.highlight_max(axis=0, color='#4ECDC4')
                 .highlight_min(axis=0, color='#FF6B6B'), 
                 use_container_width=True)

# Employee Performance Page
elif page == "🏆 Employee Performance":
    st.markdown('<div class="sub-header">Employee Performance</div>', unsafe_allow_html=True)
    
    # Performance filters
    col1, col2 = st.columns(2)
    with col1:
        min_perf = st.slider("⭐ Minimum Performance Score", 2.0, 5.0, 2.0, 0.1)
    with col2:
        perf_dept = st.selectbox("🏢 Department", ["All"] + df["Department"].unique().tolist())
    
    # Filter data
    perf_df = df[df["Performance Score"] >= min_perf]
    if perf_dept != "All":
        perf_df = perf_df[perf_df["Department"] == perf_dept]
    
    # Performance metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">🌟 High Performers (>4.0)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(perf_df[perf_df["Performance Score"] > 4.0])}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">📈 Avg Performance</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{perf_df["Performance Score"].mean():.2f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if not perf_df.empty:
            top_dept = perf_df.groupby("Department")["Performance Score"].mean().idxmax()
        else:
            top_dept = "N/A"
        st.markdown('<div class="metric-label">🏆 Top Department</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{top_dept}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance chart
    st.subheader("📊 Performance by Department")
    colors = ['#FF9AA2', '#FFB7B2', '#FFDAC1', '#E2F0CB', '#B5EAD7']
    fig = px.box(perf_df, x="Department", y="Performance Score", 
                color="Department", 
                color_discrete_sequence=colors)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top performers table
    st.subheader("🏅 Top Performers")
    top_performers = perf_df.nlargest(10, "Performance Score")
    st.dataframe(top_performers[["Name", "Department", "Position", "Performance Score", "Projects Completed"]].style
                 .background_gradient(cmap='RdYlGn', subset=["Performance Score"]), 
                use_container_width=True)

# Department Analytics Page
elif page == "🏢 Department Analytics":
    st.markdown('<div class="sub-header">Department Analytics</div>', unsafe_allow_html=True)
    
    # Department metrics
    dept_metrics = df.groupby("Department").agg({
        "Salary": "mean",
        "Performance Score": "mean",
        "Attendance Rate": "mean",
        "Employee ID": "count"
    }).round(2)
    
    dept_metrics.columns = ["Avg Salary", "Avg Performance", "Avg Attendance", "Employee Count"]
    dept_metrics = dept_metrics.reset_index()
    
    # Department comparison chart
    st.subheader("📊 Department Comparison")
    metric_choice = st.selectbox("🎯 Select Metric", 
                                ["Avg Salary", "Avg Performance", "Avg Attendance", "Employee Count"])
    
    colors = ['#6C5CE7', '#A29BFE', '#FD79A8', '#FDCB6E', '#6A89CC']
    fig = px.bar(dept_metrics, x="Department", y=metric_choice,
                color="Department",
                color_discrete_sequence=colors,
                text=metric_choice)
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed metrics table
    st.subheader("📋 Department Metrics")
    st.dataframe(dept_metrics.style.background_gradient(cmap='viridis'), 
                use_container_width=True)

# Attendance Tracker Page
elif page == "📅 Attendance Tracker":
    st.markdown('<div class="sub-header">Attendance Tracker</div>', unsafe_allow_html=True)
    
    # Tabs for different views
    att_tab1, att_tab2 = st.tabs(["📊 Overview", "📋 Detailed Records"])
    
    with att_tab1:
        st.subheader("📊 Attendance Overview")
        
        # Show overall metrics using session data if available
        if st.session_state.attendance_data:
            att_df = pd.DataFrame(st.session_state.attendance_data)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">📋 Total Records</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{len(att_df)}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">👥 Unique Employees</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{att_df["Employee Name"].nunique()}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">⏱️ Avg Daily Hours</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{att_df["Work Hours"].mean():.1f}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No attendance data recorded yet. Visit 'Mark Attendance' to add records.")
        
        # Department-wise attendance if data exists
        if st.session_state.attendance_data:
            st.subheader("🏢 Department-wise Attendance")
            att_df = pd.DataFrame(st.session_state.attendance_data)
            dept_avg = att_df.groupby("Department")["Work Hours"].mean().reset_index()
            colors = ['#6C5CE7', '#A29BFE', '#FD79A8', '#FDCB6E', '#6A89CC']
            fig = px.bar(dept_avg, x="Department", y="Work Hours",
                        color="Department", color_discrete_sequence=colors,
                        title="Average Work Hours by Department")
            st.plotly_chart(fig, use_container_width=True)
    
    with att_tab2:
        st.subheader("📋 Detailed Attendance Records")
        
        # Show attendance data table
        if st.session_state.attendance_data:
            att_df = pd.DataFrame(st.session_state.attendance_data)
            
            # Filters
            col1, col2 = st.columns(2)
            with col1:
                selected_dept = st.selectbox("🏢 Filter by Department", 
                                           ["All"] + att_df["Department"].unique().tolist())
            with col2:
                date_range = st.date_input("📅 Date Range", 
                                         [datetime.today() - timedelta(days=30), datetime.today()])
            
            # Apply filters
            filtered_att = att_df.copy()
            if selected_dept != "All":
                filtered_att = filtered_att[filtered_att["Department"] == selected_dept]
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_att["Date"] = pd.to_datetime(filtered_att["Date"])
                filtered_att = filtered_att[
                    (filtered_att["Date"] >= pd.Timestamp(start_date)) & 
                    (filtered_att["Date"] <= pd.Timestamp(end_date))
                ]
            
            # Display filtered data
            st.write(f"Showing {len(filtered_att)} records")
            st.dataframe(filtered_att, use_container_width=True)
            
            # Download button
            csv = filtered_att.to_csv(index=False)
            st.download_button(
                label="📥 Download Attendance Data",
                data=csv,
                file_name="attendance_records.csv",
                mime="text/csv"
            )
        else:
            st.info("No attendance data recorded yet. Visit 'Mark Attendance' to add records.")

# Mark Attendance Page (New Page)
elif page == "⏰ Mark Attendance":
    st.markdown('<div class="sub-header">Mark Attendance</div>', unsafe_allow_html=True)
    
    # Employee selection
    st.subheader("👤 Employee Information")
    employee_names = df["Name"].tolist()
    selected_employee = st.selectbox("Select Your Name", employee_names)
    
    # Get employee details
    employee_details = df[df["Name"] == selected_employee].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Employee ID", employee_details["Employee ID"])
    with col2:
        st.metric("Department", employee_details["Department"])
    with col3:
        st.metric("Position", employee_details["Position"])
    
    st.markdown("---")
    
    # Attendance marking section
    st.subheader("打卡时间 Punch In/Out")
    
    # Date selection
    selected_date = st.date_input("Select Date", datetime.today())
    
    # Entry and exit time
    col1, col2 = st.columns(2)
    with col1:
        entry_time = st.time_input("Entry Time", datetime.now().time())
    with col2:
        # Changed: Exit time should not be pre-filled
        exit_time = st.time_input("Exit Time")  # Removed default value
    
    # Additional attendance details
    st.subheader("📋 Additional Details")
    work_location = st.selectbox("Work Location", ["Office", "Remote", "Client Site", "Hybrid"])
    notes = st.text_area("Notes (Optional)", placeholder="Any additional information...")
    
    # Calculate work hours only if exit time is provided
    work_hours = 0
    if entry_time and exit_time:
        entry_datetime = datetime.combine(selected_date, entry_time)
        exit_datetime = datetime.combine(selected_date, exit_time)
        if exit_datetime > entry_datetime:
            work_duration = exit_datetime - entry_datetime
            work_hours = work_duration.total_seconds() / 3600
            st.info(f"📅 Work Duration: {work_hours:.2f} hours")
        else:
            st.warning("⚠️ Exit time must be after entry time")
            work_hours = 0
    
    # Save attendance button
    if st.button("💾 Save Attendance", type="primary", use_container_width=True):
        # Validation
        if not entry_time:
            st.error("Please enter your entry time")
        elif not exit_time:
            st.error("Please enter your exit time")
        elif work_hours <= 0:
            st.error("Exit time must be after entry time")
        else:
            # Create attendance record
            attendance_record = {
                "Date": selected_date.strftime("%Y-%m-%d"),
                "Employee ID": employee_details["Employee ID"],
                "Employee Name": selected_employee,
                "Department": employee_details["Department"],
                "Entry Time": entry_time.strftime("%H:%M:%S"),
                "Exit Time": exit_time.strftime("%H:%M:%S"),
                "Work Hours": round(work_hours, 2),
                "Location": work_location,
                "Notes": notes
            }
            
            # Add to session state
            st.session_state.attendance_data.append(attendance_record)
            
            # Show success message
            st.success("✅ Attendance marked successfully!")
            
            # Display the recorded attendance
            st.subheader("📋 Recorded Attendance")
            st.write(pd.DataFrame([attendance_record]))
    
    # Show recent attendance records
    if st.session_state.attendance_data:
        st.markdown("---")
        st.subheader("📊 Your Recent Attendance")
        recent_df = pd.DataFrame(st.session_state.attendance_data)
        employee_attendance = recent_df[recent_df["Employee Name"] == selected_employee]
        if not employee_attendance.empty:
            st.dataframe(employee_attendance.tail(10), use_container_width=True)
        else:
            st.info("No previous attendance records found for you.")
    
    # Monthly attendance summary
    if st.session_state.attendance_data:
        st.markdown("---")
        st.subheader("📅 Monthly Summary")
        recent_df = pd.DataFrame(st.session_state.attendance_data)
        employee_attendance = recent_df[recent_df["Employee Name"] == selected_employee]
        
        if not employee_attendance.empty:
            # Convert date column to datetime
            employee_attendance["Date"] = pd.to_datetime(employee_attendance["Date"])
            
            # Filter for current month
            current_month = datetime.now().month
            current_year = datetime.now().year
            monthly_data = employee_attendance[
                (employee_attendance["Date"].dt.month == current_month) & 
                (employee_attendance["Date"].dt.year == current_year)
            ]
            
            if not monthly_data.empty:
                total_days = len(monthly_data)
                total_hours = monthly_data["Work Hours"].sum()
                avg_hours = monthly_data["Work Hours"].mean()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">📅 Days Present</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{total_days}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">⏱️ Total Hours</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{total_hours:.1f}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">📊 Avg Hours/Day</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{avg_hours:.1f}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Attendance trend chart
                st.subheader("📈 Attendance Trend")
                fig = px.line(monthly_data, x="Date", y="Work Hours", markers=True,
                             title="Daily Work Hours Trend")
                fig.update_traces(line_color='#4ECDC4', marker=dict(color='#FF6B6B', size=8))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No attendance records found for the current month.")

# Leave Management Page (New Page)
elif page == "🌴 Leave Management":
    st.markdown('<div class="sub-header">Leave Management</div>', unsafe_allow_html=True)
    
    # Tabs for different leave functions
    leave_tab1, leave_tab2, leave_tab3 = st.tabs(["➕ Apply for Leave", "📋 My Requests", "📊 Leave Analytics"])
    
    with leave_tab1:
        st.subheader("📝 Apply for Leave")
        
        # Employee selection
        employee_names = df["Name"].tolist()
        selected_employee = st.selectbox("👤 Select Your Name", employee_names, key="leave_employee")
        
        # Get employee details
        employee_details = df[df["Name"] == selected_employee].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Employee ID", employee_details["Employee ID"])
        with col2:
            st.metric("Department", employee_details["Department"])
        with col3:
            st.metric("Position", employee_details["Position"])
        
        st.markdown("---")
        
        # Leave application form
        col1, col2 = st.columns(2)
        with col1:
            leave_type = st.selectbox("🏷️ Leave Type", 
                                    ["Annual Leave", "Sick Leave", "Personal Leave", "Maternity Leave", 
                                     "Paternity Leave", "Bereavement Leave", "Unpaid Leave"])
            start_date = st.date_input("📅 Start Date")
        with col2:
            end_date = st.date_input("📅 End Date")
            leave_reason = st.text_area("📝 Reason for Leave", 
                                      placeholder="Please provide a brief reason for your leave request...")
        
        # Calculate leave duration
        if start_date and end_date:
            leave_duration = (end_date - start_date).days + 1
            if leave_duration > 0:
                st.info(f"⏱️ Leave Duration: {leave_duration} day(s)")
            else:
                st.error("End date must be after start date")
        
        # Supporting documents upload (simulated)
        st.file_uploader("📎 Upload Supporting Documents (Optional)", 
                        type=["pdf", "jpg", "png"], 
                        accept_multiple_files=True)
        
        # Submit button
        if st.button("📤 Submit Leave Request", type="primary", use_container_width=True):
            if start_date and end_date and leave_duration > 0:
                # Create leave request record
                leave_record = {
                    "Request ID": f"LEAVE{len(st.session_state.leave_requests)+1:04d}",
                    "Employee ID": employee_details["Employee ID"],
                    "Employee Name": selected_employee,
                    "Department": employee_details["Department"],
                    "Leave Type": leave_type,
                    "Start Date": start_date.strftime("%Y-%m-%d"),
                    "End Date": end_date.strftime("%Y-%m-%d"),
                    "Duration": leave_duration,
                    "Reason": leave_reason,
                    "Status": "Pending",
                    "Applied Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Add to session state
                st.session_state.leave_requests.append(leave_record)
                
                # Show success message
                st.success("✅ Leave request submitted successfully! It will be reviewed by your manager.")
                
                # Display the submitted request
                st.subheader("📋 Submitted Request")
                st.write(pd.DataFrame([leave_record]))
            else:
                st.error("Please check your dates and try again.")
    
    with leave_tab2:
        st.subheader("📋 My Leave Requests")
        
        # Show employee's leave requests
        if st.session_state.leave_requests:
            leave_df = pd.DataFrame(st.session_state.leave_requests)
            
            # Filter by employee
            employee_names = df["Name"].tolist()
            selected_employee = st.selectbox("👤 Select Employee", employee_names, key="view_employee")
            employee_leave = leave_df[leave_df["Employee Name"] == selected_employee]
            
            if not employee_leave.empty:
                # Status filter
                status_filter = st.selectbox("🔍 Filter by Status", 
                                           ["All", "Pending", "Approved", "Rejected"])
                
                if status_filter != "All":
                    employee_leave = employee_leave[employee_leave["Status"] == status_filter]
                
                # Display leave requests
                st.write(f"Showing {len(employee_leave)} leave request(s)")
                
                # Style the dataframe based on status
                def highlight_status(s):
                    if s.Status == "Approved":
                        return ['background-color: #96CEB4']*len(s)
                    elif s.Status == "Rejected":
                        return ['background-color: #FF6B6B']*len(s)
                    else:
                        return ['background-color: #FFEAA7']*len(s)
                
                st.dataframe(employee_leave.style.apply(highlight_status, axis=1), 
                           use_container_width=True)
            else:
                st.info("No leave requests found for this employee.")
        else:
            st.info("No leave requests have been submitted yet.")
    
    with leave_tab3:
        st.subheader("📊 Leave Analytics")
        
        # Show leave statistics
        if st.session_state.leave_requests:
            leave_df = pd.DataFrame(st.session_state.leave_requests)
            
            # Overall metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">📋 Total Requests</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{len(leave_df)}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">✅ Approved</div>', unsafe_allow_html=True)
                approved_count = len(leave_df[leave_df["Status"] == "Approved"])
                st.markdown(f'<div class="metric-value">{approved_count}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">⏳ Pending</div>', unsafe_allow_html=True)
                pending_count = len(leave_df[leave_df["Status"] == "Pending"])
                st.markdown(f'<div class="metric-value">{pending_count}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">📅 Total Leave Days</div>', unsafe_allow_html=True)
                total_days = leave_df["Duration"].sum()
                st.markdown(f'<div class="metric-value">{total_days}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Leave type distribution
            st.subheader("🏷️ Leave Type Distribution")
            leave_type_counts = leave_df["Leave Type"].value_counts()
            colors = ['#FF9AA2', '#FFB7B2', '#FFDAC1', '#E2F0CB', '#B5EAD7', '#C7CEEA']
            fig1 = px.pie(values=leave_type_counts.values, names=leave_type_counts.index,
                         color_discrete_sequence=colors, title="Distribution of Leave Types")
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)
            
            # Department-wise leave requests
            st.subheader("🏢 Department-wise Leave Requests")
            dept_leave_counts = leave_df["Department"].value_counts()
            fig2 = px.bar(x=dept_leave_counts.index, y=dept_leave_counts.values,
                         labels={'x': 'Department', 'y': 'Number of Requests'},
                         color=dept_leave_counts.index,
                         color_discrete_sequence=colors,
                         title="Leave Requests by Department")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No leave data available yet. Submit a leave request to see analytics.")

# Project Management Page
elif page == "🚀 Project Management":
    st.markdown('<div class="sub-header">Project Management</div>', unsafe_allow_html=True)
    
    # Generate sample project data
    @st.cache_data
    def generate_project_data():
        projects = []
        statuses = ["Not Started", "In Progress", "Completed", "On Hold"]
        status_colors = {"Not Started": "#FF9AA2", "In Progress": "#FFB7B2", 
                        "Completed": "#96CEB4", "On Hold": "#FFEAA7"}
        for i in range(30):
            project = {
                "Project ID": f"PROJ{i+1:03d}",
                "Project Name": f"Project {i+1}",
                "Department": random.choice(df["Department"].unique()),
                "Manager": random.choice(df["Name"].tolist()),
                "Status": random.choice(statuses),
                "Status Color": status_colors[random.choice(statuses)],
                "Start Date": (datetime.today() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
                "End Date": (datetime.today() + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
                "Budget": random.randint(10000, 100000),
                "Progress": random.randint(0, 100)
            }
            projects.append(project)
        return pd.DataFrame(projects)
    
    project_df = generate_project_data()
    
    # Project filters
    col1, col2 = st.columns(2)
    with col1:
        proj_status = st.selectbox("🎯 Filter by Status", ["All"] + project_df["Status"].unique().tolist())
    with col2:
        proj_dept = st.selectbox("🏢 Filter by Department", ["All"] + project_df["Department"].unique().tolist())
    
    # Apply filters
    filtered_projects = project_df.copy()
    if proj_status != "All":
        filtered_projects = filtered_projects[filtered_projects["Status"] == proj_status]
    if proj_dept != "All":
        filtered_projects = filtered_projects[filtered_projects["Department"] == proj_dept]
    
    # Project metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">🚀 Total Projects</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(project_df)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">🔄 In Progress</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(project_df[project_df["Status"] == "In Progress"])}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">✅ Completed</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(project_df[project_df["Status"] == "Completed"])}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">📈 Avg Progress</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{project_df["Progress"].mean():.1f}%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Project status chart
    st.subheader("📊 Project Status Distribution")
    status_counts = project_df["Status"].value_counts()
    colors = ['#FF9AA2', '#FFB7B2', '#96CEB4', '#FFEAA7']
    fig = px.pie(values=status_counts.values, names=status_counts.index,
                color_discrete_sequence=colors)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
    
    # Project progress by department
    st.subheader("🏢 Project Progress by Department")
    colors = ['#6C5CE7', '#A29BFE', '#FD79A8', '#FDCB6E', '#6A89CC']
    progress_fig = px.box(filtered_projects, x="Department", y="Progress",
                         color="Department",
                         color_discrete_sequence=colors)
    st.plotly_chart(progress_fig, use_container_width=True)
    
    # Projects table
    st.subheader("📋 Project Details")
    st.dataframe(filtered_projects.style.background_gradient(cmap='Blues', subset=["Progress"]), 
                use_container_width=True)

# Resource Allocation Page
elif page == "📦 Resource Allocation":
    st.markdown('<div class="sub-header">Resource Allocation</div>', unsafe_allow_html=True)
    
    # Generate sample resource data
    @st.cache_data
    def generate_resource_data():
        resources = []
        resource_types = ["Software License", "Hardware", "Cloud Services", "Training", "Consulting"]
        type_colors = {"Software License": "#FF9AA2", "Hardware": "#FFB7B2", 
                      "Cloud Services": "#96CEB4", "Training": "#FFEAA7", "Consulting": "#B5EAD7"}
        for i in range(50):
            resource = {
                "Resource ID": f"RES{i+1:03d}",
                "Resource Name": f"{random.choice(resource_types)} {i+1}",
                "Type": random.choice(resource_types),
                "Department": random.choice(df["Department"].unique()),
                "Assigned To": random.choice(df["Name"].tolist()),
                "Status": random.choice(["Available", "In Use", "Maintenance", "Retired"]),
                "Status Color": type_colors[random.choice(resource_types)],
                "Cost": random.randint(100, 5000),
                "Acquisition Date": (datetime.today() - timedelta(days=random.randint(0, 730))).strftime("%Y-%m-%d")
            }
            resources.append(resource)
        return pd.DataFrame(resources)
    
    resource_df = generate_resource_data()
    
    # Resource filters
    col1, col2 = st.columns(2)
    with col1:
        res_type = st.selectbox("🎯 Filter by Type", ["All"] + resource_df["Type"].unique().tolist())
    with col2:
        res_status = st.selectbox("🔧 Filter by Status", ["All"] + resource_df["Status"].unique().tolist())
    
    # Apply filters
    filtered_resources = resource_df.copy()
    if res_type != "All":
        filtered_resources = filtered_resources[filtered_resources["Type"] == res_type]
    if res_status != "All":
        filtered_resources = filtered_resources[filtered_resources["Status"] == res_status]
    
    # Resource metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">📦 Total Resources</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(resource_df)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">🔧 In Use</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(resource_df[resource_df["Status"] == "In Use"])}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">✅ Available</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{len(resource_df[resource_df["Status"] == "Available"])}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">💰 Total Value</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">${resource_df["Cost"].sum():,}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Resource allocation by department
    st.subheader("🏢 Resource Allocation by Department")
    dept_resource_counts = filtered_resources["Department"].value_counts()
    colors = ['#FF9AA2', '#FFB7B2', '#FFDAC1', '#E2F0CB', '#B5EAD7']
    fig1 = px.bar(x=dept_resource_counts.index, y=dept_resource_counts.values,
                 labels={'x': 'Department', 'y': 'Resource Count'},
                 color=dept_resource_counts.index,
                 color_discrete_sequence=colors)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Resource types distribution
    st.subheader("🎯 Resource Types Distribution")
    type_counts = filtered_resources["Type"].value_counts()
    colors = ['#6C5CE7', '#A29BFE', '#FD79A8', '#FDCB6E', '#6A89CC']
    fig2 = px.pie(values=type_counts.values, names=type_counts.index,
                 color_discrete_sequence=colors)
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig2, use_container_width=True)
    
    # Resources table
    st.subheader("📋 Resource Details")
    st.dataframe(filtered_resources.style.background_gradient(cmap='Greens', subset=["Cost"]), 
                use_container_width=True)

# Interactive Tools Page
elif page == "🎮 Interactive Tools":
    st.markdown('<div class="sub-header">Interactive Tools</div>', unsafe_allow_html=True)
    
    # Tabs for different tools
    tab1, tab2, tab3 = st.tabs(["📊 Data Explorer", "🔮 Prediction Tool", "🎨 Custom Visualization"])
    
    with tab1:
        st.subheader("📊 Data Explorer")
        st.write("Explore your employee data with interactive filters")
        
        # Interactive filters
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_dept = st.multiselect("🏢 Departments", df["Department"].unique())
        with col2:
            selected_positions = st.multiselect("💼 Positions", df["Position"].unique())
        with col3:
            salary_range = st.slider("💰 Salary Range", 
                                   int(df["Salary"].min()), 
                                   int(df["Salary"].max()), 
                                   (int(df["Salary"].min()), int(df["Salary"].max())))
        
        # Apply filters
        filtered_df = df.copy()
        if selected_dept:
            filtered_df = filtered_df[filtered_df["Department"].isin(selected_dept)]
        if selected_positions:
            filtered_df = filtered_df[filtered_df["Position"].isin(selected_positions)]
        filtered_df = filtered_df[(filtered_df["Salary"] >= salary_range[0]) & 
                                 (filtered_df["Salary"] <= salary_range[1])]
        
        # Display filtered data
        st.write(f"Showing {len(filtered_df)} employees")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv,
            file_name="filtered_employees.csv",
            mime="text/csv"
        )
    
    with tab2:
        st.subheader("🔮 Performance Prediction Tool")
        st.write("Predict employee performance based on various factors")
        
        # Simple prediction form
        col1, col2 = st.columns(2)
        with col1:
            years_exp = st.slider("Years at Company", 0, 20, 5)
            projects_completed = st.slider("Projects Completed", 0, 30, 10)
        with col2:
            attendance_rate = st.slider("Attendance Rate (%)", 0, 100, 90)
            satisfaction = st.slider("Satisfaction Score", 1.0, 10.0, 7.0)
        
        # Simple prediction algorithm
        performance_score = (
            (years_exp * 0.1) + 
            (projects_completed * 0.15) + 
            (attendance_rate * 0.02) + 
            (satisfaction * 0.2)
        ) / 4
        
        # Ensure score is within bounds
        performance_score = min(5.0, max(2.0, performance_score))
        
        # Display prediction
        st.metric("Predicted Performance Score", f"{performance_score:.2f}/5.0")
        
        # Visualization
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=performance_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Performance Prediction"},
            gauge={
                'axis': {'range': [None, 5]},
                'bar': {'color': "#4ECDC4"},
                'steps': [
                    {'range': [0, 2], 'color': "#FF6B6B"},
                    {'range': [2, 3], 'color': "#FFEAA7"},
                    {'range': [3, 5], 'color': "#96CEB4"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': performance_score}}))
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("🎨 Custom Visualization")
        st.write("Create your own visualizations")
        
        # Visualization options
        viz_type = st.selectbox("Chart Type", ["Scatter Plot", "Bar Chart", "Histogram"])
        x_axis = st.selectbox("X-Axis", df.columns[3:])  # Skip ID, Name, Department
        if viz_type != "Histogram":
            y_axis = st.selectbox("Y-Axis", df.columns[3:])
        
        # Create visualization
        if viz_type == "Scatter Plot":
            fig = px.scatter(df, x=x_axis, y=y_axis, color="Department",
                           size="Performance Score" if x_axis != "Performance Score" and y_axis != "Performance Score" else None,
                           hover_data=["Name"])
            st.plotly_chart(fig, use_container_width=True)
        elif viz_type == "Bar Chart":
            grouped_df = df.groupby("Department").agg({x_axis: "mean", y_axis: "mean"}).reset_index()
            fig = px.bar(grouped_df, x="Department", y=[x_axis, y_axis], barmode="group")
            st.plotly_chart(fig, use_container_width=True)
        elif viz_type == "Histogram":
            fig = px.histogram(df, x=x_axis, color="Department", marginal="box")
            st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown('<div class="footer">Srashtikasoftware Employee Dashboard | © 2025 All Rights Reserved</div>', unsafe_allow_html=True)
