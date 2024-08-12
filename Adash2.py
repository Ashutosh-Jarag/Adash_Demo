import pandas as pd
import plotly.express as px
from jinja2 import Template

class Adash:
    def __init__(self):
        self.data = None
        self.layout_config = None
        self.plots_html = []
        self.tables_html = []
        self.texts_html = []
    
    def input_file(self, data, file_type='df'):
        if file_type == 'df':
            self.data = data
        elif file_type == 'csv':
            self.data = pd.read_csv(data)
        elif file_type == 'html':
            self.data = pd.read_html(data)[0]
        else:
            raise ValueError("Unsupported file type. Please use 'df', 'csv', or 'html'.")
    
    def set_layout(self, layout_array):
        self.layout_config = {
            'rows': [{'columns': [{'type': 'plot', 'index': i} for i in range(col)]} for row, col in enumerate(layout_array)]
        }
    
    def adash_plot(self, fig=None, plot_type='line', title=None, position='center'):
        if self.data is None and fig is None:
            raise ValueError("No data or figure provided. Please input data or pass a Plotly figure.")
        
        if fig is not None:
            # Use provided fig object
            plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
            self.plots_html.append({'html': plot_html, 'title': title, 'position': position})
        else:
            # Generate plot based on plot_type
            for i, row_config in enumerate(self.layout_config['rows']):
                for col_config in row_config['columns']:
                    if plot_type == 'line':
                        fig = px.line(self.data, x=self.data.columns[0], y=self.data.columns[1])
                    elif plot_type == 'bar':
                        fig = px.bar(self.data, x=self.data.columns[0], y=self.data.columns[1])
                    elif plot_type == 'scatter':
                        fig = px.scatter(self.data, x=self.data.columns[0], y=self.data.columns[1])
                    elif plot_type == 'histogram':
                        fig = px.histogram(self.data, x=self.data.columns[0], y=self.data.columns[1])
                    else:
                        raise ValueError("Unsupported plot type. Please use 'line', 'bar', 'scatter', or 'histogram'.")

                    # Add user-defined title if provided
                    if title is not None:
                        fig.update_layout(title_text=title)
                    
                    plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
                    self.plots_html.append({'html': plot_html, 'title': title, 'position': position})
    
    def adash_table(self, data=None):
        if data is not None:
            if isinstance(data, pd.DataFrame):
                self.tables_html.append(data.to_html(classes='display', index=False))
            elif isinstance(data, str):
                if data.endswith('.csv'):
                    df = pd.read_csv(data)
                    self.tables_html.append(df.to_html(classes='display', index=False))
                elif data.endswith('.html'):
                    df = pd.read_html(data)[0]
                    self.tables_html.append(df.to_html(classes='display', index=False))
                else:
                    raise ValueError("Unsupported file format. Please use a DataFrame, CSV, or HTML file.")
        else:
            if self.data is not None:
                table_html = self.data.to_html(classes='display', index=False)
                self.tables_html.append(table_html)
            else:
                raise ValueError("No data available. Please input data first.")

    def adash_text(self, heading=None, textlines=None, ordered_list=None, unordered_list=None, position='center'):
        position_class = self._get_text_position_class(position)
        text_html = ''
        
        if heading:
            text_html += f"<h2 class='text-2xl font-bold {position_class}'>{heading}</h2>"
        
        if textlines:
            for line in textlines:
                text_html += f"<p class='mt-2 {position_class}'>{line}</p>"
        
        if ordered_list:
            text_html += "<ol class='mt-2 list-decimal list-inside {position_class}'>"
            for item in ordered_list:
                text_html += f"<li>{item}</li>"
            text_html += "</ol>"
        
        if unordered_list:
            text_html += "<ul class='mt-2 list-disc list-inside {position_class}'>"
            for item in unordered_list:
                text_html += f"<li>{item}</li>"
            text_html += "</ul>"
        
        self.texts_html.append(text_html)
    
    def render_dashboard(self, title='Adash Dashboard'):
        # Render tables first
        tables_content = '\n'.join(self.tables_html)
        
        # Render text content
        texts_content = '\n'.join(self.texts_html)
        
        # Render plots and handle title positioning
        plots_content = ''
        for plot in self.plots_html:
            title_html = ''
            if plot['title']:
                title_html = f"<h3 class='text-xl font-semibold {self._get_title_position_class(plot['position'])}'>{plot['title']}</h3>"

            plots_content += f"{title_html}\n{plot['html']}\n"
        
        # Combine all contents in the desired order
        content_html = tables_content + texts_content + plots_content
        
        # HTML Template embedded directly in the script
        base_html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ title }}</title>
            <link href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css" rel="stylesheet">
            <link href="https://cdn.datatables.net/1.13.4/css/dataTables.bootstrap4.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@^2/dist/tailwind.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mx-auto p-4">
                <h1 class="text-3xl font-bold mb-4">{{ title }}</h1>
                {{ content|safe }}
            </div>

            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
            <script>
                $(document).ready(function() {
                    $('table').DataTable({
                        "pagingType": "simple_numbers",
                        "lengthMenu": [10, 25, 50, 75, 100],
                        "pageLength": 10,
                        "responsive": true,
                        "autoWidth": false,
                        "searching": true,
                        "ordering": true,
                        "info": true,
                        "language": {
                            "search": "Search:",
                            "lengthMenu": "Show _MENU_ entries",
                            "info": "Showing _START_ to _END_ of _TOTAL_ entries",
                            "paginate": {
                                "first": "First",
                                "last": "Last",
                                "next": "Next",
                                "previous": "Previous"
                            }
                        }
                    });
                });
            </script>
        </body>
        </html>
        """
        
        template = Template(base_html_template)
        html_content = template.render(title=title, content=content_html)
        
        return html_content
    
    def _get_text_position_class(self, position):
        if position == 'left':
            return 'text-left'
        elif position == 'right':
            return 'text-right'
        elif position == 'justify':
            return 'text-justify'
        elif position == 'start':
            return 'text-start'
        elif position == 'end':
            return 'text-end'
        else:
            return 'text-center'
    
    def _get_title_position_class(self, position):
        if position == 'left':
            return 'text-left'
        elif position == 'right':
            return 'text-right'
        else:
            return 'text-center'
    
    def save_dashboard(self, output_file):
        html_content = self.render_dashboard()
        with open(output_file, 'w') as f:
            f.write(html_content)
        print(f"Dashboard saved to {output_file}")

# Example of using the updated Adash library
if __name__ == "__main__":
    df = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=100, freq='D'),
        'Value': [i * 10 for i in range(100)],
        'Category': ['Category 1' if i % 2 == 0 else 'Category 2' for i in range(100)],
        'Details': ['Detail A' if i % 3 == 0 else 'Detail B' for i in range(100)]
    })
    
    adash = Adash()
    
    # Input data
    adash.input_file(df)
    
    # Set layout
    adash.set_layout([2, 3])
    
    # Generate table
    adash.adash_table()
    
    # Generate plots with titles and positions
    fig_line = px.line(df, x='Date', y='Value')
    adash.adash_plot(fig=fig_line, title="Line Plot", position="left")

    fig_bar = px.bar(df, x='Category', y='Value')
    adash.adash_plot(fig=fig_bar, title="Bar Plot", position="center")
    
    fig_scatter = px.scatter(df, x='Date', y='Value')
    adash.adash_plot(fig=fig_scatter, title="Scatter Plot", position="right")
    
    fig_histogram = px.histogram(df, x='Value')
    adash.adash_plot(fig=fig_histogram, title="Histogram", position="center")
    
    # Add text content with alignment
    adash.adash_text(
        heading="Summary Section",
        textlines=["This is a summary of the data.", "The following points are noteworthy."],
        ordered_list=["First important point", "Second important point"],
        unordered_list=["Additional note A", "Additional note B"],
        position="left"
    )
    
    # Save dashboard
    adash.save_dashboard('dashboard18.html')

