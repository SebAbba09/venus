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

    def test_parser_excludes_form_controls_but_keeps_documentary_choices(self):
        html = """
        <main>
          <h2>Processus de préinscription</h2>
          <form>
            <h3>Documents à fournir</h3>
            <select id="pays-v"><option>Sél. Pays</option><option>Sénégal</option></select>
            <select id="formation"><option>Sél. Formation</option><option>Licence Informatique (Bac+3)</option></select>
            <p>Licence Informatique (Bac+3)</p>
            <div class="custom-file">
              <input type="file">
              <label>Cliquer pour ajouter</label>
            </div>
            <div class="custom-control"><label>J'en ai 2</label></div>
          </form>
        </main>
        """

        parser = ESTMHTMLParser()
        parser.feed(html)
        parser.close()
        text = parser.get_text()

        self.assertIn("Processus de préinscription", text)
        self.assertIn("Documents à fournir", text)
        self.assertIn("Licence Informatique (Bac+3)", text)
        self.assertNotIn("Sél. Pays", text)
        self.assertNotIn("Sénégal", text)
        self.assertNotIn("Sél. Formation", text)
        self.assertNotIn("Cliquer pour ajouter", text)
        self.assertNotIn("J'en ai 2", text)

    def test_parser_keeps_contact_details_but_excludes_form_and_map(self):
        html = """
        <main>
          <h3>Formulaire de contact</h3>
          <form><input><textarea>Carte en cours de chargement...</textarea></form>
          <div class="contact">Dakar, avenue Cheikh Anta DIOP</div>
          <div class="contact">estm@estm.edu.sn</div>
          <div class="contact">+221 33 825 28 89</div>
          <div class="map-container"><div id="map">Carte en cours de chargement...</div></div>
        </main>
        """

        parser = ESTMHTMLParser()
        parser.feed(html)
        parser.close()
        text = parser.get_text()

        self.assertIn("Dakar, avenue Cheikh Anta DIOP", text)
        self.assertIn("estm@estm.edu.sn", text)
        self.assertIn("+221 33 825 28 89", text)
        self.assertNotIn("Formulaire de contact", text)
        self.assertNotIn("Carte en cours de chargement", text)
