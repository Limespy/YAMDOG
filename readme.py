import yamdog as md

import pathlib
import re


def main():
    name = 'YAMDOG'
    pypiname = 'yamdog'

    source = pathlib.Path(__file__).read_text('utf8')
    
    # Setup for the badges
    shields_url = 'https://img.shields.io/'

    pypi_project_url = f'https://pypi.org/project/{pypiname}'
    pypi_badge_info = (('v', 'PyPI Package latest release'),
                       ('wheel', 'PyPI Wheel'),
                       ('pyversions', 'Supported versions'),
                       ('implementation', 'Supported implementations'))
    pypi_badges = [md.Link(md.Image(f'{shields_url}pypi/{code}/{pypiname}.svg',
                                    desc), pypi_project_url, '')
                   for code, desc in pypi_badge_info]

    # Starting the document
    metasection = md.Document([
        md.Heading(1, f'Overview of {name}', in_TOC = False),
        md.Paragraph(pypi_badges, '\n'),
        'Yet Another Markdown Only Generator',
        md.Heading(2, f'What is {name}?', in_TOC = False),
        f'''{name} is toolkit for creating Markdown text using Python.
        Markdown is a light and relatively simple markup language.''',
        md.TOC()
        ]
    )

    quick_start_guide = md.Document([
        md.Heading(1, 'Quick start guide'),
        "Here's how you can start automatically generating Markdown documents",
        md.Heading(2, 'The first steps'),
        '',
        md.Heading(3, 'Install'),
        f'''Install {name} with pip.
        {name} uses only Python standard library so it has no additional dependencies.''',
        md.CodeBlock(f'pip install {pypiname}'),
        md.Heading(2, 'Using the package'),
        f'There are two main things to building a Markdown document using {name}',
        md.Listing(md.ORDERED, ['Making elements',
                               'Combining elements into a document']),
        md.Paragraph(['You can call ',
            md.Code('str'),
            ' on the element directly to get the markdown source']),
        md.CodeBlock('markdown_source = str(element)', 'python'),
        'but most of the time you will compose the elements together into an document',
        md.CodeBlock('markdown_source = str(document)', 'python')
        ])

    # EXAMPLES

    quick_start_guide += make_examples(source)


    doc = metasection + quick_start_guide
    basic_syntax_link = md.Link('basic syntax',
                                'https://www.markdownguide.org/basic-syntax/',
                                '')
    ext_syntax_link = md.Link('extended syntax',
                              'https://www.markdownguide.org/basic-syntax/',
                              '')
    doc += md.HRule()
    doc += md.Heading(1, 'Annexes')
    doc += md.Heading(2, 'Annex 1: README Python source')
    doc += '''And here the full source code that wrote this README.
            This can serve as a more advanced example of what this is capable of.'''
    doc += md.Link('The python file can also be found here', 'https://github.com/Limespy/YAMDOG/blob/main/readme.py')
    doc += md.CodeBlock(source, 'python')
    
    (pathlib.Path(__file__).parent / 'README.md').write_text(str(doc), 'utf8')

