[![PyPI Package latest release](https://img.shields.io/pypi/v/yamdog.svg)][1]
[![PyPI Wheel](https://img.shields.io/pypi/wheel/yamdog.svg)][1]
[![Supported versions](https://img.shields.io/pypi/pyversions/yamdog.svg)][1]
[![Supported implementations](https://img.shields.io/pypi/implementation/yamdog.svg)][1]

# YAMDOG <!-- omit in toc -->

YAMDOG is toolkit for creating Markdown text using Python. Markdown is a light and relatively simple markup language.

## Table of Contents <!-- omit in toc -->

- [Quick start guide](#quick-start-guide)
    - [The first steps](#the-first-steps)
        - [Installing](#installing)
        - [Importing](#importing)
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
            - [Example heading](#example-heading-1)
- [Further reading](#further-reading)

# Quick start guide

Here's how you can start

## The first steps

### Installing

Install YAMDOG with pip

```
pip install yamdog
```

### Importing

Import name is the same as install name, `yamdog`.

```python
import yamdog
```

## Using the package

There are two main things to building a Markdown document using YAMDOG

1. Making elements
2. Combining elements into a document

You can call `str` on the element directly to get the markdown source

```python
markdown_source = str(element)
```

but most of the time you will compose the elements together into a document

```python
markdown_source = str(document)
```

### Making elements

Let's start with an empty document

```python
document = md.Document([])
```

#### Heading

*Python source*

```python
heading = md.Heading('Example heading', 4)
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

~~==***All styles combined***==~~

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
table = md.Table([['a', 1, 'Python'],
                  ['b', 2, 'Markdown']],
                 ['First column', 'Second column', 'Third column'],
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
table = md.Table([['a', 1, 'Python'],
                  ['b', 2, 'Markdown']],
                 ['First column', 'Second column', 'Third column'],
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
listing = md.Listing(['Just normal text',
                      md.Text('some stylised text', {md.ITALIC}),
                      md.Checkbox('Listings can include checkboxes', False),
                      md.Checkbox('Checked and unchecked option available', True),
                      ('Sublist by using a tuple',
                        md.Listing(['first', 'second'], md.ORDERED))],
                      md.UNORDERED)
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
checklist = md.make_checklist([('unchecked box', False),
                               ('checked box', True),
                               ('done', True)])
```

*Markdown source*

```markdown
- [ ] unchecked box
- [x] checked box
- [x] done
```

*Rendered result*

- [ ] unchecked box
- [x] checked box
- [x] done

---

#### Link

*Python source*

```python
link = md.Link('https://www.markdownguide.org', 'Link to Markdown Guide')
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
codeblock = md.CodeBlock('import yamdog as md\n\ndoc = md.Document([])',
                         'python')
```

*Markdown source*

````markdown
```python
import yamdog as md

doc = md.Document([])
```
````

*Rendered result*

```python
import yamdog as md

doc = md.Document([])
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
address = md.Link('https://www.markdownguide.org')
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
quoteblock = md.Quote('Quote block supports\nmultiple lines')
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
document = md.Document([])
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

# Further reading

- [basic syntax guide][2]
- [extended syntax guide][2]

# Changelog <!-- omit in toc -->

## 0.6.0 2024-07-16 <!-- omit in toc -->

##  Deprecations <!-- omit in toc -->

- python 3.9

## Features <!-- omit in toc -->

- support for pythonn 3.13

## 0.5.0 2023-05-07 <!-- omit in toc -->

- Some API changes
- Added Raw, PDF, Comment

## 0.4.0 2023-01-23 <!-- omit in toc -->

- Much better type validation
- Some comparisons

## 0.3.1 2023-01-23 <!-- omit in toc -->

- Preliminary type validation
- Full test coverage

[1]: <https://pypi.org/project/yamdog> "Project PyPI page"
[2]: <https://www.markdownguide.org/basic-syntax/> ""
