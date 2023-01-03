# Overview of YAMDOG <!-- omit in toc -->

[![PyPI Package latest release](https://img.shields.io/pypi/v/yamdog.svg)][1]
[![PyPI Wheel](https://img.shields.io/pypi/wheel/yamdog.svg)][2]
[![Supported versions](https://img.shields.io/pypi/pyversions/yamdog.svg)][3]
[![Supported implementations](https://img.shields.io/pypi/implementation/yamdog.svg)][4]

Yet Another Markdown Only Generator

## What is YAMDOG?

YAMDOG is toolkit for creating Markdown text using Python.
Markdown is a light and relatively simple markup language.

# Quick start guide

Here's how you can start automatically generating Markdown documents

## The first steps



### Install

Install YAMDOG with pip.
YAMDOG uses only Python standard library so it has no additional dependencies.

```
pip install yamdog
```

## Using the package

There are two main things to building a Markdown document using YAMDOG

1. Making elements
2. Combining elements into a document

You can call `str` on the element directly to get the markdown source

```python
markdown_source = str(element)
```

but most of the time you will compose the elements together into an document

```python
markdown_source = str(document)
```

### Making elements

Let's start with an empty document

```python
document = md.Document()
```

#### Heading

*Python source*

```python
heading = md.Heading(3, 'Example heading')
```

*Markdown source*

```markdown
### Example heading
```

*Rendered result*

### Example heading

---

**bolded text**

*some italiced text*

~~striken text~~

*~~**All styles combined**~~*

```python
bold_text = md.Text('bolded text', {'bold'})
italiced_text = md.Text('some italiced text', {'italic'})
strikethrough_text = md.Text('striken text', {'strikethrough'})
all_together = md.Text('All styles combined',
                               {'bold', 'italic', 'strikethrough'})
```

---

#### Paragraph

*Python source*

```python
paragraph = md.Paragraph(['Example paragraph containing ',
                          md.Text('bolded text', {'bold'})])
```

*Markdown source*

```markdown
Example paragraph containing **bolded text**
```

*Rendered result*

Example paragraph containing **bolded text**

---

#### Table

*Python source*

```python
table = md.Table(['First column', 'Second column', 'third column'],
                 ['right', 'left', 'center'],
                 [['a', 1, 'Python'],
                  ['b', 2, 'Markdown']])
```

*Markdown source*

```markdown
| First column | Second column | third column |
| -----------: | :------------ | :----------: |
|            a | 1             |    Python    |
|            b | 2             |   Markdown   |
```

*Rendered result*

| First column | Second column | third column |
| -----------: | :------------ | :----------: |
|            a | 1             |    Python    |
|            b | 2             |   Markdown   |

---

You can select compact mode at the table object creation

#### Compact table

*Python source*

```python
table = md.Table(['First column', 'Second column', 'third column'],
                 ['right', 'left', 'center'],
                 [['a', 1, 'Python'],
                  ['b', 2, 'Markdown']],
                 True)
```

*Markdown source*

```markdown
First column|Second column|third column
--:|:--|:-:
a|1|Python
b|2|Markdown
```

*Rendered result*

First column|Second column|third column
--:|:--|:-:
a|1|Python
b|2|Markdown

---

or later by changing the attribute `compact`

```python
table.compact = True
```

#### Listing

*Python source*

```python
listing = md.Listing('unordered', 
                     ['Just normal text',
                      md.Text('some stylised text', {'italic'}),
                      ('Sublist by using a tuple',
                        md.Listing('ordered',
                                  ['first', 'second']))])
```

*Markdown source*

```markdown
- Just normal text
- *some stylised text*
- Sublist by using a tuple
    3. first
    4. second
```

*Rendered result*

- Just normal text
- *some stylised text*
- Sublist by using a tuple
    5. first
    6. second

---

#### Link

*Python source*

```python
link = md.Link('Link to Markdown Guide', 'https://www.markdownguide.org')
```

*Markdown source*

```markdown
[Link to Markdown Guide](https://www.markdownguide.org)
```

*Rendered result*

[Link to Markdown Guide](https://www.markdownguide.org)

---

#### Codeblock

*Python source*

```python
codeblock = md.CodeBlock('import yamdog as md\n\ndoc = md.Document()',
                         'python')
```

*Markdown source*

````markdown
```python
import yamdog as md

doc = md.Document()
```
````

*Rendered result*

```python
import yamdog as md

doc = md.Document()
```

---

#### Code

*Python source*

```python
code = md.Code('python != markdown')
```

*Markdown source*

```markdown
`python != markdown`
```

*Rendered result*

`python != markdown`

---

#### Address

*Python source*

```python
address = md.Address('https://www.markdownguide.org')
```

*Markdown source*

```markdown
<https://www.markdownguide.org>
```

*Rendered result*

<https://www.markdownguide.org>

---

#### Quote block

*Python source*

```python
quoteblock = md.QuoteBlock('Quote block supports\nmultiple lines')
```

*Markdown source*

```markdown
> Quote block supports
> multiple lines
```

*Rendered result*

> Quote block supports
> multiple lines

---

### Combining elements into a document

Initialising Document with list of elements

```python
document = md.Document([heading, link, paragraph, listing])
```

adding elements into a document

```python
document = md.Document()
document += heading
document += link
document += paragraph
document += listing
```

adding elements together into a document

```python
document = heading + link + paragraph + listing
```

Adding two documents together

```python
document1 = md.Document([heading, link])
document2 = md.Document([paragraph, listing])
document = document1 + document2
```

*Markdown source*

```markdown
### Example heading

[Link to Markdown Guide](https://www.markdownguide.org)

Example paragraph containing **bolded text**

- Just normal text
- *some stylised text*
- Sublist by using a tuple
    7. first
    8. second
```

*Rendered result*

### Example heading

[Link to Markdown Guide](https://www.markdownguide.org)

Example paragraph containing **bolded text**

- Just normal text
- *some stylised text*
- Sublist by using a tuple
    9. first
    10. second

---

## Annexes

### Annex 1, README Python source

And here the full source code that wrote this README.
This can serve as a more advanced example of what this is capable of.

```python
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
        md.Heading(2, 'Using the package'),
        f'There are two main things to building a Markdown document using {name}',
        md.Listing('ordered', ['Making elements',
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
    doc += md.Heading(2, 'Annexes')
    doc += md.Heading(3, 'Annex 1, README Python source')
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
                            md.Text('Python source', {'italic'}),
                            examples[title],
                            md.Text('Markdown source', {'italic'}),
                            md.CodeBlock(element, 'markdown'),
                            md.Text('Rendered result', {'italic'}),
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

    doc += md.Text('Markdown source', {'italic'})
    doc += md.CodeBlock(document, 'markdown')
    doc += md.Text('Rendered result', {'italic'})
    doc += document

    return doc

if __name__ == '__main__':
    main()
```

[1]: <https://pypi.org/project/yamdog> ""
[2]: <https://pypi.org/project/yamdog> ""
[3]: <https://pypi.org/project/yamdog> ""
[4]: <https://pypi.org/project/yamdog> ""