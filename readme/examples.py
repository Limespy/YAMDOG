import pathlib
import re

import yamdog as md
# ======================================================================
SOURCE = pathlib.Path(__file__).read_text('utf8')
PATTERN = re.compile('\n    #%% ')
# ======================================================================
def main() -> md.Document:
    '''Examples are collected via source code introspection'''
    # First getting the example code blocks

    examples = {}
    for block in PATTERN.split(SOURCE)[1:]:
        name, rest = block.split('\n', 1) # from the comment
        code = rest.split('\n\n', 1)[0].replace('\n    ', '\n').strip()
        examples[name.strip()] = md.CodeBlock(code, 'python')

    def get_example(title: str, element: md.Element) -> md.Document:
        return md.Document([md.Heading(title.capitalize(), 4),
                            md.Text('Python source', {md.ITALIC}),
                            examples[title],
                            md.Text('Markdown source', {md.ITALIC}),
                            md.CodeBlock(element, 'markdown'),
                            md.Text('Rendered result', {md.ITALIC}),
                            element,
                            md.HRule()])

    # Starting the actual doc
    doc = md.Document([
        md.Heading('Making elements', 3),
    ])

    #%% document
    document = md.Document([])

    doc += "Let's start with an empty document"
    doc += examples['document']

    #%% adding to document
    # document +=

    #%% heading
    heading = md.Heading('Example heading', 4)

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

    #%% paragraph
    paragraph = md.Paragraph(['Example paragraph containing ',
                              md.Text('bolded text', {md.BOLD})])

    doc += get_example('paragraph', paragraph)

    #%% table
    table = md.Table([['a', 1, 'Python'],
                      ['b', 2, 'Markdown']],
                     ['First column', 'Second column', 'Third column'],
                     [md.RIGHT, md.LEFT, md.CENTER])

    doc += get_example('table', table)

    #%% compact table
    table = md.Table([['a', 1, 'Python'],
                      ['b', 2, 'Markdown']],
                     ['First column', 'Second column', 'Third column'],
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
    listing = md.Listing(['Just normal text',
                          md.Text('some stylised text', {md.ITALIC}),
                          md.Checkbox('Listings can include checkboxes', False),
                          md.Checkbox('Checked and unchecked option available', True),
                          ('Sublist by using a tuple',
                            md.Listing(['first', 'second'], md.ORDERED))],
                          md.UNORDERED)

    doc += get_example('listing', listing)

    #%% checklist
    checklist = md.make_checklist([('unchecked box', False),
                                   ('checked box', True),
                                   ('done', True)])

    doc += get_example('checklist', checklist)
    #%% link
    link = md.Link('https://www.markdownguide.org', 'Link to Markdown Guide')

    doc += get_example('link', link)

    #%% codeblock
    codeblock = md.CodeBlock('import yamdog as md\n\ndoc = md.Document([])',
                             'python')

    doc += get_example('codeblock', codeblock)

    #%% code
    code = md.Code('python != markdown')

    doc += get_example('code', code)

    #%% Image
    # image = md.Image()

    #%% address
    address = md.Link('https://www.markdownguide.org')

    doc += get_example('address', address)

    #%% quote block
    quoteblock = md.Quote('Quote block supports\nmultiple lines')

    doc += get_example('quote block', quoteblock)

    doc += md.Heading('Combining elements into a document', 3)

    #%% calling document
    document = md.Document([heading, link, paragraph, listing])

    doc += 'Initialising Document with list of elements'
    doc += examples['calling document']

    #%% from empty document
    document = md.Document([])
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
