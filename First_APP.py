# Imports
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
#from sklearn.preprocessing import StandardScaler, MinMaxScaler
import io

# 1. Title and Subheader
st.title("Smart Data Explorer")
st.subheader("Unlock Insights, Clean Your Data, and Visualize Trends with Ease!")

# 2. Upload Dataset from various formats
upload = st.file_uploader("Upload your file", type=["csv", "xlsx", "json"])

if upload is not None:
    file_type = upload.name.split('.')[-1]
    
    # 3. Load dataset based on file type
    if file_type == 'csv':
        data = pd.read_csv(upload)
    elif file_type == 'xlsx':
        sheet = st.selectbox("Select the sheet name", pd.ExcelFile(upload).sheet_names)
        data = pd.read_excel(upload, sheet_name=sheet)
    elif file_type == 'json':
        data = pd.read_json(upload)
    
    # 4. Show Dataset structure
    if st.checkbox("Preview Dataset"):
        preview_option = st.radio("Choose view", ("Head", "Tail"))
        if preview_option == "Head":
            st.write(data.head())
        else:
            st.write(data.tail())
        
        # New Feature: Deleting unnecessary columns
        if st.checkbox("Do you want to delete any columns?"):
            # Display available columns for user to delete
            col_to_delete = st.multiselect("Select the column(s) you want to delete", data.columns)
            if st.button("Delete Selected Columns"):
                data = data.drop(columns=col_to_delete)
                st.write(f"Deleted columns: {col_to_delete}")
                st.write(data.head())  # Show updated dataset after deletion

    # 5. View dataset info
    if st.checkbox("View Dataset Info"):
        buffer = io.StringIO()
        data.info(buf=buffer)
        s = buffer.getvalue()
        st.text(s)

    # 6. Check for Missing Values
    if data.isnull().values.any():
        if st.checkbox("Display missing values in each column"):
            st.write(data.isnull().sum())
            
        if st.checkbox("Visualize Missing Values (Heatmap)"):
            fig, ax = plt.subplots()
            sns.heatmap(data.isnull(), cbar=False, ax=ax)
            st.pyplot(fig)
        
        # Handle Missing Values
        handle_na = st.selectbox("How do you want to handle missing values?", 
                                 ("Do nothing", "Drop missing values", "Fill with mean", "Fill with mode", "Fill with median"))

        if handle_na == "Drop missing values":
            data = data.dropna()
            st.write("Missing values dropped.")
    
        elif handle_na == "Fill with mean":
            # Fill only numeric columns with mean
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].mean())
            st.write("Missing values in numeric columns filled with mean.")
    
        elif handle_na == "Fill with mode":
            data = data.fillna(data.mode().iloc[0])  # Mode works for both numeric and categorical
            st.write("Missing values filled with mode.")
    
        elif handle_na == "Fill with median":
            # Fill only numeric columns with median
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].median())
            st.write("Missing values in numeric columns filled with median.")

    # 7. Remove Duplicate Values
    if data.duplicated().any():
        if st.checkbox(f"Remove {data.duplicated().sum()} duplicate rows"):
            data = data.drop_duplicates()
            st.write("Duplicate rows removed.")
    else:
        st.write("No duplicate rows found.")

    # 8. Convert Data Types if Necessary
    if st.checkbox("Convert Data Types (If need for any column)"):
        col_to_convert = st.selectbox("Select column to convert", data.columns)
    
        # Determine the target type
        convert_to = st.radio("Convert to", ("Integer", "Float", "String", "Date", "Year", "Month"))
    
        current_dtype = data[col_to_convert].dtype
    
        # Integer conversion
        if convert_to == "Integer":
            if pd.api.types.is_integer_dtype(current_dtype):
                st.info(f"Column {col_to_convert} is already an Integer.")
            elif pd.api.types.is_float_dtype(current_dtype):
                try:
                    # Only convert if the column has no decimal values
                    if (data[col_to_convert] % 1 == 0).all():
                        data[col_to_convert] = data[col_to_convert].astype(int)
                        st.success(f"Column {col_to_convert} successfully converted to Integer.")
                    else:
                        st.error(f"Column {col_to_convert} contains non-integer float values. Conversion to Integer failed.")
                except ValueError:
                    st.error(f"Conversion to Integer failed for {col_to_convert}.")
            else:
                try:
                    data[col_to_convert] = pd.to_numeric(data[col_to_convert], errors='raise', downcast='integer')
                    st.success(f"Column {col_to_convert} successfully converted to Integer.")
                except ValueError:
                    st.error(f"Column {col_to_convert} contains non-numeric values. Conversion to Integer failed.")
    
        # Float conversion
        elif convert_to == "Float":
            if pd.api.types.is_float_dtype(current_dtype):
                st.info(f"Column {col_to_convert} is already a Float.")
            else:
                try:
                    data[col_to_convert] = pd.to_numeric(data[col_to_convert], errors='raise')
                    st.success(f"Column {col_to_convert} successfully converted to Float.")
                except ValueError:
                    st.error(f"Column {col_to_convert} contains non-numeric values. Conversion to Float failed.")
    
        # String conversion
        elif convert_to == "String":
            if pd.api.types.is_string_dtype(current_dtype):
                st.info(f"Column {col_to_convert} is already a String.")
            else:
                data[col_to_convert] = data[col_to_convert].astype(str)
                st.success(f"Column {col_to_convert} successfully converted to String.")
        
        # Date conversion
        elif convert_to == "Date":
            if pd.api.types.is_datetime64_any_dtype(current_dtype):
                st.info(f"Column {col_to_convert} is already a Date.")
            else:
                try:
                    data[col_to_convert] = pd.to_datetime(data[col_to_convert], errors='coerce')
                    if data[col_to_convert].isnull().any():
                        st.warning(f"Some values in {col_to_convert} could not be converted to Date.")
                    else:
                        st.success(f"Column {col_to_convert} successfully converted to Date.")
                except Exception as e:
                    st.error(f"Error in converting column {col_to_convert} to Date: {e}")
    
        # Year conversion
        elif convert_to == "Year":
            if pd.api.types.is_integer_dtype(current_dtype) and (data[col_to_convert].between(1000, 3000)).all():
                st.info(f"Column {col_to_convert} is already a Year.")
            else:
                try:
                    data[col_to_convert] = pd.to_datetime(data[col_to_convert], errors='coerce').dt.year
                    st.success(f"Column {col_to_convert} successfully converted to Year.")
                except Exception as e:
                    st.error(f"Error in converting column {col_to_convert} to Year: {e}")
    
        # Month conversion
        elif convert_to == "Month":
            if pd.api.types.is_integer_dtype(current_dtype) and (data[col_to_convert].between(1, 12)).all():
                st.info(f"Column {col_to_convert} is already a Month.")
            else:
                try:
                    data[col_to_convert] = pd.to_datetime(data[col_to_convert], errors='coerce').dt.month
                    st.success(f"Column {col_to_convert} successfully converted to Month.")
                except Exception as e:
                    st.error(f"Error in converting column {col_to_convert} to Month: {e}")

    # 9. Summary Statistics
    if st.checkbox("Summary Statistics"):
        st.write(data.describe(include='all'))

    # 10. Analyze Categorical Variables
    if st.checkbox("Analyze Categorical Variables"):
        # Get categorical columns
        categorical_columns = data.select_dtypes(include='object').columns
    
        if len(categorical_columns) > 0:
            cat_column = st.selectbox("Select column for analysis", categorical_columns)
            st.write(data[cat_column].value_counts())
        else:
            st.warning("No categorical columns available for analysis.")

    # 11. Visualize Data Distributions
    if st.checkbox("Visualize Data Distributions"):
        column = st.selectbox("Select column to visualize", data.select_dtypes(include=np.number).columns)
        plot_type = st.radio("Choose plot type", ("Histogram", "Boxplot"))
        
        if plot_type == "Histogram":
            fig, ax = plt.subplots()
            sns.histplot(data[column], kde=True, ax=ax)
            st.pyplot(fig)
        else:
            fig, ax = plt.subplots()
            sns.boxplot(data[column], ax=ax)
            st.pyplot(fig)

    # 12. Analyze Relationships
    if st.checkbox("Analyze Relationships"):
        analysis_type = st.radio("Choose analysis type", ("Correlation Matrix", "Scatter Plot"))

        if analysis_type == "Correlation Matrix":
            # Filter only numeric columns for correlation calculation
            numeric_data = data.select_dtypes(include=[np.number])

            if numeric_data.empty:
                st.warning("No numeric columns available for correlation matrix.")
            else:
                fig, ax = plt.subplots(figsize=(10, 8))  # Adjust figure size as needed
                sns.heatmap(numeric_data.corr(), annot=True, cmap="coolwarm", ax=ax, 
                            annot_kws={"size": 10}, fmt=".2f")  # Adjust annotation font size
                st.pyplot(fig)

        elif analysis_type == "Scatter Plot":
            x_axis = st.selectbox("Select X-axis", data.columns)
            y_axis = st.selectbox("Select Y-axis", data.columns)
            fig, ax = plt.subplots()
            sns.scatterplot(x=data[x_axis], y=data[y_axis], ax=ax)
            st.pyplot(fig)

    # 13. Group and Aggregate Data
    if st.checkbox("Group and Aggregate Data"):
        group_by_column = st.selectbox("Select column to group by", data.columns)
    
    # Filter numeric columns for aggregations like mean, sum, etc.
        numeric_columns = data.select_dtypes(include=np.number).columns
        if not numeric_columns.any():
            st.warning("No numeric columns available for aggregation.")
        else:
            agg_column = st.selectbox("Select column to aggregate", numeric_columns)
            agg_function = st.selectbox("Select aggregation function", ["sum", "mean", "max", "min", "count"])
        
        # Apply the aggregation function
            try:
                grouped_data = data.groupby(group_by_column)[agg_column].agg(agg_function)
                st.write(grouped_data)
            except TypeError as e:
                st.error(f"Aggregation function failed: {str(e)}")

    # 14. Identify Outliers
    if st.checkbox("Identify Outliers (Boxplot)"):
        outlier_column = st.selectbox("Select column to visualize outliers", data.columns)
        fig, ax = plt.subplots()
        sns.boxplot(data[outlier_column], ax=ax)
        st.pyplot(fig)

    # 15. Normalize or Scale Data
    #if st.checkbox("Normalize or Scale Data"):
     #   scale_option = st.radio("Choose scaling method", ("StandardScaler", "MinMaxScaler"))
      #  scale_columns = st.multiselect("Select columns to scale", data.select_dtypes(include=np.number).columns)
        
       # if scale_option == "StandardScaler":
        #    scaler = StandardScaler()
        #else:
         #   scaler = MinMaxScaler()

        #data[scale_columns] = scaler.fit_transform(data[scale_columns])
        #st.write(f"Columns {scale_columns} scaled using {scale_option}")

    # 16. Analyze Trends Over Time
    if st.checkbox("Analyze Trends Over Time"):
        time_column = st.selectbox("Select time column", data.columns)
        trend_column = st.selectbox("Select column to analyze trends", data.select_dtypes(include=np.number).columns)
        fig, ax = plt.subplots()
        data.groupby(time_column)[trend_column].mean().plot(ax=ax)
        st.pyplot(fig)

    # 17. Export Cleaned Data
    if st.checkbox("Export Cleaned Data"):
        buffer = io.BytesIO()
        data.to_csv(buffer, index=False)
        buffer.seek(0)
        st.download_button("Download CSV", data=buffer, file_name="cleaned_data.csv")
    
# 18. Add Author Info and Links
st.write("### Developed by Nafiul Araf 🎉")
st.write("[Linkedin](https://www.linkedin.com/in/nafiul-araf-50b0b7203/)")
st.write("[GitHub](https://github.com/nafiul-araf)")
