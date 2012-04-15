#! /usr/local/bin/python
#-*- coding: utf-8 -*-

import epub
from genshi.template import TemplateLoader

class Section:
    def __init__(self):
        self.title = ''
        self.paragraphs = []
        self.tocDepth = 1

def makeBook(title, authors, sections, outputDir, lang='en-US', cover=None):
    book = epub.EpubBook()
    book.setLang(lang)
    book.setTitle(title)
    for author in authors:
        book.addCreator(author)
    #book.addTitlePage()
    #book.addTocPage()
    #if cover:
        #book.addCover(cover)

    loader = TemplateLoader('./epub/templates')
    tmpl = loader.load('ez-section.html')

    for i, section in enumerate(sections):
        stream = tmpl.generate(section = section)
        html = stream.render('xhtml', doctype='xhtml11', drop_xml_decl=False)
        item = book.addHtml('', 's%d.html' % (i + 1), html)
        book.addSpineItem(item)
        book.addTocMapNode(item.destPath, section.title, section.tocDepth)

    outputFile = outputDir + 'article.epub'
    book.createBook(outputDir)
    book.createArchive(outputDir, outputFile)