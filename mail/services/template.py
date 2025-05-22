from core.config import TEMPLATES_DIR
from jinja2 import Template


def  get_template(name: str, params: dict):
    with open(f"{TEMPLATES_DIR}/{name}", "r", encoding="utf-8") as f:
        template_str = f.read()

    template = Template(template_str)
    return template.render(params)
