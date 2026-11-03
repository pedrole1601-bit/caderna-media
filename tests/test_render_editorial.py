import unittest,importlib.util,copy,tempfile
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('editorial',root/'scripts/render_editorial.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def example(kind='carousel'):
    return {'id':'2026-11-03-enem-carrossel-demo','kind':kind,'theme':'ink','risk':'low',
      'section':'EDUCAÇÃO','headline':'Enem 2026 começa neste domingo',
      'deck':'O local de prova pode ser consultado no Cartão de Confirmação, segundo o Inep.',
      'sources':['https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/enem/enem-2026-participantes-ja-podem-conferir-os-locais-de-prova/','https://agenciabrasil.ebc.com.br/educacao/noticia/2026-11/menos-de-uma-semana-para-o-enem-2026-mec-da-dicas-aos-participantes'],
      'source_label':'INEP / AGENCIA BRASIL','caption':'O Enem 2026 terá a primeira prova em 8 de novembro. O local de aplicação deve ser consultado pelo candidato na Página do Participante. Os portões abrem às 12h e fecham às 13h. Fontes: Inep e Agência Brasil, outubro e novembro de 2026.',
      'slides':[
         {'title':'Quando são as provas','body':'A primeira prova ocorre em 8 de novembro, com Linguagens, Ciências Humanas e Redação. O segundo dia, em 15 de novembro, terá Matemática e Ciências da Natureza.'},
         {'title':'Onde consultar o local','body':'O Cartão de Confirmação está disponível na Página do Participante, com login gov.br. O Inep recomenda levá-lo aos dois domingos, mas ele não é obrigatório.'},
         {'title':'Horários para se organizar','body':'Os portões abrem ao meio-dia e fecham às 13h, sempre pelo horário de Brasília. A aplicação começa às 13h30. O documento oficial com foto é obrigatório.'}
      ]}
class RenderTests(unittest.TestCase):
    def test_both_themes_and_headline(self):
        for theme in ('cream','ink'):
            a=example('headline');a['theme']=theme
            with tempfile.TemporaryDirectory() as t:
                q=module.render(a,Path(t))
                self.assertEqual(q['jpeg_count'],1)
                with Image.open(Path(t)/(a['id']+'-01.jpg')) as im:self.assertEqual(im.size,(1080,1350))
    def test_carousel_four_slides(self):
        with tempfile.TemporaryDirectory() as t:
            q=module.render(example(),Path(t))
            self.assertEqual(q['jpeg_count'],4)
            self.assertEqual(len(q['qa']),4)
    def test_risk_flag_blocks_sensitive(self):
        a=example();a['risk']='high'
        with self.assertRaises(ValueError):module.assert_story(a)
    def test_sensitive_keyword_blocks_even_if_mislabeled(self):
        a=example();a['headline']='A eleição presidencial termina neste domingo'
        with self.assertRaises(ValueError):module.assert_story(a)
    def test_one_source_is_not_research(self):
        a=example();a['sources']=[a['sources'][0]]
        with self.assertRaises(ValueError):module.assert_story(a)
    def test_oversized_copy_is_rejected(self):
        a=example();a['slides'][0]['body']='contexto sem evidência '*30
        with self.assertRaises(ValueError):module.assert_story(a)
if __name__=='__main__':unittest.main()
