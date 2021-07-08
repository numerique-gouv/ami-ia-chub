import sys, os
sys.path.append(os.path.abspath('..'))
import unittest
import fhirclient.models.encounter as fhir_encounter_mod
import requests
from datetime import datetime
from pprint import pprint

from .utils_test import datetime_fromisoformat
from src import web


class EncounterTest(unittest.TestCase):

    def setUp(self):
        self.app = None
        self.docker_adress = os.environ.get('TEST_DOCKER_ADRESS', None)
        if self.docker_adress is None:
            self.app = web.app.test_client()
        self.verbose = os.environ.get('TEST_VERBOSE', False)

    def _get_route(self, api_path):
        if self.docker_adress is not None:
            res = requests.get(f'http://{self.docker_adress}{api_path}')
            res.json = res.json()
            return res
        else:
            return self.app.get(api_path)

    def test_ressource_ok(self):
        # When
        encounter_num = 22
        response = self._get_route(f'/encounters/{encounter_num}')
        self.assertEqual(200, response.status_code)
        self._check_ressource(response.json, encounter_num=encounter_num)

        patient_id = 2
        response = self._get_route(f'/patients/{patient_id}/encounters')
        self.assertEqual(200, response.status_code)
        [self._check_ressource(e, patient_id=patient_id) for e in response.json]

    def _check_ressource(self, json_result, encounter_num=None, patient_id=None):
        # Then
        if self.verbose:
            pprint(json_result)

        self.assertIsInstance(json_result, dict)

        fhir_encounter_mod.Encounter(jsondict=json_result)

        self.assertEqual('Encounter', json_result['resourceType'])
        if encounter_num is not None:
            self.assertEqual(str(encounter_num), json_result['id'])
        self.assertIn('identifier', json_result)
        for ident in json_result['identifier']:
            self.assertIn('system', ident)
            self.assertIn('value', ident)

        self.assertIn('status', json_result)
        self.assertIn('period', json_result)
        self.assertIn('start', json_result['period'])
        self.assertIsInstance(datetime_fromisoformat(json_result['period']['start']), datetime)
        self.assertIn('end', json_result['period'])
        self.assertIsInstance(datetime_fromisoformat(json_result['period']['end']), datetime)

        self.assertIn('type', json_result)
        self.assertIsInstance(json_result['type'], list)
        [self.assertIn('text', l) for l in json_result['type']]

        self.assertIn('subject', json_result)
        self.assertIn('reference', json_result['subject'])
        self.assertEqual('Patient/', json_result['subject']['reference'][:len('Patient/')])
        if patient_id is not None:
            self.assertEqual(str(patient_id), json_result['subject']['reference'][len('Patient/'):])

        self.assertIn('location', json_result)
        self.assertGreaterEqual(len(json_result['location']), 1)
        for location in json_result['location']:
            self.assertIn('location', location)
            self.assertIn('display', location['location'])
            self.assertIn('period', location)
            self.assertIn('start', location['period'])
            self.assertIsInstance(datetime_fromisoformat(location['period']['start']), datetime)
            self.assertIn('end', location['period'])
            self.assertIsInstance(datetime_fromisoformat(location['period']['end']), datetime)

    def test_ressource_failure(self):
        # When
        response = self._get_route(f'/encounters/test')
        self.assertEqual(404, response.status_code)

        response = self._get_route(f'/encounters/')
        self.assertEqual(404, response.status_code)

        response = self._get_route(f'/patients/test/encounters')
        self.assertEqual(404, response.status_code)

        response = self._get_route(f'/patients//encounters')
        self.assertEqual(404, response.status_code)

    # def tearDown(self):
    #     pass