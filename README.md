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

## The notation

Read the notation

### Examples

Here examples of what each element does.

Let's start with an empty document

#### Document

python

```python
document = md.Document()
```

markdown

```markdown



```





---

#### Heading

python

```python
heading = md.Heading(3, 'Example heading')
```

markdown

```markdown
### Example heading
```

### Example heading

---

**bolded text**

*some italiced text*

~~striken text~~

**~~*All styles combined*~~**

```python
bold_text = md.StylisedText('bolded text', {'bold'})
italiced_text = md.StylisedText('some italiced text', {'italic'})
strikethrough_text = md.StylisedText('striken text', {'strikethrough'})
all_together = md.StylisedText('All styles combined',
                               {'bold', 'italic', 'strikethrough'})
```

---

#### Paragraph

python

```python
paragraph = md.Paragraph(['Example paragraph containing ',
                          md.StylisedText('bolded text', {'bold'})])
```

markdown

```markdown
Example paragraph containing **bolded text**
```

Example paragraph containing **bolded text**

---

#### Table

python

```python
table = md.Table(['First column', 'Second column', 'third column'],
                 ['right', 'left', 'center'],
                 [['a', 1, 'Python'],
                  ['b', 2, 'Markdown']])
```

markdown

```markdown
| First column | Second column | third column |
| -----------: | :------------ | :----------: |
|       a      |       1       |    Python    |
|       b      |       2       |   Markdown   |
```

| First column | Second column | third column |
| -----------: | :------------ | :----------: |
|       a      |       1       |    Python    |
|       b      |       2       |   Markdown   |

---

#### Listing

python

```python
listing = md.Listing('unordered', 
                     ['Just normal text',
                      md.StylisedText('some stylised text', {'italic'}),
                      ('Sublist by using a tuple',
                        md.Listing('ordered',
                                  ['first', 'second']))])
```

markdown

```markdown
- Just normal text
- *some stylised text*
- Sublist by using a tuple
    1. first
    2. second
```

- Just normal text
- *some stylised text*
- Sublist by using a tuple
    3. first
    4. second

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
        md.CodeBlock('', f'pip install {pypiname}'),
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
    doc += md.CodeBlock('python', source)

    (pathlib.Path(__file__).parent / 'README.md').write_text(str(doc), 'utf8')

def make_examples(source: str) -> md.Document:
    '''Examples are collected via source code introspection'''
    # First getting the example code blocks
    pattern = re.compile('\n    #%% ')
    examples = {}
    for block in pattern.split(source)[1:]:
        name, rest = block.split('\n', 1)
        code = rest.split('\n\n', 1)[0].replace('\n    ', '\n').strip()
        examples[name.strip()] = md.CodeBlock('python', code)

    def get_example(title: str, element: md.Element) -> md.Document:
        return md.Document([md.Heading(4, title.capitalize()),
                            'python',
                            examples[title],
                            'markdown',
                            md.CodeBlock('markdown', element),
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
    doc += get_example('document', document)

    #%% adding to document
    # document += 

    #%% heading
    heading = md.Heading(3, 'Example heading')

    doc += get_example('heading', heading)

    #%% stylised
    bold_text = md.StylisedText('bolded text', {'bold'})
    italiced_text = md.StylisedText('some italiced text', {'italic'})
    strikethrough_text = md.StylisedText('striken text', {'strikethrough'})
    all_together = md.StylisedText('All styles combined',
                                   {'bold', 'italic', 'strikethrough'})

    doc += bold_text
    doc += italiced_text
    doc += strikethrough_text
    doc += all_together
    doc += examples['stylised']
    doc += md.HRule()

    #%%  paragraph
    paragraph = md.Paragraph(['Example paragraph containing ',
                              md.StylisedText('bolded text', {'bold'})])

    doc += get_example('paragraph', paragraph)

    #%% table
    table = md.Table(['First column', 'Second column', 'third column'],
                     ['right', 'left', 'center'],
                     [['a', 1, 'Python'],
                      ['b', 2, 'Markdown']])

    doc += get_example('table', table)

    #%% listing
    listing = md.Listing('unordered', 
                         ['Just normal text',
                          md.StylisedText('some stylised text', {'italic'}),
                          ('Sublist by using a tuple',
                            md.Listing('ordered',
                                      ['first', 'second']))])

    doc += get_example('listing', listing)

    #%% codeblock

    #%% Link


    #%% Image

    return doc

if __name__ == '__main__':
    main()
```



[1]: <https://pypi.org/project/yamdog> ""
[2]: <https://pypi.org/project/yamdog> ""
[3]: <https://pypi.org/project/yamdog> ""
[4]: <https://pypi.org/project/yamdog> ""