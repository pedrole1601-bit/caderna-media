"""Tests for constructing official Commons resize URLs without changing source provenance."""
import ast
import unittest
from pathlib import Path
from urllib.parse import urlparse

source=(Path(__file__).resolve().parents[1]/"scripts/render_editorial.py").read_text(encoding="utf8")
module=ast.parse(source)
node=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=="commons_derivatives")
namespace={"urlparse":urlparse}
exec(compile(ast.Module(body=[node],type_ignores=[]),"<commons_derivatives>","exec"),namespace)
derive=namespace["commons_derivatives"]

class CommonsDerivativesTests(unittest.TestCase):
    def test_valid_jpeg_has_resized_fallback(self):
        url="https://upload.wikimedia.org/wikipedia/commons/6/69/Prefeitura-Natal.jpg"
        choices=derive(url)
        self.assertEqual(choices[0],"https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Prefeitura-Natal.jpg/1600px-Prefeitura-Natal.jpg")
        self.assertEqual(choices[1],"https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Prefeitura-Natal.jpg/1280px-Prefeitura-Natal.jpg")
        self.assertEqual(choices[-1],url)
    def test_no_external_photo_origin_is_fabricated(self):
        url="https://example.org/photo.jpg"
        self.assertEqual(derive(url),[url])
    def test_existing_thumbnail_is_not_double_wrapped(self):
        url="https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Prefeitura-Natal.jpg/1600px-Prefeitura-Natal.jpg"
        self.assertEqual(derive(url),[url])
if __name__=="__main__":
    unittest.main()
