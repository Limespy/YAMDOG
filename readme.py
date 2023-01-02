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
        md.Heading(1, f'Overview of {name}', False, False),
        md.Paragraph(pypi_badges, '\n'),
        'Yet Another Markdown Only Generator',
        md.Heading(2, f'What is {name}?'),
        f'''{name} is toolkit for creating Markdown text using Python.
Markdown is a light and relatively simple markup language.'''
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
        md.Heading(2, 'The notation'),
        'Read the notation'
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
    doc += '''And here the full source code that wrote this README.
This can serve as a more advanced example of what this is capable of.'''
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
                            md.Text('Python Source', {'italic'}),
                            examples[title],
                            md.Text('Markdown Source', {'italic'}),
                            md.CodeBlock(element, 'markdown'),
                            md.Text('Rendered Result', {'italic'}),
                            element,
                            md.HRule()])

    # Starting the actual doc
    doc = md.Document([
        md.Heading(3, 'Examples'),
        'Here examples of what each element does.'
    ])

    #%% document
    document = md.Document()

    doc += "Let's start with an empty document"
    doc += examples['document']

    #%% adding to document
    # document += 

    #%% heading
    heading = md.Heading(3, 'Example heading')

    doc += get_example('heading', heading)

    #%% stylised
    bold_text = md.Text('bolded text', {'bold'})
    italiced_text = md.Text('some italiced text', {'italic'})
    strikethrough_text = md.Text('striken text', {'strikethrough'})
    all_together = md.Text('All styles combined',
                                   {'bold', 'italic', 'strikethrough'})

    doc += bold_text
    doc += italiced_text
    doc += strikethrough_text
    doc += all_together
    doc += examples['stylised']
    doc += md.HRule()

    #%%  paragraph
    paragraph = md.Paragraph(['Example paragraph containing ',
                              md.Text('bolded text', {'bold'})])

    doc += get_example('paragraph', paragraph)

    #%% table
    table = md.Table(['First column', 'Second column', 'third column'],
                     ['right', 'left', 'center'],
                     [['a', 1, 'Python'],
                      ['b', 2, 'Markdown']])

    doc += get_example('table', table)

    #%% compact table
    table = md.Table(['First column', 'Second column', 'third column'],
                     ['right', 'left', 'center'],
                     [['a', 1, 'Python'],
                      ['b', 2, 'Markdown']],
                     True)

    doc += 'You can select compact mode at the table object creation'
    doc += get_example('compact table', table)

    #%% table compact attribute
    table.compact = True

    doc += md.Paragraph(['or later by changing the attribute ',
                         md.Code('compact')])
    doc += examples['table compact attribute']

    #%% listing
    listing = md.Listing('unordered', 
                         ['Just normal text',
                          md.Text('some stylised text', {'italic'}),
                          ('Sublist by using a tuple',
                            md.Listing('ordered',
                                      ['first', 'second']))])

    doc += get_example('listing', listing)


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

    return doc

if __name__ == '__main__':
    main()