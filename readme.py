import yamdog as yg
import pathlib

link1 = yg.Link('hobbit-hole',
                'https://en.wikipedia.org/wiki/Hobbit#Lifestyle',
                'Hobbit lifestyles')
link2 = yg.Link('YAMDOG PyPI site',
                'https://pypi.org/project/yamdog/',
                'PyPI page for YAMDOG')
link3 = yg.Link(yg.InlineMath('\leq'),'https://www.markdownguide.org/' )
doc = yg.Document()
doc += yg.Heading(1, 'YAMDOG', False)
doc += 'Yet Another Markdown Only Generator'
doc += yg.Heading(2, 'Examples')
# doc += yg.Paragraph(['hmmm ', link1,' maybe'])

table = yg.QuoteBlock(yg.Table(['a', 'b', yg.InlineMath('\leq')],
                               ['left', 'center', 'right'],
                               [[1,2,link3],
                                [3,link2,5],
                                [7,link1,9]]))

listing = yg.Listing('ordered',
                     ['Just text',
                      ('Unordered sublist',
                       yg.Listing('unordered', ['thing', 'other thing'])),
                      table,
                      ('second sublisting, definition', 
                        yg.Listing('definition', ['First definition', 'Second definition'])),
                     yg.StylisedText(link1, {'bold', 'italic'})])

doc += listing

doc += yg.Paragraph(['Hmm',
                     yg.Footnote(yg.Paragraph(['Link in footnotes?',
                                               link1]))])



doc.to_file(pathlib.Path(__file__).parent / 'README.md')