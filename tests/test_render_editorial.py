import unittest,importlib.util,copy,tempfile
from unittest.mock import patch
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
      'source_label':'INEP / AGENCIA BRASIL',
      'photo':{
       'image_url':'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Datacenter_Server_Racks_%2822370909788%29.jpg/1280px-Datacenter_Server_Racks_%2822370909788%29.jpg',
       'source_page':'https://commons.wikimedia.org/wiki/File:Datacenter_Server_Racks_(22370909788).jpg',
       'author':'Carl Lender','credit':'Carl Lender / Wikimedia Commons',
       'license':'CC BY 2.0','license_url':'https://creativecommons.org/licenses/by/2.0/',
       'description':'Fotografia real de um data center usada apenas como fixture para testes de layout',
       'context':'archive_illustrative',
       'context_note':'Imagem de arquivo; não representa equipamentos ou acontecimentos documentados nesta pauta.',
       'date_taken':'2015-11-04'},
      'caption':'O Enem 2026 terá a primeira prova em 8 de novembro. O local de aplicação deve ser consultado pelo candidato na Página do Participante. Os portões abrem às 12h e fecham às 13h. Fontes: Inep e Agência Brasil, outubro e novembro de 2026.',
      'slides':[
         {'title':'Quando são as provas','body':'A primeira prova ocorre em 8 de novembro, com Linguagens, Ciências Humanas e Redação. O segundo dia, em 15 de novembro, terá Matemática e Ciências da Natureza.'},
         {'title':'Onde consultar o local','body':'O Cartão de Confirmação está disponível na Página do Participante, com login gov.br. O Inep recomenda levá-lo aos dois domingos, mas ele não é obrigatório.'},
         {'title':'Horários para se organizar','body':'Os portões abrem ao meio-dia e fecham às 13h, sempre pelo horário de Brasília. A aplicação começa às 13h30. O documento oficial com foto é obrigatório.'}
      ]}
def render_fixture(story,out):
    # A simulated bitmap is allowed only in isolated unit tests; never in production.
    photograph=Image.new('RGB',(1600,900),'#42556A')
    with patch.object(module,'acquire_photo',return_value=(photograph,'0'*64)):
        return module.render(story,out)
class RenderTests(unittest.TestCase):
    def test_both_themes_and_headline(self):
        for theme in ('cream','ink'):
            a=example('headline');a['theme']=theme
            with tempfile.TemporaryDirectory() as t:
                q=render_fixture(a,Path(t))
                self.assertEqual(q['jpeg_count'],1)
                with Image.open(Path(t)/(a['id']+'-01.jpg')) as im:self.assertEqual(im.size,(1080,1350))
    def test_three_line_headline_fits_editorial_grid(self):
        a=example('headline')
        a['headline']='BULL E SCHWARZ DIGITS FIRMAM ACORDO PARA IA EUROPEIA'
        with tempfile.TemporaryDirectory() as t:
            result=render_fixture(a,Path(t))
            self.assertEqual(len(result['qa'][0]['headline_lines']),3)
            self.assertEqual(result['jpeg_count'],1)
    def test_photo_must_be_real_and_provenanced(self):
        a=example('headline');del a['photo']
        with self.assertRaisesRegex(ValueError,'REAL_PHOTO_REQUIRED'):
            module.assert_story(a)
    def test_photo_license_without_proof_rejected(self):
        a=example('headline');a['photo']['license']='ALL RIGHTS RESERVED'
        with self.assertRaisesRegex(ValueError,'PHOTO_LICENSE_NOT_VERIFIED'):
            module.assert_story(a)
    def test_photo_from_unknown_image_host_rejected(self):
        a=example('headline');a['photo']['image_url']='https://example.com/fake.jpg'
        with self.assertRaisesRegex(ValueError,'PHOTO_ORIGIN_UNVERIFIED'):
            module.assert_story(a)
    def test_photo_dominates_cover(self):
        a=example('headline')
        with tempfile.TemporaryDirectory() as t:
            qa=render_fixture(a,Path(t))
            self.assertGreater(qa['qa'][0]['photograph_fraction'],0.55)
            self.assertEqual(qa['photograph']['sha256'],'0'*64)
    def test_carousel_four_slides(self):
        with tempfile.TemporaryDirectory() as t:
            q=render_fixture(example(),Path(t))
            self.assertEqual(q['jpeg_count'],4)
            self.assertEqual(len(q['qa']),4)
    def high_brief(self):
        a=example()
        a['risk']='high'
        a['topic']='politica'
        a['sources'].append('https://www.reuters.com/world/')
        a['editorial_process']='source-anchored-triple-review'
        a['claim_status']='verified'
        a['disputed_claims']=[]
        a['review_checks']={
            'claims_checked':True,'contradictions_checked':True,
            'attribution_checked':True,'editorial_neutrality_checked':True,
            'primary_source_checked':True}
        a['verification_log']=[
            {'source_url':u,'source_excerpt':'Trecho documental específico, registrado e conferido'}
            for u in a['sources']]
        return a
    def test_high_risk_missing_research_is_blocked(self):
        a=example();a['risk']='high'
        with self.assertRaises(ValueError):module.assert_story(a)
    def test_high_risk_verified_story_can_render(self):
        a=self.high_brief()
        with tempfile.TemporaryDirectory() as t:
            q=render_fixture(a,Path(t))
            self.assertEqual(q['jpeg_count'],4)
            self.assertEqual(q['risk'],'high')
    def test_high_risk_missing_third_quote_blocks(self):
        a=self.high_brief();a['verification_log']=a['verification_log'][:2]
        with self.assertRaises(ValueError):module.assert_story(a)
    def test_high_risk_disputed_claim_blocks(self):
        a=self.high_brief();a['disputed_claims']=['Número de pessoas afetadas diverge nas fontes']
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
