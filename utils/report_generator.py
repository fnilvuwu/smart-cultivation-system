import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64

def create_quality_graphs(latest_water_quality):
    """Create water quality graphs using plotly"""
    # Create gauge charts
    fig_gauges = make_subplots(
        rows=1, cols=3,
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]]
    )

    fig_gauges.add_trace(
        go.Indicator(
            mode="gauge+number",
            title={'text': "Latest pH"},
            value=latest_water_quality.get('pH', 7.0),
            gauge={'axis': {'range': [0, 14]}},
        ), row=1, col=1
    )

    fig_gauges.add_trace(
        go.Indicator(
            mode="gauge+number",
            title={'text': "Latest Turbidity"},
            value=latest_water_quality.get('turbidity', 0),
            gauge={'axis': {'range': [0, 100]}},
        ), row=1, col=2
    )

    fig_gauges.add_trace(
        go.Indicator(
            mode="gauge+number",
            title={'text': "Latest Temperature"},
            value=latest_water_quality.get('temperature', 25),
            gauge={'axis': {'range': [0, 40]}},
        ), row=1, col=3
    )

    return fig_gauges

def create_history_graph(water_qualities):
    """Create historical water quality graph"""
    dates = [wq.date for wq in water_qualities]
    ph_values = [wq.pH for wq in water_qualities]
    turbidity_values = [wq.turbidity for wq in water_qualities]
    temperature_values = [wq.temperature for wq in water_qualities]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=ph_values, name='pH'))
    fig.add_trace(go.Scatter(x=dates, y=turbidity_values, name='Turbidity'))
    fig.add_trace(go.Scatter(x=dates, y=temperature_values, name='Temperature'))

    fig.update_layout(
        title='Historical Water Quality',
        xaxis_title='Date',
        yaxis_title='Value'
    )

    return fig

