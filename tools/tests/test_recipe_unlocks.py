"""Recipe-book discovery regressions; all generated files stay in temporary directories."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('bugslife_generator', ROOT / 'tools/gen_resources.py')
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class RecipeDiscoveryTests(unittest.TestCase):
    def test_every_shipped_recipe_has_matching_discovery_and_generation_preserves_inputs(self):
        with tempfile.TemporaryDirectory(prefix='bugslife-recipe-test-') as temporary:
            data = Path(temporary)
            shutil.copytree(ROOT / 'src/main/resources/data/bugslife/recipe', data / 'recipe')
            recipes = sorted((data / 'recipe').glob('*.json'))
            self.assertEqual(32, len(recipes), 'Review recipe discovery coverage when adding/removing recipes')
            hashes = {p.name: hashlib.sha256(p.read_bytes()).digest() for p in recipes}
            unrelated = data / 'advancement/untouched.json'
            unrelated.parent.mkdir()
            unrelated.write_text('{"sentinel": true}')
            with patch.object(generator, 'D', str(data)):
                generator.recipe_unlocks()
                generator.recipe_unlocks()
            self.assertEqual(hashes, {p.name: hashlib.sha256(p.read_bytes()).digest() for p in recipes})
            self.assertEqual('{"sentinel": true}', unrelated.read_text())
            generated = list((data / 'advancement/recipes').rglob('*.json'))
            self.assertEqual(len(recipes), len(generated))
            for recipe in recipes:
                with self.subTest(recipe=recipe.name):
                    original = json.loads(recipe.read_text())
                    category = original.get('category', 'misc')
                    result = json.loads((data / f'advancement/recipes/{category}/{recipe.name}').read_text())
                    recipe_id = 'bugslife:' + recipe.stem
                    self.assertEqual([recipe_id], result['rewards']['recipes'])
                    self.assertEqual(recipe_id, result['criteria']['has_the_recipe']['conditions']['recipe'])
                    self.assertEqual([list(result['criteria'])], result['requirements'], 'Discovery uses OR, not every ingredient at once')
                    discovery = [value for name, value in result['criteria'].items() if name != 'has_the_recipe']
                    self.assertTrue(discovery)
                    self.assertTrue(all(value['trigger'] == 'minecraft:inventory_changed' for value in discovery))
                    self.assertTrue(all(isinstance(value['conditions']['items'][0]['items'], str) for value in discovery))

    def test_component_ingredient_discovers_by_base_item_without_altering_crafting(self):
        with tempfile.TemporaryDirectory(prefix='bugslife-component-recipe-') as temporary:
            data = Path(temporary)
            (data / 'recipe').mkdir()
            recipe = {'type': 'minecraft:crafting_shapeless', 'category': 'misc', 'ingredients': [
                {'type': 'neoforge:components', 'items': 'bugslife:bug_jar', 'components': {'bugslife:bug': {'species': 'firefly'}}},
                {'tag': 'minecraft:logs'}], 'result': {'id': 'bugslife:firefly_lantern'}}
            source = data / 'recipe/lantern.json'
            source.write_text(json.dumps(recipe))
            before = source.read_bytes()
            with patch.object(generator, 'D', str(data)):
                generator.recipe_unlocks()
            result = json.loads((data / 'advancement/recipes/misc/lantern.json').read_text())
            selectors = {value['conditions']['items'][0]['items'] for name, value in result['criteria'].items() if name != 'has_the_recipe'}
            self.assertEqual({'bugslife:bug_jar', '#minecraft:logs'}, selectors)
            self.assertEqual(before, source.read_bytes())

    def test_unsupported_ingredient_is_rejected_before_writing_advancement(self):
        with tempfile.TemporaryDirectory(prefix='bugslife-invalid-recipe-') as temporary:
            data = Path(temporary)
            (data / 'recipe').mkdir()
            (data / 'recipe/invalid.json').write_text(json.dumps({'ingredients': [{'unknown': 'x'}]}))
            with patch.object(generator, 'D', str(data)):
                with self.assertRaises(ValueError):
                    generator.recipe_unlocks()
            self.assertFalse((data / 'advancement').exists())


if __name__ == '__main__':
    unittest.main()
