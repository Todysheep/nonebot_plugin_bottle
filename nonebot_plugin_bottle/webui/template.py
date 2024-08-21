from jinja2 import Template

template_str = """
<div class="bottle-content">
    {% for item in data %}
        {% if item.type == 'text' %}
            <p>{{ item.data.text }}</p>
        {% elif item.type == 'cached_image' %}
            <img src="/bottle/images/{{ item.data.file }}" alt="Cached Image" class="bottle-cached-image">
        {% elif item.type == 'image' %}
            <img src="{{ item.data.url }}" alt="Image" class="bottle-cached-image">
        {% endif %}
    {% endfor %}
</div>
"""

# Create a Jinja2 Template object
template = Template(template_str)

def getHtml(data):
    return template.render(data=data)