def generate_excel_report(pond_data, water_qualities, fish_data, metrics, latest_water_quality):
    """Generate Excel report with multiple sheets and graphs"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book

        # Create Current Water Quality Indicators sheet
        gauge_worksheet = workbook.add_worksheet('Current Indicators')
        gauge_fig = create_quality_graphs(latest_water_quality)
        gauge_img = BytesIO()
        gauge_fig.write_image(gauge_img, format='png')
        gauge_worksheet.insert_image('A1', 'gauges.png', {'image_data': gauge_img})

        # Create Historical Water Quality sheet
        history_worksheet = workbook.add_worksheet('Historical Data')
        history_fig = create_history_graph(water_qualities)
        history_img = BytesIO()
        history_fig.write_image(history_img, format='png')
        history_worksheet.insert_image('A1', 'history.png', {'image_data': history_img})

        # Pond Information
        pond_df = pd.DataFrame({
            'Pond ID': [pond_data.pond_id],
            'Name': [pond_data.pond_name],
            'Location': [pond_data.location],
            'Creation Date': [pond_data.creation_date]
        })
        pond_df.to_excel(writer, sheet_name='Pond Information', index=False)

        # Water Quality Data
        if water_qualities:
            wq_df = pd.DataFrame([{
                'Date': wq.date,
                'pH': wq.pH,
                'Turbidity': wq.turbidity,
                'Temperature': wq.temperature,
                'Nitrate': wq.nitrate,
                'Ammonia': wq.ammonia,
                'Dissolved Oxygen': wq.dissolved_oxygen,
                'Quality Grade': wq.quality_grade,
                'Recorded By': wq.recorded_by_employee.employee_name
            } for wq in water_qualities])
            wq_df.to_excel(writer, sheet_name='Water Quality', index=False)

        # Fish Data
        if fish_data:
            fish_df = pd.DataFrame([{
                'Date': fd.date,
                'Weight (g)': fd.fish_weight,
                'Height (cm)': fd.fish_height,
                'Population': fd.fish_population,
                'Recorded By': fd.recorded_by_employee.employee_name
            } for fd in fish_data])
            fish_df.to_excel(writer, sheet_name='Fish Data', index=False)

        # Metrics
        if metrics:
            metrics_df = pd.DataFrame([{
                'Date': m.date,
                'Total Weight': m.total_fish_weight,
                'Average Weight': m.average_fish_weight,
                'Average Height': m.average_fish_height,
                'Total Population': m.total_population
            } for m in metrics])
            metrics_df.to_excel(writer, sheet_name='Metrics', index=False)

    output.seek(0)
    return output

def generate_pdf_report(pond_data, water_qualities, fish_data, metrics, latest_water_quality):
    """Generate PDF report with graphs"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()

    # Title page with pond information
    elements.append(Paragraph(f"Pond Report - {pond_data.pond_name}", styles['Heading1']))
    elements.append(Spacer(1, 20))
    
    # Pond Information
    elements.append(Paragraph("Pond Information", styles['Heading2']))
    pond_info = [['Pond ID', 'Name', 'Location', 'Creation Date'],
                 [pond_data.pond_id, pond_data.pond_name, pond_data.location, 
                  pond_data.creation_date.strftime('%Y-%m-%d')]]
    t = Table(pond_info)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    elements.append(PageBreak())

    # Current Water Quality Indicators page
    elements.append(Paragraph("Current Water Quality Indicators", styles['Heading1']))
    gauge_fig = create_quality_graphs(latest_water_quality)
    gauge_img = BytesIO()
    gauge_fig.write_image(gauge_img, format='png')
    gauge_img.seek(0)
    elements.append(Image(gauge_img, width=500, height=200))
    elements.append(PageBreak())

    # Historical Water Quality page
    elements.append(Paragraph("Historical Water Quality", styles['Heading1']))
    history_fig = create_history_graph(water_qualities)
    history_img = BytesIO()
    history_fig.write_image(history_img, format='png')
    history_img.seek(0)
    elements.append(Image(history_img, width=500, height=300))
    elements.append(PageBreak())

    # Water Quality Data
    if water_qualities:
        elements.append(Paragraph("Water Quality Data", styles['Heading2']))
        wq_data = [['Date', 'pH', 'Turbidity', 'Temperature', 'Nitrate', 'Ammonia', 'Dissolved Oxygen', 'Quality Grade', 'Recorded By']]
        for wq in water_qualities:
            wq_data.append([
                wq.date.strftime('%Y-%m-%d'),
                f"{wq.pH:.2f}",
                f"{wq.turbidity:.2f}",
                f"{wq.temperature:.2f}",
                f"{wq.nitrate:.2f}",
                f"{wq.ammonia:.2f}",
                f"{wq.dissolved_oxygen:.2f}",
                wq.quality_grade,
                wq.recorded_by_employee.employee_name
            ])
        t = Table(wq_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(PageBreak())

    # Fish Data
    if fish_data:
        elements.append(Paragraph("Fish Data", styles['Heading2']))
        fish_table_data = [['Date', 'Weight (g)', 'Height (cm)', 'Population', 'Recorded By']]
        for fd in fish_data:
            fish_table_data.append([
                fd.date.strftime('%Y-%m-%d'),
                f"{fd.fish_weight:.2f}",
                f"{fd.fish_height:.2f}",
                str(fd.fish_population),
                fd.recorded_by_employee.employee_name
            ])
        t = Table(fish_table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(PageBreak())

    # Metrics Data
    if metrics:
        elements.append(Paragraph("Pond Metrics", styles['Heading2']))
        metrics_table_data = [['Date', 'Total Weight', 'Average Weight', 'Average Height', 'Total Population']]
        for m in metrics:
            metrics_table_data.append([
                m.date.strftime('%Y-%m-%d'),
                f"{m.total_fish_weight:.2f}",
                f"{m.average_fish_weight:.2f}",
                f"{m.average_fish_height:.2f}",
                str(m.total_population)
            ])
        t = Table(metrics_table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    return buffer