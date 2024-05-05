#pip install json2table
#pip install Jinja2

from jinja2 import Template
from json2table import convert
import requests

def build_html_table_from_json(json_object):
    """
    Converts a JSON object to an HTML table.

    Args:
        json_object (dict): JSON object to convert.

    Returns:
        str: HTML representation of the JSON object as a table.
    """
    build_direction = "LEFT_TO_RIGHT"
    table_attributes = {"style": "width:100%"}
    html_table = convert(json_object, build_direction=build_direction, table_attributes=table_attributes)
    return html_table

def render_html_template(title, content):
    """
    Renders an HTML template using provided title and content.

    Args:
        title (str): The title of the report.
        content (str): HTML content to include in the report.

    Returns:
        str: Rendered HTML content.
    """
    template = requests.get("https://raw.githubusercontent.com/pvanand07/Multi-Agent-Research/master/scripts/json2html_report_template.html").text
    rendered_template = Template(template).render(title=title, content=content)
    return rendered_template

def json2html_report(json_data, report_title):
    """
    Generates an HTML report from JSON output.

    Args:
        json_data (dict): JSON data to convert into an HTML table.
        report_title (str): Title of the report.
    
    Returns:
        str: Rendered HTML file.
    
    Side effects:
        Writes an HTML file based on the JSON data.
    """
    # Convert JSON to HTML table
    html_content = build_html_table_from_json(json_data)

    # Render the full HTML page
    rendered_html = render_html_template(report_title, html_content)

    print("JSON converted to HTML report")
    return rendered_html

if __name__ == "__main__":
    # Sample JSON data and report title
    sample_json_data = {
        "Name": "John Doe",
        "Age": 30,
        "City": "New York"
    }
    sample_report_title = "Sample Report"

    # Generate and save the HTML report
    json2html_report(sample_json_data, sample_report_title, "sample_report")
