from django.test.testcases import TransactionTestCase
from django.utils import unittest
from django.utils.unittest.suite import TestSuite
from vaultier.models.card.model import Card
from vaultier.test.auth_tools import auth_api_call, register_api_call
from vaultier.test.tools.card_api_tools import create_card_api_call, delete_card_api_call
from vaultier.test.case.workspace.workspace_tools import create_workspace_api_call, delete_workspace_api_call
from vaultier.test.tools.vault_api_tools import create_vault_api_call, delete_vault_api_call


class CardSoftDeleteTest(TransactionTestCase):

      def test_010_softdelete(self):

        # create user
        email = 'jan@rclick.cz'
        register_api_call(email=email, nickname='Misan').data
        user1token = auth_api_call(email=email).data.get('token')

        # create workspace
        workspace = create_workspace_api_call(user1token, name='workspace').data

        #create vault
        vault = create_vault_api_call(user1token,
                                      name="vault_in_workspace",
                                      workspace=workspace.get('id')
        ).data

        #create card
        card = create_card_api_call(user1token,
                                      name="card_in_workspace",
                                      vault=vault.get('id')
        ).data

        delete_card_api_call(user1token, card.get('id'))

        cards =Card.objects.filter(id=card.get('id'))
        self.assertEquals(cards.count(), 0 )

        cards =Card.objects.include_deleted().filter(id=card.get('id'))
        self.assertEquals(cards.count(), 1 )

      def test_020_softdelete_vault(self):

        # create user
        email = 'jan@rclick.cz'
        register_api_call(email=email, nickname='Misan').data
        user1token = auth_api_call(email=email).data.get('token')

        # create workspace
        workspace = create_workspace_api_call(user1token, name='workspace').data

        #create vault
        vault = create_vault_api_call(user1token,
                                      name="vault_in_workspace",
                                      workspace=workspace.get('id')
        ).data

        #create card
        card = create_card_api_call(user1token,
                                      name="card_in_workspace",
                                      vault=vault.get('id')
        ).data

        delete_vault_api_call(user1token, vault.get('id'))

        cards =Card.objects.filter(id=card.get('id'))
        self.assertEquals(cards.count(), 0 )

        cards =Card.objects.include_deleted().filter(id=card.get('id'))
        self.assertEquals(cards.count(), 1 )

      def test_020_softdelete_workspace(self):

        # create user
        email = 'jan@rclick.cz'
        register_api_call(email=email, nickname='Misan').data
        user1token = auth_api_call(email=email).data.get('token')

        # create workspace
        workspace = create_workspace_api_call(user1token, name='workspace').data

        #create vault
        vault = create_vault_api_call(user1token,
                                      name="vault_in_workspace",
                                      workspace=workspace.get('id')
        ).data

        #create card
        card = create_card_api_call(user1token,
                                      name="card_in_workspace",
                                      vault=vault.get('id')
        ).data

        delete_workspace_api_call(user1token, vault.get('id'))

        cards =Card.objects.filter(id=card.get('id'))
        self.assertEquals(cards.count(), 0 )

        cards =Card.objects.include_deleted().filter(id=card.get('id'))
        self.assertEquals(cards.count(), 1 )


def card_softdelete_suite():
    suite = TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(CardSoftDeleteTest))
    return suite