from nbconvert import MarkdownExporter
import nbformat

def notebook_to_markdown(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)

    markdown_cells = [cell.source for cell in notebook.cells if cell.cell_type == 'markdown']

    markdown_text = '\n\n'.join(markdown_cells)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_text)


if __name__ == "__main__":
    input_notebook = "challenge.ipynb" 
    output_markdown = "data_munging.md"

    notebook_to_markdown(input_notebook, output_markdown)
