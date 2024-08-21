"""Mapping between SQLAlchemy column types and most suitable configuration of HTML input elements."""

sqlalchemy_to_html_mapping = {
    "Boolean": [{"html_tag": "input", "html_tag_args": {"type": "checkbox"}}],
    "DateTime": [{"html_tag": "input", "html_tag_args": {"type": "datetime-local"}}],
    "Date": [{"html_tag": "input", "html_tag_args": {"type": "date"}}],
    "Integer": [{"html_tag": "input", "html_tag_args": {"type": "number", "step": 1}}],
    "String": [{"html_tag": "input", "html_tag_args": {"type": "text"}}],
    "Text": [{"html_tag": "textarea", "html_tag_args": {"type": "text"}}],
    "Time": [{"html_tag": "input", "html_tag_args": {"type": "time"}}],
}
