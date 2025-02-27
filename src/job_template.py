import yaml


def load_yaml_template(template_path, params):
    """Load a YAML template and replace placeholders dynamically."""
    with open(template_path, "r") as file:
        yaml_content = file.read()
    
    for key, value in params.items():
        yaml_content = yaml_content.replace(f"{{{{{key}}}}}", str(value))

    return yaml.safe_load(yaml_content)


def save_yaml_file(content, output_path):
    """Save the modified YAML content to a file."""
    with open(output_path, "w") as file:
        yaml.dump(content, file)
