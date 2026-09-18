import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from collect_estm_corpus import ESTMHTMLParser


class ESTMHTMLParserTests(unittest.TestCase):
    def test_parser_keeps_document_content_and_excludes_interface_structure(self):
        html = """
        <html>
          <head><title>Page ESTM</title><style>.x { color: red; }</style></head>
          <body>
            <nav><a href="/">Accueil</a><a href="/formations">Nos formations</a></nav>
            <div class="breadcrumb-estm">Accueil / Formation</div>
            <main>
              <ul class="nav"><li>Onglet technique</li></ul>
              <h1>Formation initiale</h1>
              <p>Cette formation développe des compétences utiles.</p>
              <div class="card">
                <h2>Master Informatique</h2>
                <span class="large-screen">Survoler pour voir plus</span>
                <div class="mask"><a class="text-estm">Cliquez ici</a></div>
              </div>
              <p>Durée : 2 ans.</p>
            </main>
            <div class="modal" id="brochure-modal">Formulaire de téléchargement</div>
            <footer>Mentions légales</footer>
          </body>
        </html>
        """

        parser = ESTMHTMLParser()
        parser.feed(html)
        parser.close()
        text = parser.get_text()

        self.assertIn("Formation initiale", text)
        self.assertIn("Cette formation développe des compétences utiles.", text)
        self.assertIn("Master Informatique", text)
        self.assertIn("Durée : 2 ans.", text)
        self.assertNotIn("Accueil", text)
        self.assertNotIn("Onglet technique", text)
        self.assertNotIn("Survoler pour voir plus", text)
        self.assertNotIn("Cliquez ici", text)
        self.assertNotIn("Formulaire de téléchargement", text)
        self.assertNotIn("Mentions légales", text)
        self.assertNotIn("color: red", text)
