import re


def isolate(content, start_index):
    """
    Finds the end index of the group corresponding to the scope of the given index and removes the content between the start and end index.

    Args:
        content (str): The content of the SVG file.
        start_index (int): The index of the path that needs to be isolated.

    Returns:
        str: The content of the SVG file with the path removed.
    """
    s_index = start_index - 1
    counter = 1
    while counter != 0:
        index_open = content.find("<g", start_index)
        index_close = content.find("</g>", start_index)
        if index_open < index_close:
            counter += 1
            start_index = index_open + len("<g")
        else:
            counter -= 1
            start_index = index_close + len("</g>")
    e_index = index_close + len("</g>")

    # Remove the content between the start and end index
    content = content[:s_index] + content[e_index:]

    return content


def remove_rouge_instances(content):
    """
    Removes all the paths that are not inside a group.

    Args:
        content (str): The content of the SVG file.

    Returns:
        str: The content of the SVG file with only the paths inside a group.
    """
    pattern = r"<path fill.*?</path>|<path fill.*?/>"
    paths = re.findall(pattern, content, re.DOTALL)
    for path in paths:
        if not is_inside_group(path):
            content = content.replace(path, "")
    return content


def is_inside_group(path):
    """
    Checks if the path is inside a <g>...</g>

    Args:
        path (str): The path that needs to be checked.

    Returns:
        bool: True if the path is inside a group, False otherwise.
    """
    return "<g>" in path and "</g>" in path


def clean_content(content):
    """
    Cleans up the SVG and converts all text to white and background to black

    Args:
        content (str): The content of the SVG file.

    Returns:
        str: The cleaned and formatted SVG content.
    """
    content = remove_rouge_instances(content)

    keyword = 'width="450" fill="#'
    start = 0
    while True:
        start = content.find(keyword, start)
        if start == -1:
            break
        start += len(keyword)
        content = content[:start] + "000000" + content[start + 6 :]
        start += 6

    keyword = '<g fill="#'
    start = 0
    while True:
        start = content.find(keyword, start)
        if start == -1:
            break
        start += len(keyword)
        content = content[:start] + "ffffff" + content[start + 6 :]
        start += 6

    return content