def make_examples(source: str) -> md.Document:
    '''Examples are collected via source code introspection'''
    # First getting the example code blocks
    pattern = re.compile('\n    #%% ')
    examples = {}
    for block in pattern.split(source)[1:]:
        name, rest = block.split('\n', 1) # from the comment
        code = rest.split('\n\n', 1)[0].replace('\n    ', '\n').strip()
        examples[name.strip()] = md.CodeBlock(code, 'python')

    def get_example(title: str, element: md.Element) -> md.Document:
        return md.Document([md.Heading(4, title.capitalize()),
                            md.Text('Python source', {md.ITALIC}),
                            examples[title],
                            md.Text('Markdown source', {md.ITALIC}),
                            md.CodeBlock(element, 'markdown'),
                            md.Text('Rendered result', {md.ITALIC}),
                            element,
                            md.HRule()])

    # Starting the actual doc
    doc = md.Document([
        md.Heading(3, 'Making elements'),

    ])

    #%% document
    document = md.Document()

    doc += "Let's start with an empty document"
    doc += examples['document']

    #%% adding to document
    # document += 

    #%% heading
    heading = md.Heading(4, 'Example heading')

    doc += get_example('heading', heading)

    #%% stylised
    bold_text = md.Text('bolded text', {md.BOLD})
    italiced_text = md.Text('some italiced text', {md.ITALIC})
    strikethrough_text = md.Text('striken text', {md.STRIKETHROUGH})
    highlighted_text = md.Text('highlighted text', {md.HIGHLIGHT})
    all_together = md.Text('All styles combined',
                                   {md.BOLD, md.ITALIC,
                                    md.STRIKETHROUGH, md.HIGHLIGHT})

    doc += bold_text
    doc += italiced_text
    doc += strikethrough_text
    doc += highlighted_text
    doc += all_together
    doc += examples['stylised']
    doc += md.HRule()

    #%%  paragraph
    paragraph = md.Paragraph(['Example paragraph containing ',
                              md.Text('bolded text', {md.BOLD})])

    doc += get_example('paragraph', paragraph)

    #%% table
    table = md.Table(['First column', 'Second column', 'Third column'],
                     [['a', 1, 'Python'],
                      ['b', 2, 'Markdown']],
                     [md.RIGHT, md.LEFT, md.CENTER])

    doc += get_example('table', table)

    #%% compact table
    table = md.Table(['First column', 'Second column', 'Third column'],
                     [['a', 1, 'Python'],
                      ['b', 2, 'Markdown']],
                     [md.RIGHT, md.LEFT, md.CENTER],
                     True)

    doc += 'You can select compact mode at the table object creation'
    doc += get_example('compact table', table)

    #%% table compact attribute
    table.compact = True

    doc += md.Paragraph(['or later by changing the attribute ',
                         md.Code('compact')])
    doc += examples['table compact attribute']

    #%% listing
    listing = md.Listing(md.UNORDERED, 
                         ['Just normal text',
                          md.Text('some stylised text', {md.ITALIC}),
                          md.Checkbox(False, 'Listings can include checkboxes'),
                          md.Checkbox(True, 'Checked and unchecked option available'),
                          ('Sublist by using a tuple',
                            md.Listing(md.ORDERED,
                                      ['first', 'second']))])

    doc += get_example('listing', listing)

    #%% checklist


    #%% link
    link = md.Link('Link to Markdown Guide', 'https://www.markdownguide.org')

    doc += get_example('link', link)

    #%% codeblock
    codeblock = md.CodeBlock('import yamdog as md\n\ndoc = md.Document()',
                             'python')

    doc += get_example('codeblock', codeblock)

    #%% code
    code = md.Code('python != markdown')

    doc += get_example('code', code)

    #%% Image
    # image = md.Image()

    #%% address
    address = md.Address('https://www.markdownguide.org')

    doc += get_example('address', address)

    #%% quote block
    quoteblock = md.QuoteBlock('Quote block supports\nmultiple lines')

    doc += get_example('quote block', quoteblock)

    doc += md.Heading(3, 'Combining elements into a document')

    #%% calling document
    document = md.Document([heading, link, paragraph, listing])

    doc += 'Initialising Document with list of elements'
    doc += examples['calling document']

    #%% from empty document
    document = md.Document()
    document += heading
    document += link
    document += paragraph
    document += listing

    doc += 'adding elements into a document'
    doc += examples['from empty document']

    #%% document by adding
    document = heading + link + paragraph + listing

    doc += 'adding elements together into a document'
    doc += examples['document by adding']

    #%% document concatenation
    document1 = md.Document([heading, link])
    document2 = md.Document([paragraph, listing])
    document = document1 + document2

    doc += 'Adding two documents together'
    doc += examples['document concatenation']

    doc += md.Text('Markdown source', {md.ITALIC})
    doc += md.CodeBlock(document, 'markdown')
    doc += md.Text('Rendered result', {md.ITALIC})
    doc += document

    return doc

if __name__ == '__main__':
    main()