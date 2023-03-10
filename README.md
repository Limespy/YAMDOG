# Overview of YAMDOG <!-- omit in toc -->

[![PyPI Package latest release](https://img.shields.io/pypi/v/yamdog.svg)][1]
[![PyPI Wheel](https://img.shields.io/pypi/wheel/yamdog.svg)][1]
[![Supported versions](https://img.shields.io/pypi/pyversions/yamdog.svg)][1]
[![Supported implementations](https://img.shields.io/pypi/implementation/yamdog.svg)][1]

Yet Another Markdown Only Generator

## What is YAMDOG? <!-- omit in toc -->

YAMDOG is toolkit for creating Markdown text using Python. Markdown is a light and relatively simple markup language.

### Table of Content <!-- omit in toc -->

- [Quick start guide](#quick-start-guide)
    - [The first steps](#the-first-steps)
        - [Install](#install)
        - [Import](#import)
    - [Using the package](#using-the-package)
        - [Making elements](#making-elements)
            - [Heading](#heading)
            - [Example heading](#example-heading)
            - [Paragraph](#paragraph)
            - [Table](#table)
            - [Compact table](#compact-table)
            - [Listing](#listing)
            - [Checklist](#checklist)
            - [Link](#link)
            - [Codeblock](#codeblock)
            - [Code](#code)
            - [Address](#address)
            - [Quote block](#quote-block)
        - [Combining elements into a document](#combining-elements-into-a-document)
            - [Example heading](#example-heading1)
- [Changelog](#changelog)
- [Further reading](#further-reading)
- [Annexes](#annexes)
    - [Annex 1: README Python source](#annex-1-readme-python-source)

# Quick start guide

Here's how you can start automatically generating Markdown documents

## The first steps



### Install

Install YAMDOG with pip. YAMDOG uses only Python standard library so it has no additional dependencies.

```
pip install yamdog
```

### Import

Import name is the same as install name, yamdog.

```python
import yamdog
```

Since the package is accessed often, I use abbreviation`md` for MarkDown. The abbreviation is used throughout this document.

```python
import yamdog as md
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
heading = md.Heading(4, 'Example heading')
```

*Markdown source*

```markdown
#### Example heading
```

*Rendered result*

#### Example heading

---

**bolded text**

*some italiced text*

~~striken text~~

==highlighted text==

==*~~**All styles combined**~~*==

```python
bold_text = md.Text('bolded text', {md.BOLD})
italiced_text = md.Text('some italiced text', {md.ITALIC})
strikethrough_text = md.Text('striken text', {md.STRIKETHROUGH})
highlighted_text = md.Text('highlighted text', {md.HIGHLIGHT})
all_together = md.Text('All styles combined',
                               {md.BOLD, md.ITALIC,
                                md.STRIKETHROUGH, md.HIGHLIGHT})
```

---

#### Paragraph

*Python source*

```python
paragraph = md.Paragraph(['Example paragraph containing ',
                          md.Text('bolded text', {md.BOLD})])
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
table = md.Table(['First column', 'Second column', 'Third column'],
                 [['a', 1, 'Python'],
                  ['b', 2, 'Markdown']],
                 [md.RIGHT, md.LEFT, md.CENTER])
```

*Markdown source*

```markdown
| First column | Second column | Third column |
| -----------: | :------------ | :----------: |
|            a | 1             |    Python    |
|            b | 2             |   Markdown   |
```

*Rendered result*

| First column | Second column | Third column |
| -----------: | :------------ | :----------: |
|            a | 1             |    Python    |
|            b | 2             |   Markdown   |

---

You can select compact mode at the table object creation

#### Compact table

*Python source*

```python
table = md.Table(['First column', 'Second column', 'Third column'],
                 [['a', 1, 'Python'],
                  ['b', 2, 'Markdown']],
                 [md.RIGHT, md.LEFT, md.CENTER],
                 True)
```

*Markdown source*

```markdown
First column|Second column|Third column
--:|:--|:-:
a|1|Python
b|2|Markdown
```

*Rendered result*

First column|Second column|Third column
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
listing = md.Listing(md.UNORDERED, 
                     ['Just normal text',
                      md.Text('some stylised text', {md.ITALIC}),
                      md.Checkbox(False, 'Listings can include checkboxes'),
                      md.Checkbox(True, 'Checked and unchecked option available'),
                      ('Sublist by using a tuple',
                        md.Listing(md.ORDERED,
                                  ['first', 'second']))])
```

*Markdown source*

```markdown
- Just normal text
- *some stylised text*
- [ ] Listings can include checkboxes
- [x] Checked and unchecked option available
- Sublist by using a tuple
    1. first
    2. second
```

*Rendered result*

- Just normal text
- *some stylised text*
- [ ] Listings can include checkboxes
- [x] Checked and unchecked option available
- Sublist by using a tuple
    1. first
    2. second

---

#### Checklist

*Python source*

```python
checklist = md.make_checklist([(False, 'unchecked box'),
                               (True, 'checked box'),
                               (True, 'done')])
```

*Markdown source*

```markdown

```

*Rendered result*



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
#### Example heading

[Link to Markdown Guide](https://www.markdownguide.org)

Example paragraph containing **bolded text**

- Just normal text
- *some stylised text*
- [ ] Listings can include checkboxes
- [x] Checked and unchecked option available
- Sublist by using a tuple
    1. first
    2. second
```

*Rendered result*

#### Example heading

[Link to Markdown Guide](https://www.markdownguide.org)

Example paragraph containing **bolded text**

- Just normal text
- *some stylised text*
- [ ] Listings can include checkboxes
- [x] Checked and unchecked option available
- Sublist by using a tuple
    1. first
    2. second

# Changelog

## 0.4.0 2023-01-23 <!-- omit in toc -->

- Much better type validation
- Some comparisons

## 0.3.1 2023-01-23 <!-- omit in toc -->

- Preliminary type validation
- Full test coverage

# Further reading

- [basic syntax][2]
- [extended syntax][2]

---

# Annexes

## Annex 1: README Python source

And here the full source code that wrote this README. This can serve as a more advanced example of what this is capable of.

[The python file can also be found here](https://github.com/Limespy/YAMDOG/blob/main/readme.py)

```python
import yamdog as md

import pathlib
import re

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
    checklist = md.make_checklist([(False, 'unchecked box'),
                                   (True, 'checked box'),
                                   (True, 'done')])

    doc += get_example('checklist', checklist)
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

def make_quick_start_guide(name, pypiname, source):
    doc = md.Document([
        md.Heading(1, 'Quick start guide'),
        "Here's how you can start automatically generating Markdown documents",
        md.Heading(2, 'The first steps'),
        '',
        md.Heading(3, 'Install'),
        f'''Install {name} with pip.
        {name} uses only Python standard library so it has no additional dependencies.''',
        md.CodeBlock(f'pip install {pypiname}'),
        md.Heading(3, 'Import'),
        f'''Import name is the same as install name, {pypiname}.''',
        md.CodeBlock(f'import {pypiname}', 'python'),
        md.Paragraph(['Since the package is accessed often, I use abbreviation',
                      md.Code('md'), 
                      ' for MarkDown. The abbreviation is used throughout this document.']),
        md.CodeBlock(f'import {pypiname} as md', 'python'),
        md.Heading(2, 'Using the package'),
        f'There are two main things to building a Markdown document using {name}',
        md.Listing(md.ORDERED, ['Making elements',
                               'Combining elements into a document']),
        md.Paragraph(['You can call ',
            md.Code('str'),
            ' on the element directly to get the markdown source']),
        md.CodeBlock('markdown_source = str(element)', 'python'),
        '''but most of the time you will compose the elements together into an
        document''',
        md.CodeBlock('markdown_source = str(document)', 'python')
        ])
    doc += make_examples(source)
    return doc


def make_changelog():
    doc = md.Document([md.Heading(1, 'Changelog')])

    changelog = (('0.4.0', '2023-01-23', ['Much better type validation',
                                          'Some comparisons']),
                 ('0.3.1', '2023-01-23', ['Preliminary type validation',
                                          'Full test coverage'])
                 )

    for version, date, changes in changelog:
        doc += md.Heading(2, f'{version} {date}', in_TOC = False)
        doc += md.Listing(md.UNORDERED, changes)

    return doc

def make_further_reading():
    basic_syntax_link = md.Link('basic syntax',
                                'https://www.markdownguide.org/basic-syntax/',
                                '')
    extended_syntax_link = md.Link('extended syntax',
                                  'https://www.markdownguide.org/basic-syntax/',
                                   '')

    doc = md.Document([md.Heading(1, 'Further reading')])
    doc += md.Listing(md.UNORDERED, [basic_syntax_link, extended_syntax_link])
    return doc

def make_annexes(source):
    doc = md.Document([md.Heading(1, 'Annexes')])
    doc += md.Heading(2, 'Annex 1: README Python source')
    doc += '''And here the full source code that wrote this README.
            This can serve as a more advanced example of what this is
            capable of.'''
    doc += md.Link('The python file can also be found here',
                   'https://github.com/Limespy/YAMDOG/blob/main/readme.py')
    doc += md.CodeBlock(source, 'python')
    return doc

def make_readme(name, pypiname, source):
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
    doc = md.Document([
        md.Heading(1, f'Overview of {name}', in_TOC = False),
        md.Paragraph(pypi_badges, '\n'),
        'Yet Another Markdown Only Generator',
        md.Heading(2, f'What is {name}?', in_TOC = False),
        f'''{name} is toolkit for creating Markdown text using Python.
        Markdown is a light and relatively simple markup language.''',
        md.Heading(3, 'Table of Content', in_TOC = False),
        md.TOC()
        ])
    doc += make_quick_start_guide(name, pypiname, source)
    doc += make_changelog()
    doc += make_further_reading()
    doc += md.HRule()
    doc += make_annexes(source)
    return doc

def main():
    name = 'YAMDOG'
    pypiname = 'yamdog'

    source = pathlib.Path(__file__).read_text('utf8')

    doc = make_readme(name, pypiname, source)

    (pathlib.Path(__file__).parent / 'README.md').write_text(str(doc), 'utf8')
    return doc

if __name__ == '__main__':
    main()
```

[1]: <https://pypi.org/project/yamdog> ""
[2]: <https://www.markdownguide.org/basic-syntax/> ""