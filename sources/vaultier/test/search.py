from django.test.testcases import TransactionTestCase
from django.utils import unittest
from django.utils.unittest.suite import TestSuite
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_200_OK, HTTP_204_NO_CONTENT
from vaultier.models.fields import SecretTypeField
from vaultier.test.auth_tools import auth_api_call, register_api_call
from vaultier.test.card_tools import create_card_api_call, list_cards_api_call, retrieve_card_api_call
from vaultier.test.search_tools import search_api_call
from vaultier.test.secret_tools import create_secret_api_call, delete_secret_api_call, list_secrets_api_call, retrieve_secret_api_call
from vaultier.test.tools import format_response
from vaultier.test.vault_tools import create_vault_api_call, delete_vault_api_call, list_vaults_api_call, retrieve_vault_api_call
from vaultier.test.workspace_tools import create_workspace_api_call, delete_workspace_api_call


class ApiSearchTest(TransactionTestCase):


    def test_010_search_vault_case_insensitive(self):

        # create user
        email = 'jan@rclick.cz'
        register_api_call(email=email, nickname='Misan').data
        user1token = auth_api_call(email=email).data.get('token')

        # create workspace
        workspace = create_workspace_api_call(user1token, name='Workspace').data

        #create vault
        vault = create_vault_api_call(user1token, name="this is vault", workspace=workspace.get('id')).data

        response = search_api_call(user1token, query='VaUlT')

        # should be ok
        self.assertEqual(
            response.status_code,
            HTTP_200_OK,
            format_response(response)
        )

        # one vault should be returned
        self.assertEqual(
            len(response.data.get('vaults')),
            1,
            format_response(response)
        )

    def test_020_search_vault_permissions(self):

        # create user
        email = 'jan@rclick.cz'
        register_api_call(email=email, nickname='Misan').data
        user1token = auth_api_call(email=email).data.get('token')

        # create user2
        email = 'marcel@rclick.cz'
        register_api_call(email=email, nickname='Marcel').data
        user2token = auth_api_call(email=email).data.get('token')

        # create workspace
        workspace1 = create_workspace_api_call(user1token, name='Workspace').data

        #create vault
        vault1 = create_vault_api_call(user1token, name="this is vault 1", workspace=workspace1.get('id')).data

        # create workspace
        workspace2 = create_workspace_api_call(user2token, name='Workspace').data

        #create vault
        vault2 = create_vault_api_call(user2token, name="this is vault 2", workspace=workspace2.get('id')).data

        response = search_api_call(user1token, query='VaUlT')
        # one vault should be returned
        self.assertEqual(
            response.data.get('vaults')[0].get('name'),
            'this is vault 1',
            format_response(response)
        )

        response = search_api_call(user2token, query='VaUlT')
        # one vault should be returned
        self.assertEqual(
            response.data.get('vaults')[0].get('name'),
            'this is vault 2',
            format_response(response)
        )

    def test_030_search_card_case_insensitive(self):

        # create user
        email = 'jan@rclick.cz'
        register_api_call(email=email, nickname='Misan').data
        user1token = auth_api_call(email=email).data.get('token')

        # create workspace
        workspace = create_workspace_api_call(user1token, name='Workspace').data

        #create vault
        vault = create_vault_api_call(user1token, name="this is vault", workspace=workspace.get('id')).data

        #create card
        card = create_card_api_call(user1token, name="this is card", vault=vault.get('id')).data

        response = search_api_call(user1token, query='ThIs')

        # should be ok
        self.assertEqual(
            response.status_code,
            HTTP_200_OK,
            format_response(response)
        )

        # one vault should be returned
        self.assertEqual(
            len(response.data.get('vaults')),
            1,
            format_response(response)
        )

        # one card should be returned
        self.assertEqual(
            len(response.data.get('cards')),
            1,
            format_response(response)
        )

    def test_040_search_card_permissions(self):

        # create user
        email = 'jan@rclick.cz'
        register_api_call(email=email, nickname='Misan').data
        user1token = auth_api_call(email=email).data.get('token')

        # create user2
        email = 'marcel@rclick.cz'
        register_api_call(email=email, nickname='Marcel').data
        user2token = auth_api_call(email=email).data.get('token')

        # create workspace
        workspace1 = create_workspace_api_call(user1token, name='Workspace').data

        #create vault
        vault1 = create_vault_api_call(user1token, name="this is vault 1", workspace=workspace1.get('id')).data

        #create card
        card1 = create_card_api_call(user1token, name="this is card 1", vault=vault1.get('id')).data

        # create workspace
        workspace2 = create_workspace_api_call(user2token, name='Workspace').data

        #create vault
        vault2 = create_vault_api_call(user2token, name="this is vault 2", workspace=workspace2.get('id')).data

        #create card
        card2 = create_card_api_call(user2token, name="this is card 2", vault=vault2.get('id')).data

        response = search_api_call(user1token, query='card')
        # one vault should be returned
        self.assertEqual(
            response.data.get('cards')[0].get('name'),
            'this is card 1',
            format_response(response)
        )

        response = search_api_call(user2token, query='card')
        # one vault should be returned
        self.assertEqual(
            response.data.get('cards')[0].get('name'),
            'this is card 2',
            format_response(response)
        )



def search_suite():
    suite = TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(ApiSearchTest))
    return suite