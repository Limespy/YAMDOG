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

- [x] hmm
- [ ] 1
- no
- Hello
- [x] a
### Install

Install YAMDOG with pip.
YAMDOG uses only Python standard library so it has no additional dependencies.

```
pip install yamdog
```

## The notation

Read the notation

### Examples

Here examples of what each element does.

Let's start with an empty document

```python
document = md.Document()
```

#### Heading

*Python Source*

```python
heading = md.Heading(3, 'Example heading')
```

*Markdown Source*

```markdown
### Example heading
```

*Rendered Result*

### Example heading

---

**bolded text**

*some italiced text*

~~striken text~~

~~***All styles combined***~~

```python
bold_text = md.Text('bolded text', {'bold'})
italiced_text = md.Text('some italiced text', {'italic'})
strikethrough_text = md.Text('striken text', {'strikethrough'})
all_together = md.Text('All styles combined',
                               {'bold', 'italic', 'strikethrough'})
```

---

#### Paragraph

*Python Source*

```python
paragraph = md.Paragraph(['Example paragraph containing ',
                          md.Text('bolded text', {'bold'})])
```

*Markdown Source*

```markdown
Example paragraph containing **bolded text**
```

*Rendered Result*

Example paragraph containing **bolded text**

---

#### Table

*Python Source*

```python
table = md.Table(['First column', 'Second column', 'third column'],
                 ['right', 'left', 'center'],
                 [['a', 1, 'Python'],
                  ['b', 2, 'Markdown']])
```

*Markdown Source*

```markdown
| First column | Second column | third column |
| -----------: | :------------ | :----------: |
|            a | 1             |    Python    |
|            b | 2             |   Markdown   |
```

*Rendered Result*

| First column | Second column | third column |
| -----------: | :------------ | :----------: |
|            a | 1             |    Python    |
|            b | 2             |   Markdown   |

---

You can select compact mode at the table object creation

#### Compact table

*Python Source*

```python
table = md.Table(['First column', 'Second column', 'third column'],
                 ['right', 'left', 'center'],
                 [['a', 1, 'Python'],
                  ['b', 2, 'Markdown']],
                 True)
```

*Markdown Source*

```markdown
First column|Second column|third column
--:|:--|:-:
a|1|Python
b|2|Markdown
```

*Rendered Result*

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

*Python Source*

```python
listing = md.Listing('unordered', 
                     ['Just normal text',
                      md.Text('some stylised text', {'italic'}),
                      ('Sublist by using a tuple',
                        md.Listing('ordered',
                                  ['first', 'second']))])
```

*Markdown Source*

```markdown
- Just normal text
- *some stylised text*
- Sublist by using a tuple
    1. first
    2. second
```

*Rendered Result*

- Just normal text
- *some stylised text*
- Sublist by using a tuple
    3. first
    4. second

---

#### Link

*Python Source*

```python
link = md.Link('Link to Markdown Guide', 'https://www.markdownguide.org')
```

*Markdown Source*

```markdown
[Link to Markdown Guide](https://www.markdownguide.org)
```

*Rendered Result*

[Link to Markdown Guide](https://www.markdownguide.org)

---

#### Codeblock

*Python Source*

```python
codeblock = md.CodeBlock('import yamdog as md\n\ndoc = md.Document()',
                         'python')
```

*Markdown Source*

````markdown
```python
import yamdog as md

doc = md.Document()
```
````

*Rendered Result*

```python
import yamdog as md

doc = md.Document()
```

---

#### Code

*Python Source*

```python
code = md.Code('python != markdown')
```

*Markdown Source*

```markdown
`python != markdown`
```

*Rendered Result*

`python != markdown`

---

#### Address

*Python Source*

```python
address = md.Address('https://www.markdownguide.org')
```

*Markdown Source*

```markdown
<https://www.markdownguide.org>
```

*Rendered Result*

<https://www.markdownguide.org>

---

#### Quote block

*Python Source*

```python
quoteblock = md.QuoteBlock('Quote block supports\nmultiple lines')
```

*Markdown Source*

```markdown
> Quote block supports
> multiple lines
```

*Rendered Result*

> Quote block supports
> multiple lines

---

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
```

[1]: <https://pypi.org/project/yamdog> ""
[2]: <https://pypi.org/project/yamdog> ""
[3]: <https://pypi.org/project/yamdog> ""
[4]: <https://pypi.org/project/yamdog> ""