import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

def index(request):
    text = None
    summary = None  
    
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        file_path = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(file_path)

        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(fs.path(file_path))
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(fs.path(file_path))
        else:
            text = "Unsupported file format."
            return render(request, 'core/index.html', {'text': text})
        
        df.rename(columns={'Cust State': 'Cust_State'}, inplace=True)

        total_entries = len(df)
        avg_dpd = df['DPD'].mean()
        max_dpd = df['DPD'].max()
        min_dpd = df['DPD'].min()
        state_summary_df = df.groupby('Cust_State').agg({
            'ACCNO': 'count',
            'DPD': 'mean',   
        }).reset_index()

        states = state_summary_df['Cust_State'].tolist()
        dpd_values = state_summary_df['DPD'].tolist()
        customer_counts = state_summary_df['ACCNO'].tolist()

        summary = {
            'total_entries': total_entries,
            'avg_dpd': avg_dpd,
            'max_dpd': max_dpd,
            'min_dpd': min_dpd,
            'state_summary': state_summary_df.to_dict(orient='records'),
            'states': states,  
            'dpd_values': dpd_values, 
            'customer_counts': customer_counts 
        }

    return render(request, 'core/index.html', {'text': text, 'summary': summary})
